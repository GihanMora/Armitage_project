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
    options.add_argument('headless')
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
def add_parser(text):
    extracted_addresses = []
    addregexau = re.compile(
        r"(?i)(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d+))(\b(?:(?!\s{2,}).){1,60})\b(New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|VIC|NSW|ACT|QLD|NT|SA|TAS|WA).?[,\s|.\s|,.|\s]*(\b\d{4}).?[,\s|.\s|,.|\s]*(\b(Australia|Au))?")
    searchau = addregexau.findall(text)
    if (len(searchau)):
        add_r = (" ").join(list(searchau[0]))
        add_r = add_r.strip()
        extracted_addresses.append(add_r)
        # print("au", add_r)

    addregexnz = re.compile(
        r"(?i)(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d+))(\b(?:(?!\s{2,}).){1,60})\b(Northland|Auckland|Waikato|Bay of Plenty|Gisborne|Hawke's Bay|Taranaki|Manawatu-Whanganui|Wellington|Tasman|Nelson|Marlborough|West Coast|Canterbury|Otago|Southland).?[,\s|.\s|,.|\s]*(\b\d{4}).?[,\s|.\s|,.|\s]*(\b(New zealand|Newzealand|Nz))?")
    searchnz = addregexnz.findall(text)
    if (len(searchnz)):
        add_nz = (" ").join(list(searchnz[0]))
        add_nz = add_nz.strip()
        extracted_addresses.append(add_nz)
        # print("nz", add_nz)


    adss = pyap.parse(text, country='US')  # extracting addresses(Us address parser)
    adss = [str(i) for i in adss]
    if (len(adss)):
        extracted_addresses.extend(adss)

    return extracted_addresses

def get_address_from_google(company_name):
    results = []
    browser = get_browser()
    searchText = company_name+' australia street address'
    searchGoogle = URL = f"https://google.com/search?q={searchText}"+"&num=" + str(10)
    browser.get(searchGoogle)
    time.sleep(5)
    pageSource = browser.page_source
    browser.quit()
    soup = BeautifulSoup(pageSource, 'html.parser')#bs4
    result_div = soup.find_all('div', attrs={'class': 'NqXXPb'})
    for each in result_div:
        print(each.get_text())
        if(len(each.get_text())):
            print(each.get_text())
            results.append(each.get_text())

    result_div = soup.find_all('tr', attrs={'class': 'ztXv9'})
    for each in result_div:
        if (len(each.get_text())):
            print(each.get_text())
            results.append(each.get_text())

    search_divs = soup.find_all('div', attrs={'class': 'g'})
    for each in search_divs:
        description = each.find('span', attrs={'class': 'st'})  # extracting the description
        if isinstance(description, Tag):
            description = description.get_text()
            ext_ads = add_parser(description)
            if(len(ext_ads)):
                results.extend(ext_ads)

    # print(extracted_addresses)
    # print(results)
    results =set(results)
    return results


print(get_address_from_google("armitage"))

