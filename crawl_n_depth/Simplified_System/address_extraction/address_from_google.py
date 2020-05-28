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
from Simplified_System.Database.db_connect import refer_collection,refer_cleaned_collection


def get_browser():
    ua = UserAgent()
    # PROXY = proxy_generator()
    for k in range(5):
        userAgent = ua.random  # get a random user agent
        if ('Mobile' in userAgent):
            print("got mobile")
            continue
        else:
            break
    print(userAgent)
    options = webdriver.ChromeOptions()  # use headless version of chrome to avoid getting blocked
    options.add_argument("--no-sandbox")
    options.add_argument(f'user-agent={userAgent}')
    options.add_argument('headless')
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

def scrape_address_from_google(company_name):
    results = []
    browser = get_browser()
    searchText = company_name+' australia street address'
    searchGoogle = URL = f"https://google.com/search?q={searchText}"+"&num=" + str(10)
    browser.get(searchGoogle)
    time.sleep(5)
    pageSource = browser.page_source
    browser.quit()
    soup = BeautifulSoup(pageSource, 'html.parser')#bs4
    is_captcha_on_page = soup.find("div", id="recaptcha") is not None
    if (is_captcha_on_page):  # a captcha triggered
        print("Captcha Detected")
        return results
    result_div = soup.find_all('div', attrs={'class': 'NqXXPb'})
    for each in result_div:
        if(len(each.get_text())):
            print(each.get_text())
            results.append(each.get_text())

    result_div = soup.find_all('tr', attrs={'class': 'ztXv9'})
    results =list(set(results))
    return results

def get_ad_from_google(id_list):
    # mycol = refer_collection()
    mycol = refer_cleaned_collection()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        try:
            comp_name = data[0]['comp_name']
            print(comp_name)
            g_ad_data = scrape_address_from_google(comp_name)
            data_dict = {'google_address':g_ad_data}
            print(data_dict)
            if(len(g_ad_data)):
                mycol.update_one({'_id': entry_id},
                                 {'$set': data_dict})
                print("Successfully extended the data entry with google address data", entry_id)
            else:
                print("No google address data found! dict is empty")
        except IndexError:
            print("No google address data found!")
        except KeyError:
            print("No google address data found!")


# get_ad_from_google([ObjectId('5eb6311c86662885174692de')])

# print(scrape_address_from_google("armitage"))

