import os
import psutil
from typing import Dict
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
            base_delay=(2.0, 4.0),  # Random delay between 2-4 seconds
            max_delay=30.0,  # Cap delay at 30 seconds
            max_retries=5,  # Retry up to 5 times on rate-limiting errors
            rate_limit_codes=[429, 503]  # Handle these HTTP status codes
        )

        # Dispatcher that adapts how many sessions will run based on memory usage #
        self.dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=95.0,  # Pause crawling if memory exceeds this
            check_interval=1.0,  # How often to check memory
            max_session_permit=5,  # Maximum concurrent tasks
            memory_wait_timeout=60,
            rate_limiter=self.rate_limiter
        )

        self.sitemap_extractor = SitemapExtractor()

    def _log_memory(self, prefix: str = "") -> None:
        """
        Logs the current memory usage
        prefix -> for the log message
        """
        current_mem = self.process.memory_info().rss # in bytes #
        if current_mem > self.peak_memory:
            self.peak_memory = current_mem

        current_mb = current_mem // (1024 * 1024)
        peak_mb = self.peak_memory // (1024 * 1024)
        logger.info(f"{prefix} Current Memory: {current_mb} MB, Peak: {peak_mb} MB")

    async def crawl_sitemap(self, url: str):
        """
        Crawls(scrapes) the list of provided URLs in parallel with timeout handling.
        urls -> List of URLs to scrape/crawl to
        returns dictionary with results
        """
        try:
            logger.info("=== Begin parallel sitemap crawling ===")
            base_url = url.rstrip("/")
            website_title = "Untitled"
            markdowns = []

            urls = self.sitemap_extractor.get_urls_from_sitemap(url)

            if not urls:
                logger.info(f"No urls found for url: {url}")
                return website_title, markdowns

            logger.info(f"Found {len(urls)} urls for crawling from {url}")

            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                results = await crawler.arun_many(
                    urls=urls,
                    config=self.run_config,
                    dispatcher=self.dispatcher
                )

            logger.info(f"Processed {len(results)} URLs from sitemap crawling.")

            for result in results:
                title, stop = self._handle_crawl_result(result, base_url, markdowns)
                if title != "Untitled":
                    website_title = title

                if stop:
                    logger.error("=== Sitemap crawling stopped due to timeout ===")
                    return "Untitled", []

            # Log final statistics #
            total_urls = len(results)
            logger.info(f"=== Sitemap crawling completed ===")
            logger.info(f"Total URLs processed: {total_urls}")
            logger.info(f"Final markdown count: {len(markdowns)}")

            return website_title, markdowns

        except Exception as e:
            logger.exception(f"Unexpected error during sitemap crawling: {e}")
            return "Untitled", []


    async def crawl_multipage(self, start_url: str, max_depth: int = 2):
        base_url = start_url.rstrip("/")
        website_title = "Untitled"
        markdowns = []

        # Track visited URLs to prevent revisiting and infinite loops #
        visited = set()

        # Start with the initial URL #
        current_urls = {normalize_url(start_url)}

        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                for depth in range(max_depth):
                    logger.info(f"\n=== Crawling Depth {depth + 1}/{max_depth} ===")

                    # Only crawl URLs we haven't seen yet (ignoring fragments) #
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

                        title, stop = self._handle_crawl_result(result, base_url, markdowns)
                        if title != "Untitled":
                            website_title = title

                        if stop:
                            logger.error("=== Sitemap crawling stopped due to timeout ===")
                            return "Untitled", []

                            # Collect all new internal links for the next depth #
                        if result.success:
                            if internal_links := result.links.get("internal") if result.links else None:
                                hrefs = [
                                    normalize_url(link["href"])
                                    for link in internal_links
                                    if "href" in link
                                ]

                                # Filter by domain #
                                filtered_urls = self.sitemap_extractor.filter_urls_by_domain(hrefs, base_url)

                                # Add to next level if not visited
                                for next_url in filtered_urls:
                                    if next_url not in visited:
                                        next_level_urls.add(next_url)

                        else:
                            logger.error(f"Failed to crawl {result.url}: {result.error_message}")

                    # Move to the next set of URLs for the next recursion depth #
                    current_urls = next_level_urls
                    logger.info(f"Discovered {len(next_level_urls)} new URLs for next depth")

            logger.info("=== Recursive crawling completed ===")
            logger.info(f"Total URLs crawled: {len(visited)}")
            logger.info(f"Final website_title: {website_title}")
            logger.info(f"Final markdown count: {len(markdowns) if markdowns else 'None or empty'}")

            return website_title, markdowns

        except Exception as e:
            logger.exception(f"Unexpected error during crawling {e}")
            return "Untitled", []


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

    def _handle_crawl_result(self, result, base_url: str, markdowns: list) -> tuple[str, bool]:
        """
        Handle individual crawl result with proper error logging and timeout handling
        Returns: (website_title, timeout_occurred)
        """
        website_title = "Untitled"

        if result.success:
            try:
                dr = result.dispatch_result
                markdown_object = result.markdown

                if markdown_object and hasattr(markdown_object, 'fit_markdown'):
                    markdowns.append(markdown_object.fit_markdown)

                    logger.info(f"Successfully crawled: {result.url}")
                    logger.info(f"Memory: {dr.memory_usage:.1f}MB")
                    logger.info(f"Duration: {dr.end_time - dr.start_time}")

                    self._log_memory(prefix="After processing result:")

                    # Set website title from the base URL
                    if result.url.rstrip("/") == base_url:
                        website_title = self.get_title(result)

                    return website_title, False
                else:
                    logger.warning(f"⚠ No markdown content extracted from: {result.url}")
                    return website_title, False

            except Exception as e:
                logger.error(f"✗ Error processing successful result for {result.url}: {e}")
                return website_title, False
        else:
            # Handle different types of failures
            error_msg = result.error_message or "Unknown error"

            # Check if it's a timeout error - stop the entire crawling process
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                logger.error(f"Crawler timed out")
                return website_title, True  # Signal timeout occurred
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                logger.warning(f"Access forbidden for {result.url} (continuing): {error_msg}")
            elif "404" in error_msg or "not found" in error_msg.lower():
                logger.warning(f"Page not found {result.url} (continuing): {error_msg}")
            elif "robots.txt" in error_msg.lower():
                logger.warning(f"Robots.txt blocked {result.url} (continuing): {error_msg}")
            else:
                logger.error(f"Failed to crawl {result.url}: {error_msg}")

            return website_title, False

    @staticmethod
    def get_title(result) -> str:
        html = result.html
        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.string.strip() if soup.title else "Untitled"
        return title
