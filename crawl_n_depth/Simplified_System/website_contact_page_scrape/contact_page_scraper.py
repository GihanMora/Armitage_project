#fix sys path if you want to run this script individually
#check chrome driver exeecutable path
import re
import time
import sys

import pyap
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

def is_valid_tp(tp):
    ll = ''.join(filter(str.isdigit, tp))
    if(len(tp)>20):
        return False
    if('.' in tp):
        return False
    if ('12345678' in tp):
        return False
    elif (len(ll) == 10 and (ll[0] == '1' or ll[0] == '0')):
        return True
    elif (len(ll) == 11 and ll[0:2] == '61'):
        return True
    elif (len(ll) == 12 and ll[0:2] == '61'):
        return True
    elif ((len(ll) == 10 or len(ll) == 9) and (ll[0] == '0')):
        return True
    elif ((len(ll) == 10 or len(ll) == 11 or len(ll) == 12) and (ll[0:2] == '64')):
        return True
    else:return False

def add_parser(text):
    extracted_addresses = []
    addregexau = re.compile(
        r"(?i)(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d+))(\b(?:(?!\s{5,}).){1,60})\b(New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|VIC|NSW|ACT|QLD|NT|SA|TAS|WA|Pymble).?[,\s|.\s|,.|\s]*(\b\d{4}).?[,\s|.\s|,.|\s]*(\b(Australia|Au))?")
    searchau = re.findall(addregexau, text)
    for each in searchau:
        add_l = []
        add_r = list(each)
        for each_r in add_r:
            if (each_r.strip() not in add_l):
                # print(each_r,len(each_r.strip()))
                add_l.append(each_r.strip())
        # print(add_l)
        add_f = (" ").join(add_l).strip()
        extracted_addresses.append(add_f)
        # print("au", add_r)

    addregexnz = re.compile(
        r"(?i)(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d+))(\b(?:(?!\s{5,}).){1,60})\b(Northland|Auckland|Waikato|Bay of Plenty|Gisborne|Hawke's Bay|Taranaki|Manawatu-Whanganui|Wellington|Tasman|Nelson|Marlborough|West Coast|Canterbury|Otago|Southland).?[,\s|.\s|,.|\s]*(\b\d{4}).?[,\s|.\s|,.|\s]*(\b(New zealand|Newzealand|Nz))?")
    searchnz = addregexnz.findall(text)
    for each in searchnz:
        add_ln = []
        add_rn = list(each)
        for each_rn in add_rn:
            if (each_rn.strip() not in add_ln):
                add_ln.append(each_rn.strip())
        # print(add_l)
        add_fn = (" ").join(add_ln).strip()
        extracted_addresses.append(add_fn)
        # print("nz", add_nz)

    return extracted_addresses

def get_domain(c_n_link):

    c_n_dom = c_n_link.split("/")[2]
    try:
        c_name = c_n_dom.split("www.")[1]
    except IndexError:
        c_name = c_n_dom
    if ('.com' in c_name):
        cc_name = c_name.split(".com")[0]
    elif ('.org' in c_name):
        cc_name = c_name.split(".org")[0]
    elif ('.io' in c_name):
        cc_name = c_name.split(".io")[0]
    elif ('.net' in c_name):
        cc_name = c_name.split(".net")[0]
    else:
        cc_name = c_name

    return cc_name

def get_browser():
    ua = UserAgent()

    userAgent = ua.random #get a random user agent
    options = webdriver.ChromeOptions()  # use headless version of chrome to avoid getting blocked
    options.add_argument('headless')
    # options.add_argument(f'user-agent={userAgent}')
    options.add_argument('--no-sandbox')
    # options.add_argument("start-maximized")# // open Browser in maximized mode
    # options.add_argument("disable-infobars")# // disabling infobars
    # options.add_argument("--disable-extensions")# // disabling extensions
    # options.add_argument("--disable-gpu")# // applicable to windows os only
    # options.add_argument("--disable-dev-shm-usage")# // overcome limited resource problems
    # options.add_argument('--proxy-server=%s' % PROXY)
    options.add_argument("--incognito")
    browser = webdriver.Chrome(chrome_options=options,  # give the path to selenium executable
                                   # executable_path='F://Armitage_lead_generation_project//chromedriver.exe'
                                   executable_path='F://Armitage_project//crawl_n_depth//utilities//chromedriver.exe',
                                    service_args=["--verbose", "--log-path=D:\\qc1.log"]
                                   )
    return browser


def get_contact_page(entry_id):
    c_p_urls = []
    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    attris = list(data[0].keys())
    if ('crawled_links' in attris):
        crawled_links = data[0]['crawled_links']
        for each_cl in crawled_links:
            if ('contact' in each_cl.lower()):
                c_p_urls.append(each_cl)
                print('taken from crawled links')
    if(len(c_p_urls)==0):
        comp_url = data[0]['link']
        sr = getGoogleLinksForSearchText(comp_url + " contact", 5, 'normal')
        if (len(sr) == 0):
            sr = getGoogleLinksForSearchText(comp_url + " contact", 5, 'normal')
            if (len(sr) == 0):
                sr = getGoogleLinksForSearchText(comp_url + " contact", 5, 'normal')
        filtered_li = []
        for p in sr:
            # print(p['link'])
            if ('contact' in p['link'].lower()):
                print(get_domain(p['link']),get_domain(comp_url))
                if(get_domain(p['link'])==get_domain(comp_url)):
                    filtered_li.append(p['link'])
        if (len(filtered_li)):
            print('filtered',filtered_li)
            c_p_urls.extend(filtered_li)
    if(len(c_p_urls)):
        return [c_p_urls[0]]
    else:
        return []

# get_contact_page(ObjectId('5eb63c1e9c69232f6ed6edd8'))
def get_tp(all_text_in_page):
    extracted_tp_numbers = re.findall(r'[(]?[+]?[0-9][0-9 .\-\(\)]{8,}[0-9]', all_text_in_page)  # extracting tp numbers
    filtered_tp = []
    for each_tp in extracted_tp_numbers:
        if (each_tp.count('(') == 1 and each_tp.count(')') == 0):
            each_tp = each_tp.replace('(', "")
        # print(tp)
        if (is_valid_tp(each_tp)):
            filtered_tp.append(each_tp)
    return filtered_tp
def clean_add(add_list):
    cleaned_add = []
    for each_ad in add_list:
        if(' Act ' in each_ad or ' act ' in each_ad):
            continue
        if (' Sa ' in each_ad or ' sa ' in each_ad):
            continue
        if (' Wa ' in each_ad or ' wa ' in each_ad):
            continue
        if (' tas ' in each_ad or ' Tas ' in each_ad):
            continue
        w_ori_list = each_ad.split(" ")
        w_list = each_ad.lower().split(" ")
        if('level' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('level'):])
            each_ad = cl_ad
        if ('post' in w_list and 'box' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('post'):])
            each_ad = cl_ad
        if ('po' in w_list and 'box' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('po'):])
            each_ad = cl_ad

        each_ad = each_ad.replace('\\n','')
        each_ad = each_ad.replace('\n', '')
        each_ad = each_ad.replace('\\', '')
        each_ad = each_ad.replace('+', '')
        each_ad = each_ad.replace('<br','')
        each_ad = each_ad.replace('/>', '')
        cleaned_add.append(each_ad)
    return cleaned_add

def scrape_c_page(c_p_link):
    data_dict = {}
    telephone_numbers = []
    emails = []
    addresses = []
    social_media_links = []

    browser = get_browser()
    browser.get(c_p_link)
    pageSource = browser.page_source
    # print(pageSource)
    soup = BeautifulSoup(pageSource, "lxml")
    all_text_in_page = ''
    blacklist = [
        '[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style'

    ]
    text = soup.find_all(text=True)  # extract and concatenate all text in the site
    text_strip = [t.strip() for t in text]
    text_adds = (" ").join(text_strip)

    # print(text)
    for t in text:
        if t.parent.name not in blacklist:
            all_text_in_page += '{} '.format(t)

    # if(response.url == 'https://www.codelikeagirl.com/'):
    #     print(all_text_in_page)
    # print("all",all_text_in_page)
    telephone_numbers.extend(get_tp(all_text_in_page))

    extracted_emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", all_text_in_page)  # extracting emails
    emails.extend(extracted_emails)

    adds_from_reg = add_parser(text_adds)
    adds_from_reg = clean_add(adds_from_reg)
    addresses.extend(adds_from_reg)
    # print(all_text_in_page)

    # extracted_addresses = pyap.parse(all_text_in_page, country='US')#extracting addresses(Us address parser)
    # extracted_addresses = [str(i) for i in extracted_addresses]
    # addresses.extend(extracted_addresses)
    sm_sites = ['twitter.com', 'facebook.com', 'linkedin.com', 'youtube.com']
    extracted_sm_sites = []

    all_links = soup.find_all('a', href=True)  # extracting social media links
    for link_i in all_links:
        link_s = link_i['href']
        if (
                'twitter' in link_s or 'facebook' in link_s or 'linkedin' in link_s or 'youtube' in link_s or 'instagram' in link_s):
            extracted_sm_sites.append(link_s)
            # print(link_s)

    social_media_links.extend(extracted_sm_sites)

    # all_urls = [l['href'] for l in all_links]
    # contact_urls = []
    # for each_l in all_urls:
    #     if ('contact' in each_l.lower()):
    #         if (get_domain(c_p_link) == get_domain(each_l)):
    #             contact_urls.append(each_l)
    #
    # contact_urls.remove(c_p_link)
    # contact_urls = list(set(contact_urls))
    # print("**", contact_urls)
    # for each_cont_l in contact_urls:
    #     browser = get_browser()
    #     browser.get(each_cont_l)
    #     pageSource = browser.page_source
    #     # print(pageSource)
    #     soup = BeautifulSoup(pageSource, "lxml")
    #     all_text_in_page = ''
    #     blacklist = [
    #         '[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style'
    #
    #     ]
    #     text = soup.find_all(text=True)  # extract and concatenate all text in the site
    #     text_adds = (" ").join(text)
    #
    #     # print(text)
    #     for t in text:
    #         if t.parent.name not in blacklist:
    #             all_text_in_page += '{} '.format(t)
    #
    #     # if(response.url == 'https://www.codelikeagirl.com/'):
    #     #     print(all_text_in_page)
    #
    #     telephone_numbers.extend(get_tp(all_text_in_page))
    #
    #     extracted_emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", all_text_in_page)  # extracting emails
    #     emails.extend(extracted_emails)
    #
    #     adds_from_reg = add_parser(all_text_in_page)
    #     addresses.extend(adds_from_reg)
    #     sm_sites = ['twitter.com', 'facebook.com', 'linkedin.com', 'youtube.com']
    #     extracted_sm_sites = []
    #
    #     all_links = soup.find_all('a', href=True)  # extracting social media links
    #     for link_i in all_links:
    #         link_s = link_i['href']
    #         if (
    #                 'twitter' in link_s or 'facebook' in link_s or 'linkedin' in link_s or 'youtube' in link_s or 'instagram' in link_s):
    #             extracted_sm_sites.append(link_s)
    #             # print(link_s)
    #
    #     social_media_links.extend(extracted_sm_sites)
    print(emails)
    print(social_media_links)
    print(telephone_numbers)
    print(addresses)
    data_dict['emails']=list(set(emails))
    data_dict['social_media_links'] = list(set(social_media_links))
    data_dict['telephone_numbers'] = list(set(telephone_numbers))
    data_dict['addresses'] = list(set(addresses))
    return data_dict


# scrape_c_page('https://centralinnovation.com/contact-us/australian-offices/new-south-wales-head-office/')

def get_cp_page_data(id_list):
    mycol = refer_collection()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        cont_page = get_contact_page(entry_id)
        if(len(cont_page)):
            scraped_data_dict = scrape_c_page(cont_page[0])
            if(len(scraped_data_dict.keys())):
                updated_emails = data[0]['emails']+scraped_data_dict['emails']
                updated_addresses = data[0]['addresses']+scraped_data_dict['addresses']
                updated_sm = data[0]['social_media_links']+scraped_data_dict['social_media_links']
                updated_tp = data[0]['telephone_numbers']+scraped_data_dict['telephone_numbers']
                updated_data_dict = {'emails':updated_emails,'social_media_links':updated_sm,'addresses':updated_addresses,'telephone_numbers':updated_tp}
                mycol.update_one({'_id': entry_id},
                                 {'$set': updated_data_dict})
                print("Successfully extended the conatact page information", entry_id)

        else:
             print("No contact page found!")
ids_list = [ ObjectId('5eb6311c86662885174692de'),ObjectId('5eb63c1e9c69232f6ed6edd8'),ObjectId('5eb63e1ee805d1cff3d80a25'),ObjectId('5eb6479687b6932b9e6de098'),ObjectId('5eb648bf6bc924ef46ab60da'),ObjectId('5eb64e13158973dfa9982019'),ObjectId('5eb65a927cb5b3a1ff4ae362'),ObjectId('5eb669883e6dc49bd6f1540f'),ObjectId('5eb66a9b90f9dd06f1107866'),ObjectId('5eb66ce4535d821544a14dee'),ObjectId('5eb66dabf3d5b58ef16a4c74'),ObjectId('5eb66e99e95b7d86f2518828'),ObjectId('5eb68405b8f3f1e1b3084a52'),ObjectId('5eb688a782ee2ac4699515f2'),ObjectId('5eb68a771a268ae85ef97960'),ObjectId('5eb68c65501e64174bede873'),ObjectId('5eb68d458e708541f4671189'),ObjectId('5eb690038f7f6e26b6253fd5'),ObjectId('5eb6918fa2e66438837c2d83'),ObjectId('5eb6944565d7b2466379f198'),ObjectId('5eb694f59c10ae1d407b7c2a'),ObjectId('5eb696f6ef36438bec383b7e'),ObjectId('5eb697cac579ca076779cb0f'),ObjectId('5eb69b6fc6cad85bd913e12a'),ObjectId('5eb6a12f7ef80a97c531cc67'),ObjectId('5eb6a21fe632eaf0b1d593db'),ObjectId('5eb6a63fc0820e4534126e94'),ObjectId('5eb6b9dbb8b6b03010c4dcc6'),ObjectId('5ed38efe1838c05e0c6fb6e4'),ObjectId('5ed3900863e5bffa1d2b4e2f'),ObjectId('5ed391925d33c4975503bb94'),ObjectId('5ed394144eb75866dfdcdc0d'),ObjectId('5ed39521d784bdc428779a0f'),ObjectId('5eb66401b0e60a643fae0467')]
# print(ids_list.index(ObjectId('5eb697cac579ca076779cb0f')))
get_cp_page_data(ids_list)
