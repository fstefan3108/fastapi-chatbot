import requests
from xml.etree import ElementTree
from urllib.parse import urljoin, urlparse
from app.core.logger import logger


class SitemapExtractor:
    """
    A class to extract URLs from website sitemaps
    """
    def __init__(self):
        self.timeout = 10

    def get_urls_from_sitemap(self, base_url: str) -> list[str]:
        """
        Extracts URLs from sitemap
        base_url -> the base url of the website (e.g. http://example.com)
        Returns a list of URLs found in the sitemap
        """
        sitemap_paths = ['/sitemap.xml', '/sitemap_index.xml', '/sitemap.xml.gz']

        for sitemap_path in sitemap_paths:
            sitemap_url = urljoin(base_url, sitemap_path) # Joins base url with sitemap paths #
            if urls := self._fetch_sitemap_urls(sitemap_url):

                logger.info(f"Found {len(urls)} URLs in sitemap: {sitemap_url}")
                return self.filter_urls_by_domain(urls, base_url)

        logger.info(f"No sitemap found for: {base_url}")
        return []

    def _fetch_sitemap_urls(self, sitemap_url: str) -> list[str]:
        """
        Fetch URLs from the provided sitemap url
        sitemap_url -> the url of the sitemap passed by the main get_urls_from_sitemap method
        returns a list of URLs found in the sitemap
        """
        try:
            response = requests.get(sitemap_url, timeout=self.timeout)
            response.raise_for_status()

            root = ElementTree.fromstring(response.content) # Parses the xml #
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = [loc.text for loc in root.findall('.//ns:loc', namespace)] # Extracts the actual urls inside <loc> xml tags #

            return urls

        except Exception as e:
            logger.error(f"Error fetching sitemap: {sitemap_url}: {e}")
            return []

    @staticmethod
    def filter_urls_by_domain(urls: list[str], base_url: str) -> list[str]:
        """
        Filters irrelevant external URLs in the sitemap (if there are any)
        (e.g. we have a https://www.invt.tech/ domain, and an external instagram link
        in the sitemap we don't need to jump/crawl to.)
        urls -> fetched urls that need to be filtered
        base_url -> base url of the site, used to compare domains against
        returns filtered urls
        """
        base_domain = urlparse(base_url).netloc # from https://www.invt.tech/ to -> www.invt.tech #

        filtered_urls = [
            url for url in urls
            if urlparse(url).netloc == base_domain
        ]

        return filtered_urls