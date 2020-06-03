#fix sys path if you want to run this script individually
#check chrome driver exeecutable path
import time
import sys

from bson import ObjectId

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

def proxy_generator():
    response = requests.get("https://sslproxies.org/")
    soup = BeautifulSoup(response.content, 'html5lib')
    proxy = {'https': choice(list(map(lambda x:x[0]+':'+x[1], list(zip(map(lambda x:x.text,
	   soup.findAll('td')[::8]), map(lambda x:x.text, soup.findAll('td')[1::8]))))))}
    return proxy

def get_browser():
    ua = UserAgent()
    PROXY = proxy_generator()
    # PROXY = {'https': '123.231.86.102'}
    print(PROXY)
    userAgent = ua.random #get a random user agent
    options = webdriver.ChromeOptions()  # use headless version of chrome to avoid getting blocked
    options.add_argument('headless')
    # options.add_argument(f'user-agent={userAgent}')
    # options.add_argument("start-maximized")# // open Browser in maximized mode
    # options.add_argument("disable-infobars")# // disabling infobars
    # options.add_argument("--disable-extensions")# // disabling extensions
    # options.add_argument("--disable-gpu")# // applicable to windows os only
    # options.add_argument("--disable-dev-shm-usage")# // overcome limited resource problems
    # options.add_argument('--proxy-server=%s' % PROXY['https'])
    # options.add_argument("--incognito")
    browser = webdriver.Chrome(chrome_options=options,  # give the path to selenium executable
                                   # executable_path='F://Armitage_lead_generation_project//chromedriver.exe'
                                   executable_path='F://Armitage_project//crawl_n_depth//utilities//chromedriver.exe',
                                    service_args=["--verbose", "--log-path=D:\\qc1.log"]
                                   )
    return browser



browser = get_browser()
browser.get('https://www.linkedin.com/company/armitage-associates-pty-ltd')
pageSource = browser.page_source
print(len(pageSource))
# browser.quit()

soup = BeautifulSoup(pageSource, 'html.parser')#bs4
com_sum = soup.findAll("p",attrs={'class': 'about-us__description'})
print('coml',len(com_sum))
for each_ele in com_sum:
    print(each_ele.get_text())
basic_info_dict = {}
basic_info = soup.findAll("dl",attrs={'class': 'about-us__basic-info-list'})
for each_bil in basic_info:
    all_bi = each_bil.findAll("div",attrs={'class':'basic-info-item'})
    for each_bi in all_bi:
        term_bi = each_bi.find("dt",attrs={'class':'basic-info-item__term'}).get_text()
        des_bi = each_bi.find("dd",attrs={'class':'basic-info-item__description'}).get_text()
        basic_info_dict[term_bi]=des_bi
print(basic_info_dict)
loc_info_dict = {}
location_info = soup.findAll("section",attrs={'class': 'locations section-container'})
for each_lo in location_info:
    l_items = each_lo.findAll("ul", attrs={'class':'show-more-less__list show-more-less__list--no-hidden-elems'})
    for each_li in l_items:
        locs = each_li.findAll("li", attrs={'class': 'locations__location'})
        for i,each_add in enumerate(locs):
            locations = each_add.get_text().strip()
            loc_info_dict['locs_'+str(i)]=locations
print(loc_info_dict)
emp_info_dict = {}
emp_info = soup.findAll("section",attrs={'class': 'employees-at section-container'})
for each_em in emp_info:
    e_items = each_em.findAll("ul", attrs={'class':'employees__list'})
    for each_emp in e_items:
        emps = each_emp.findAll("li", attrs={'class': 'result-card profile-result-card'})
        for i,each_em_li in enumerate(emps):
            emp_det = each_em_li.get_text()
            emp_info_dict['emp_det'+str(i)]=emp_det
print(emp_info_dict)
#     para = each_ele.text.replace("D&B Hoovers provides sales leads and sales intelligence data on over 120 million companies like CALTEX AUSTRALIA PETROLEUM PTY LTD around the world, including contacts, financials, and competitor information. To witness the full depth and breadth of our data and for industry leading sales intelligence tools, take D&B Hoovers for a test drive. Try D&B Hoovers Free","").strip()
#      # paras = para.split("<br/><br/
#