import time
import sys
sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
from Simplified_System.Database.db_connect import refer_collection


import pymongo
from selenium.common.exceptions import TimeoutException
import requests
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Tag
from fake_useragent import UserAgent
from random import choice
from Simplified_System.Initial_Crawling.get_n_search_results import getGoogleLinksForSearchText
def get_browser():
    ua = UserAgent()
    # PROXY = proxy_generator()
    userAgent = ua.random #get a random user agent
    options = webdriver.ChromeOptions()  # use headless version of chrome to avoid getting blocked
    options.add_argument('headless')
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument("start-maximized")# // open Browser in maximized mode
    options.add_argument("disable-infobars")# // disabling infobars
    options.add_argument("--disable-extensions")# // disabling extensions
    options.add_argument("--disable-gpu")# // applicable to windows os only
    options.add_argument("--disable-dev-shm-usage")# // overcome limited resource problems
    # options.add_argument('--proxy-server=%s' % PROXY)
    browser = webdriver.Chrome(chrome_options=options,  # give the path to selenium executable
                                   # executable_path='F://Armitage_lead_generation_project//chromedriver.exe'
                                   executable_path='F://Armitage_project//crawl_n_depth//utilities//chromedriver.exe'
                                   )
    return browser


def scrape_opencorporates(comp_url):

    browser = get_browser()
    # browser.set_page_load_timeout(30)
    try:
        browser.get(comp_url)
        # time.sleep(5)
    except TimeoutException:
        print("browser timeout")
        return []
    pageSource = browser.page_source
    browser.quit()
    # print(pageSource)
    results=[]
    soup = BeautifulSoup(pageSource, 'html.parser')#bs4
    # dt_list = soup.findAll("dt")
    attriss = soup.findAll('div', {'id': 'attributes'})
    attribute_data = {}
    for elem in attriss:
        for each_dd in elem.find_all("dd"):
            if(len(each_dd["class"])==1):
                # print(each_dd["class"])
                attribute_data[each_dd["class"][0]] = each_dd.text
            else:
                tag = "_".join(each_dd["class"])
                # print(tag)
                if(tag =='officers_trunc8'):
                    attribute_data["directors_or_officers"]=each_dd.text
                else:
                    attribute_data[tag] = each_dd.text


    for each in attribute_data:
        print(each,attribute_data[each])
    print(attribute_data)
    # children = attriss.find("dd")
    # for child in children:
    #     print(child)
    # dd_list = soup.findAll("dd")
    print("***********************************")
    # print(attribute_list)
    # for i in dd_list:
    #     print(i["class"],i.text)
scrape_opencorporates('https://opencorporates.com/companies/us_ca/C3957816')
