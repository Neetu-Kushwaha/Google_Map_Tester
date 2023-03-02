from config import TestData
from test_base import BaseTest
import time
import pytest
from scraping_manager.automate import WebScraping


class TestWebsite(BaseTest):

    def test_cookies(self):
        flag = self.scraper.check_exists_by_xpath(TestData.XPATH_COOKIES)
        assert flag

    def test_cookies_click(self):
        print("hello word")
        self.scraper.element_to_be_clickable(TestData.XPATH_COOKIES)
        time.sleep(10)
        flag = self.scraper.check_exists_by_xpath(TestData.XPATH_COOKIES) == False
        assert flag

    def test_search_click(self):
        self.scraper.element_to_be_clickable(TestData.XPATH_SEARCH)
        self.scraper.send_data(TestData.XPATH_SEARCH, TestData.KEYWORD_SEARCH)
        self.scraper.click(TestData.XPATH_SEARCH_CLICK)
        time.sleep(10)
        assert self.scraper.check_exists_by_xpath(TestData.XPATH_SEARCH_CLICK)

    def test_search_result(self):
        assert self.scraper.get_text(TestData.XPATH_NAME) == TestData.RESULT_NAME
        assert self.scraper.get_text(TestData.XPATH_SUB_NAME) == TestData.RESULT_SUB_NAME
        assert self.scraper.get_text(TestData.XPATH_ADDRESS) == TestData.RESULT_ADDRESS
        assert self.scraper.get_text(TestData.XPATH_WEBSITE_LINK) == TestData.RESULT_WEBSITE

