import time
import usaddress
import pyap
from commonregex import CommonRegex
import pymongo
from selenium.common.exceptions import TimeoutException
import requests
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Tag
from fake_useragent import UserAgent
from random import choice
import re
# from Simplified_System.Initial_Crawling.get_n_search_results import getGoogleLinksForSearchText

def get_browser():
    ua = UserAgent()
    # PROXY = proxy_generator()
    userAgent = ua.random #get a random user agent
    options = webdriver.ChromeOptions()  # use headless version of chrome to avoid getting blocked
    # options.add_argument('headless')
    options.add_argument(f'user-agent={userAgent}')
    # options.add_argument("start-maximized")# // open Browser in maximized mode
    # options.add_argument("disable-infobars")# // disabling infobars
    # options.add_argument("--disable-extensions")# // disabling extensions
    # options.add_argument("--disable-gpu")# // applicable to windows os only
    # options.add_argument("--disable-dev-shm-usage")# // overcome limited resource problems
    # options.add_argument('--proxy-server=%s' % PROXY)
    browser = webdriver.Chrome(chrome_options=options,  # give the path to selenium executable
                                   # executable_path='F://Armitage_lead_generation_project//chromedriver.exe'
                                   executable_path='F://Armitage_project//crawl_n_depth//utilities//chromedriver.exe',
                                    service_args=["--verbose", "--log-path=D:\\qc1.log"]
                                   )
    return browser

def get_address_from_google(company_name):
    results = []
    browser = get_browser()
    searchText = company_name+' australia phone number'
    searchGoogle = URL = f"https://google.com/search?q={searchText}"+"&num=" + str(10)
    browser.get(searchGoogle)
    time.sleep(5)
    pageSource = browser.page_source
    browser.quit()
    soup = BeautifulSoup(pageSource, 'html.parser')  # bs4 TxZVoe
    result_div = soup.find_all('div', attrs={'class': 'bBmoPd'})
    for each in result_div:
        if (len(each.get_text())):
            print(each.get_text())
            results.append(each.get_text())

    search_divs = soup.find_all('div', attrs={'class': 'g'})
    for each in search_divs:
        description = each.find('span', attrs={'class': 'st'})  # extracting the description
        if isinstance(description, Tag):
            description = description.get_text()
            extracted_tp_numbers = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]',
                                              description)  # extracting tp numbers
            results.extend(extracted_tp_numbers)
    results = list(set(results))
    return results

print(get_address_from_google('answersportals.com'))