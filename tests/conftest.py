# from ad import WebScraping
# from selenium import webdriver
# from selenium import webdriver
# from selenium import webdriver
import pytest
from scraping_manager.automate import WebScraping
from config import TestData
# web_page = "https://www.google.com/maps"


# scraper = None
# This fixture contains the set up and tear down code for each test.
@pytest.fixture(scope='class')
def init_driver(request):
    # global scraper
    web_scraper = WebScraping(web_page=TestData.BASE_URL)
    request.cls.scraper = web_scraper
    yield
    web_scraper.end_browser()
