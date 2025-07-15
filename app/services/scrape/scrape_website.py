from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from app.core.logger import logger

class Scraper:

    """
    - Scrapes the provided website's content using playwright.
    - extract_body_content() -> extracts the raw html content of the website using bs.
    - clean_body_content() -> cleans the raw html content by removing unnecessary tags (like style, script).
    - split_dom_content() -> splits the content into chunks so we don't overload the AI model.
    - Synchronous because celery is more compatible with sync functionality.
    """

    def __init__(self, url: str):
        self.url = url
        self.title = ""
        self.html = ""
        self.body_text = ""
        self.cleaned_text = ""
        self.chunks = []

    def scrape(self) -> dict:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()

                page.goto(self.url, wait_until="domcontentloaded")

                self.title = page.title()
                self.html = page.content()

                self.body_text = self.extract_body_content()
                self.cleaned_text = self.clean_body_content()
                self.chunks = self.split_dom_content()

            return {
                "title": self.title,
                "url": self.url,
                "chunks": self.chunks,
            }

        except Exception as e:
            logger.error(f"Error scraping: {e}", exc_info=True)
            raise


    def extract_body_content(self) -> str:
        soup = BeautifulSoup(self.html, 'html.parser')
        body_content = soup.body
        if body_content:
            return str(body_content)
        return ""


    def clean_body_content(self) -> str:
        soup = BeautifulSoup(self.body_text, 'html.parser')

        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()

        cleaned_text = soup.get_text(separator='\n')
        cleaned_text = '\n'.join(line.strip() for line in cleaned_text.splitlines() if line.strip())

        return cleaned_text


    def split_dom_content(self, max_length=6000) -> list[str]:
        return [self.cleaned_text[i: i + max_length] for i in range(0, len(self.cleaned_text), max_length)]

