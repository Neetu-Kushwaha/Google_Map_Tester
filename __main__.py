import os
import re
import csv
import math
import time
import requests
import threading
from logs import logger
from time import sleep
from bs4 import BeautifulSoup
from scraping_manager.automate import WebScraping
from dotenv import load_dotenv
import urllib.parse
from collections import defaultdict
import pandas as pd
load_dotenv()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}

USE_SELENIUM = os.getenv("USE_SELENIUM", "").lower() == "true"
WAIT_TIME = int(os.getenv("WAIT_TIME", 0))
THREADS = int(os.getenv("THREADS", 1))
XPATH_SEARCH = '//*[@id="searchboxinput"]'
XPATH_SEARCH_CLICK = '//*[@id="searchbox-searchbutton"]'
XPATH_COOKIES = '//*[@id="yDmH0d"]/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[1]/div/div/button'
XPATH_NAME = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[1]/h1/span[2]'
XPATH_ADDRESS = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div[3]/button/div[1]/div[2]/div[1]'
XPATH_WEBSITE_LINK = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div[5]/a/div[1]/div[2]/div[1]'
XPATH_SUB_NAME = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[2]/span[1]/span[1]/button'
Excel_INPUT_PATH = os.path.join(os.path.dirname(__file__), "input.xlsx")



def write_to_xlsx(data):
    print('write to excel...')
    # name of columns in excel file
    cols = ["name", "company_name", "Sub_name", "address", "website"]
    # convert data to data frame
    df = pd.DataFrame(data, columns=cols)
    # save data frame df to
    df.to_excel('output.xlsx')


def scrape_pages(web_page: str, final_keyword: list) -> dict:
    """ Extract data from specific pages in a website

    Args:
        # start_page (int): start page number
        # final_keyword (list): number of keywords to search in google map
    """

    # Start scraper
    scraper = None
    if USE_SELENIUM:
        logger.info(f"chrome started in background")
        scraper = WebScraping(headless=True, web_page=web_page)

    if scraper:
        scraper.element_to_be_clickable(XPATH_COOKIES)
    time.sleep(5)
    data = []
    for i in final_keyword:
        scraper.set_page(web_page)
        scraper.element_to_be_clickable(XPATH_SEARCH)
        scraper.send_data(XPATH_SEARCH, i)
        scraper.click(XPATH_SEARCH_CLICK)
        print("keyword------", i)
        time.sleep(10)
        time.sleep(20)
        name = scraper.get_text(XPATH_NAME)
        sub_name = scraper.get_text(XPATH_SUB_NAME)
        address = scraper.get_text(XPATH_ADDRESS)
        link = scraper.get_text(XPATH_WEBSITE_LINK)
        if link:
            new_website = "https://www."+ link
            print(new_website)
        print("----------")
        data.append([i, name, sub_name, address, link])
        time.sleep(70)
    return data

def main():
    """ Scrape pages from "input.xlsx" file and save results to "output.xlsx" file """

    # Website link to scrape
    web_page = "https://www.google.com/maps"

    # Validate input file
    if not os.path.isfile(Excel_INPUT_PATH):
        logger.info("File 'input.xslx' not found")
        return ""
    df_new = pd.read_excel('input.xlsx')

    # convert 'new_keyword' column from data frame (df_new) to list
    keyword_search = df_new['new_keyword'].to_list()
    # select subset of keyword
    final_keyword = keyword_search[600:700]

    # Wait for scrape_pages function to finish
    data1 = scrape_pages(web_page, final_keyword)

    # Save data to excel file when finished
    write_to_xlsx(data1)


if __name__ == "__main__":
    main()


