import time
import usaddress
import pyap
from bson import ObjectId
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
import sys
sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
from Simplified_System.Database.db_connect import refer_collection

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



def scrape_cp_from_google(company_name):
    results = []
    browser = get_browser()
    searchText = company_name+' australia CEO | founder | director'
    searchGoogle = URL = f"https://google.com/search?q={searchText}"+"&num=" + str(10)
    browser.get(searchGoogle)
    time.sleep(5)
    pageSource = browser.page_source
    browser.quit()
    soup = BeautifulSoup(pageSource, 'html.parser')  # bs4 TxZVoe
    result_div = soup.find_all('div', attrs={'class': 'LGOjhe'})
    for each in result_div:
        # print(each.text)
        if (len(each.get_text())):
            print(each.get_text())
            results.append(each.get_text())
    results = list(set(results))
    return results

def get_cp_from_google(id_list):
    mycol = refer_collection()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        try:
            comp_name = data[0]['comp_name']
            print(comp_name)
            g_cp_data = scrape_cp_from_google(comp_name)
            data_dict = {'google_cp':g_cp_data}
            print(data_dict)
            if(len(data_dict.keys())):
                mycol.update_one({'_id': entry_id},
                                 {'$set': data_dict})
                print("Successfully extended the data entry with google contact data", entry_id)
            else:
                print("No google contact data found! dict is empty")
        except IndexError:
            print("No google contact data found!")
        except KeyError:
            print("No google contact data found!")


get_cp_from_google([ObjectId('5eb6311c86662885174692de')])
# print(get_cp_from_google('skedulo'))