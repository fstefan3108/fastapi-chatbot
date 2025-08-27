import os
import psutil
from typing import Dict, Tuple, List
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher, RateLimiter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter
from app.core.logger import logger
from app.services.crawler.sitemap_extract import SitemapExtractor
from app.utils.normalize_url import normalize_url

class WebCrawler:
    """
    A class for crawling web pages in parallel using Crawl4AI.
    max_concurrent -> Maximum number of sessions running at the same time.
    memory_threshold -> Memory threshold percentage (0-100)
    peak_memory -> Highest amount of memory used during the process
    """
    def __init__(self):
        self.peak_memory = 0
        self.process = psutil.Process(os.getpid()) # A way to monitor the current python process #
        self.sitemap_extractor = SitemapExtractor()

        # Run browser in headless mode #
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=False,
            extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"], # limits resource usage #
        )

        # Junk filter/remover (e.g. headers, footers, links, etc.) #
        self.prune_filter = PruningContentFilter(
            threshold=0.4,
            threshold_type="dynamic",
            min_word_threshold=5
        )

        # Setup markdown generator #
        self.fit_markdown_generator = DefaultMarkdownGenerator(
            content_source="cleaned_html",
            options={"ignore_links": True},
            content_filter=self.prune_filter
        )

        # Set up crawl configuration
        self.run_config = CrawlerRunConfig(
            excluded_tags=["nav", "footer", "header"],
            cache_mode=CacheMode.BYPASS,
            check_robots_txt=True, # Check if website permits scraping #
            stream=False,
            markdown_generator=self.fit_markdown_generator,
            page_timeout=20000,
        )

        # Limit request sending to the website domain to prevent blocking from the website #
        self.rate_limiter = RateLimiter(
            base_delay=(2.0, 4.0),  # Wait between 2-4 seconds #
            max_delay=30.0,  # Cap delay at 30 seconds #
            max_retries=5,  # Retry up to 5 times on rate-limiting errors #
            rate_limit_codes=[429, 503]  # Handle these HTTP status codes #
        )

        # Dispatcher that adapts how many sessions will run based on memory usage #
        self.dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=95.0,  # Pause crawling if memory exceeds this #
            check_interval=1.0,  # How often to check memory #
            max_session_permit=3,  # Maximum concurrent tasks #
            memory_wait_timeout=60, # Wait max 60s for memory to free up #
            rate_limiter=self.rate_limiter # Use the rate limiter #
        )

    def _log_memory(self, prefix: str = "") -> None:
        """
        Logs the current memory usage
        prefix -> for the log message
        """
        current_mem = self.process.memory_info().rss
        self.peak_memory = max(self.peak_memory, current_mem)

        current_mb = current_mem // (1024 * 1024)
        peak_mb = self.peak_memory // (1024 * 1024)
        logger.info(f"{prefix} Memory: {current_mb}MB (Peak: {peak_mb}MB)")

    async def crawl_sitemap(self, url: str) -> Tuple[str, List[str]]:
        """
        Crawls(scrapes) the list of provided URLs in parallel with timeout handling.
        urls -> List of URLs to scrape/crawl to
        returns dictionary with results
        """
        logger.info("=== Starting sitemap crawling ===")

        urls = await self.sitemap_extractor.get_urls_from_sitemap(url)
        if not urls:
            logger.info(f"No URLs found in sitemap for: {url}")
            return "Untitled", []

        logger.info(f"Crawling {len(urls)} URLs from sitemap")
        return await self._crawl_urls(urls, url.rstrip("/"))

    async def crawl_multipage(self, start_url: str, max_depth: int = 2) -> Tuple[str, List[str]]:
        """Recursively crawl website up to specified depth."""
        logger.info(f"=== Starting multi-page crawling (depth: {max_depth}) ===")

        base_url = str(start_url).rstrip("/")
        website_title = "Untitled"
        all_markdowns = []

        # Track visited URLs to prevent revisiting and infinite loops #
        visited = set()

        # Start with the initial URL #
        current_urls = {normalize_url(str(start_url))}

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for depth in range(max_depth):
                logger.info(f"\n=== Crawling Depth {depth + 1}/{max_depth} ===")

                # Filter out already visited URLs #
                urls_to_crawl = [url for url in current_urls if url not in visited]
                if not urls_to_crawl:
                    logger.info(f"No new URLs to crawl at depth {depth + 1}")
                    break

                logger.info(f"Crawling {len(urls_to_crawl)} URLs at depth {depth + 1}")

                # Batch-crawl all URLs at this depth in parallel
                results = await crawler.arun_many(
                    urls=urls_to_crawl,
                    config=self.run_config,
                    dispatcher=self.dispatcher
                 )

                next_level_urls = set()

                for result in results:
                    norm_url = normalize_url(result.url)
                    visited.add(norm_url)  # Mark as visited (no fragment) #

                    title, markdowns, stop = self._handle_crawl_result(result, base_url)
                    if title != "Untitled":
                        website_title = title
                    all_markdowns.extend(markdowns)

                    if stop:
                        logger.error("=== Sitemap crawling stopped due to timeout ===")
                        return "Untitled", []

                    # Collect all new internal links for the next depth #
                    if result.success and result.links:
                        internal_links = result.links.get("internal", [])
                        new_urls = [
                            normalize_url(link["href"])
                            for link in internal_links
                            if isinstance(link, dict) and "href" in link
                        ]
                        filtered_urls = self.sitemap_extractor.filter_urls_by_domain(new_urls, base_url)
                        next_level_urls.update(url for url in filtered_urls if url not in visited)

                # Move to the next set of URLs for the next recursion depth #
                current_urls = next_level_urls
                logger.info(f"Discovered {len(next_level_urls)} new URLs for next depth")

        logger.info("=== Recursive crawling completed ===")
        logger.info(f"Total URLs crawled: {len(visited)}")
        logger.info(f"Final website_title: {website_title}")
        logger.info(f"Final markdown count: {len(all_markdowns) if all_markdowns else 'None or empty'}")

        return website_title, all_markdowns

    def get_memory_usage(self) -> Dict[str, int]:
        """
        Get current memory usage
        returns memory usage in MB
        """
        current_mem = self.process.memory_info().rss
        return {
            'current_mb': current_mem // (1024 * 1024),
            'peak_mb': self.peak_memory // (1024 * 1024)
        }

    async def _crawl_urls(self, urls: List[str], base_url: str) -> Tuple[str, List[str]]:
        """Core crawling logic for a list of URLs."""
        website_title = "Untitled"
        all_markdowns = []

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            results = await crawler.arun_many(urls, config=self.run_config, dispatcher=self.dispatcher)

            for result in results:
                title, markdowns, should_stop = self._handle_crawl_result(result, base_url)

                if title != "Untitled":
                    website_title = title
                all_markdowns.extend(markdowns)

                if should_stop:
                    return "Untitled", []

        logger.info(f"Processed {len(results)} URLs, extracted {len(all_markdowns)} markdown documents")
        return website_title, all_markdowns

    def _handle_crawl_result(self, result, base_url: str):
        """Process a single crawl result."""
        if not result.success:
            return self._handle_error(result)

        try:
            # Extract markdown
            markdowns = []
            if (result.markdown and
                hasattr(result.markdown, 'fit_markdown') and
                result.markdown.fit_markdown and
                result.markdown.fit_markdown.strip()):

                markdowns.append(result.markdown.fit_markdown)
                logger.info(f"✓ Crawled: {result.url}")
                self._log_memory()

            # Extract title if this is the base URL
            title = "Untitled"
            if result.url.rstrip("/") == base_url:
                title = self._get_title(result)

            return title, markdowns, False

        except Exception as e:
            logger.error(f"Error processing {result.url}: {e}")
            return "Untitled", [], False

    @staticmethod
    def _handle_error(result) -> Tuple[str, List[str], bool]:
        """Handle crawl errors with appropriate logging."""
        error_msg = (result.error_message or "").lower()

        # Stop on timeout
        if "timeout" in error_msg or "timed out" in error_msg:
            logger.error(f"Timeout error for {result.url}")
            return "Untitled", [], True

        # Log other errors but continue
        error_types = {
            ("403", "forbidden"): "Access forbidden",
            ("404", "not found"): "Page not found",
            ("robots.txt",): "Blocked by robots.txt"
        }

        for patterns, msg_type in error_types.items():
            if any(pattern in error_msg for pattern in patterns):
                logger.warning(f"{msg_type}: {result.url}")
                return "Untitled", [], False

        logger.error(f"Failed to crawl {result.url}: {result.error_message}")
        return "Untitled", [], False

    @staticmethod
    def _get_title(result) -> str:
        try:
            html = result.html
            if not html:
                return "Untitled"

            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.find("title")

            if title_tag and title_tag.string:
                return title_tag.string.strip()
            return "Untitled"

        except Exception as e:
            logger.error(f"Error extracting title: {e}")
            return "Untitled"
