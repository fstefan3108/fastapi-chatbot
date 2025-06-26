import os
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from app.services.scrape.clean_body import clean_body_content
from app.services.scrape.extract_content import extract_body_content
from app.services.scrape.split_dom import split_dom_content


### Scrapes content from website using selenium web driver, which we connected to by proxy connection ###
### Gets the raw html and the page title for dynamically generating website title field, then calls the related ###
### functions for formatting the raw html into readable chunks, which are later called in the website API endpoint. ###
### Returns a dict with the scrapped data. ###

def scrape_website(url: str):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    chrome_driver_path = os.path.join(BASE_DIR, "chromedriver.exe")
    options = ChromeOptions()

    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    try:
        driver.get(url)
        title = driver.title
        html = driver.page_source
        body_text = extract_body_content(html)
        cleaned_text = clean_body_content(body_text)
        chunks = split_dom_content(cleaned_text)

        return {
            "title": title,
            "html": html,
            "body_text": body_text,
            "cleaned_text": cleaned_text,
            "chunks": chunks,
        }

    finally:
        driver.quit()







