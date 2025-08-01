from pydantic import HttpUrl
from app.core.logger import logger
from app.services.crawler.web_crawler import WebCrawler
from app.services.crawler.sitemap_extract import SitemapExtractor

async def run_crawler_service(url: HttpUrl):
    web_crawler = WebCrawler()
    extractor = SitemapExtractor()

    urls = await extractor.get_urls_from_sitemap(str(url))

    if urls:
        logger.info(f"Proceeding crawling with a sitemap:")
        return await web_crawler.crawl_sitemap(url=str(url))
    else:
        logger.info(f"Proceeding with recursive website crawling:")
        return await web_crawler.crawl_multipage(start_url=str(url))

