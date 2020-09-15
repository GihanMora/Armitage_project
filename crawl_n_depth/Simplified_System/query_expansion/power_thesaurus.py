
# setx AVENTION_PASSWORD "<password>"
import ast
import os
import time
import sys
from selenium.webdriver.common.by import By
from azure.storage.queue import QueueClient
from bson import ObjectId
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.keys import Keys

from os.path import dirname as up

from selenium.webdriver.remote.webelement import WebElement

three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)

from Simplified_System.Database.db_connect import refer_collection

from selenium.webdriver.common.keys import Keys
import pymongo
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import requests
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Tag
from fake_useragent import UserAgent
from random import choice
from Simplified_System.Initial_Crawling.get_n_search_results import getGoogleLinksForSearchText

def get_browser():
    # ua = UserAgent()
    # PROXY = proxy_generator()
    # userAgent = ua.random #get a random user agent
    options = webdriver.ChromeOptions()  # use headless version of chrome to avoid getting blocked
    # options.add_argument('headless')
    # options.add_argument('window-size=1920x1080')
    # options.add_argument(f'user-agent={userAgent}')
    options.add_argument("incognito")#
    options.add_argument("start-maximized")# // open Browser in maximized mode
    options.add_argument("disable-infobars")# // disabling infobars
    options.add_argument("--disable-extensions")# // disabling extensions
    options.add_argument("--disable-gpu")# // applicable to windows os only
    options.add_argument("--disable-dev-shm-usage")# // overcome limited resource problems
    # options.add_argument('--proxy-server=%s' % PROXY)
    browser = webdriver.Chrome(chrome_options=options,  # give the path to selenium executable
                                   # executable_path='F://Armitage_lead_generation_project//chromedriver.exe'
                                   executable_path=three_up+'//utilities//chromedriver.exe',
                               # service_args=["--verbose", "--log-path=D:\\qc1.log"]
                                   )
    return browser

def get_results_pt(query):
    browser = None
    try:

        browser = get_browser()
        browser.maximize_window()

        # browser.get('chrome://settings/clearBrowserData')
        # browser.find_element_by_xpath('//settings-ui').send_keys(Keys.ENTER)

        time.sleep(5)
        browser.get('https://www.powerthesaurus.org/')
        browser.find_element_by_name('q').send_keys(query)
        time.sleep(3)
        browser.find_element_by_name('q').send_keys(Keys.RETURN)
        time.sleep(5)

        pageSource = browser.page_source
        soup = BeautifulSoup(pageSource, 'html.parser')#bs4

        syn_results = soup.findAll("a",attrs={'class': 'b4_cm b4_b5 ts_cm'})
        # print(syn_results)
        similar_queries = []
        for each_res in syn_results:
            similar_queries.append(each_res.get_text())

        return similar_queries
        browser.close()
        browser.quit()
    except WebDriverException:
        print("Browser Issue Occured!")
        if(browser!=None):
            browser.close()
            browser.quit()
        return []
    except Exception as e:
        print("Exception Occured!",e)
        if (browser != None):
            browser.close()
            browser.quit()
        return []


# get_results_pt("content management")




