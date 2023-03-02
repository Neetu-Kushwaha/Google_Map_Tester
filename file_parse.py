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
Excel_INPUT_PATH = os.path.join(os.path.dirname(__file__), "paper_website_2_99.xlsx")
CSV_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "output.csv")


def split (pages, threads):
    chunk_size = math.ceil(len(pages) / threads)
    for start in range(0, len(pages), chunk_size):
        yield pages[start:start + chunk_size]


def scrape_pages (pages: list, thread_num: int, data: list, web_page: str):
    """ Extract data from specific pages in a thread
    Args:
        pages (list): list of pages to scrape
        thread_num (int): number of the current thread
        data (list): list where data will be saved
        web_page(str(): start with url to accept cookies
    """

    # Start scraper
    scraper = None
    if USE_SELENIUM:
        logger.info (f"(thread {thread_num}) chrome started in background")
        # scraper = WebScraping(headless=True, web_page=web_page)
        scraper = WebScraping(web_page=web_page)

    if scraper:
        scraper.element_to_be_clickable(XPATH_COOKIES)
    # Loop through csv rows
    for page in pages:
        if scraper:
            logger.info (f"(thread {thread_num}) Scraping page with chrome: {subpage}")
            scraper.element_to_be_clickable(XPATH_SEARCH)
            scraper.send_data(XPATH_SEARCH, page)
            scraper.click(XPATH_SEARCH_CLICK)
            time.sleep(10)
            time.sleep(40)
            name = scraper.get_text(XPATH_NAME)
            sub_name = scraper.get_text(XPATH_SUB_NAME)
            address = scraper.get_text(XPATH_ADDRESS)
            link = scraper.get_text(XPATH_WEBSITE_LINK)
            if link:
                link = "https://www." + link
        # Wait for loop to finish
            # Save found data
            data.append ([page, name, sub_name, address, link])


def write_to_xlsx(data):
    print('write to excel...')
    cols = ["name", "company_name", "Sub_name", "address", "website"]
    df = pd.DataFrame(data, columns=cols)
    df.to_excel('out.xlsx')


def main():
    """ Scrape pages from "input.csv" file and save results to "output.csv" file """

    web_page = "https://www.google.com/maps"

    # Validate input file
    # if not os.path.isfile(Excel_INPUT_PATH):
    #     logger.info("File 'input.xslx' not found")
    #     return ""

    # Read csv file content
    # with open(CSV_INPUT_PATH, "r") as file:
    #     pages = list(set(file.readlines()))

    df_new = pd.read_excel('keyword_usa.xlsx')

    keyword_search = df_new['new_keyword'].to_list()
    final_keyword = keyword_search[:8]

    # Create threads
    data = [["page", "company_name", "Sub_name", "address", "website"]]
    # organization_websiteLink = organization_websiteLink[:30]
    pages_threads = list(split(final_keyword, THREADS))
    print(len(pages_threads[0]))
    threads_objs = []
    for pages_thread in pages_threads:
        sleep(0.1)
        index = pages_threads.index(pages_thread) + 1
        logger.info("Starting thread " + str(index) + " of " + str(len(pages_threads)))
        thread_obj = threading.Thread(target=scrape_pages, args=(pages_thread, index, data, web_page))
        thread_obj.start()
        threads_objs.append(thread_obj)

        # Wait for threads to finish
    while True:
        sleep(1)
        running_threads = list(filter(lambda thread: thread.is_alive(), threads_objs))
        if not running_threads:
            break

    print(data)
    write_to_xlsx(data)
    # Save data to csv file when finished
    with open(CSV_OUTPUT_PATH, "w", encoding='UTF-8', newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)


if __name__ == "__main__":
    main()


