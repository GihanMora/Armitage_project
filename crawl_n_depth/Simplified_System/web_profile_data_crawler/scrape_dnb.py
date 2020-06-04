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

def scrape_dnb_profile(comp_url):
    browser = get_browser()
    print('check1')
    browser.set_page_load_timeout(30)
    try:
        browser.get(comp_url)
        time.sleep(5)
        pageSource = browser.page_source
    except TimeoutException:
        print("browser timeout")
        return {}
    print('check2')
    # time.sleep(10)
    # wait = WebDriverWait(browser, 10)

    browser.quit()
    # browser.close()
    # print(len(pageSource))
    # print(pageSource)
    soup = BeautifulSoup(pageSource, 'html.parser')#bs4

    #getting company summary
    company_summary = []
    com_sum = soup.findAll("span",attrs={'class': 'company_summary'})
    for each_ele in com_sum:
        para = each_ele.text.replace("D&B Hoovers provides sales leads and sales intelligence data on over 120 million companies like CALTEX AUSTRALIA PETROLEUM PTY LTD around the world, including contacts, financials, and competitor information. To witness the full depth and breadth of our data and for industry leading sales intelligence tools, take D&B Hoovers for a test drive. Try D&B Hoovers Free","").strip()
        # paras = para.split("<br/><br/
        company_summary.append(para)
        # print(para)
    #getting trade_name
    company_trade_name = []
    t_name = soup.findAll("div", attrs={'class': 'tradeName'})
    for k in t_name:
        t_data = k.text.strip()
        company_trade_name.append(t_data)
        # print(t_data)

    #getting address
    company_address = []
    address = soup.findAll("div", attrs={'class': 'address'})
    for element in address:
        ad_data = element.text.split()
        ad_data = " ".join(ad_data)
        company_address.append(ad_data)
        # print(ad_data)

    # getting phone numbers
    company_phone=[]
    phone = soup.findAll("div", attrs={'class': 'phone'})
    for p in phone:
        p_data = p.text.strip()
        company_phone.append(p_data)
        # print(p_data)


    #getting web address
    company_web = []
    web = soup.findAll("div", attrs={'class': 'web'})
    for w in web:
        for links in  w.findAll("a", href=True):
            # print(links['href'])
            company_web.append(links['href'])

    # getting company type
    company_type = []
    type_r = soup.findAll("div", attrs={'class': 'type-role'})
    for r in type_r:
        r_data = r.text.strip()
        # print(r_data.replace("\n"," "))
        company_type.append(r_data.replace("\n"," "))

    # getting company revenue
    company_revenue = []
    rev_f = soup.findAll("div", attrs={'class': 'rev_title'})
    for rf in rev_f:
        all_divs = [rf] + rf.find_next_siblings('div')
        all_d = []
        for each_d in all_divs:
            rf_data = each_d.text.strip()
            all_d.append(rf_data.replace("\n", " "))
        company_revenue.append("|".join(all_d))
        # print("|".join(all_d))

    # getting company snapshot
    company_snapshot=[]
    snap = soup.findAll("div", attrs={'class': 'company_info_body module_body'})

    for s in snap:
        for uls in s.findAll("ul"):
            for lis in uls.findAll("li"):
                company_snapshot.append("|".join(lis.text.strip().split()))
                # print(" ".join(lis.text.strip().split()))
        #     s_data = s.text.strip().replace("\n", " ")

        # print(s_data)

    company_related_industries = []
    related_ind = soup.findAll("li", attrs={'class': 'related_industry'})
    for ri in related_ind:
        ri_data = ri.text.strip().split("\n")
        # print("ssasas")
        # print(ri_data)
        company_related_industries.append(ri_data)





    company_contacts = []
    employee_list = soup.findAll("li",attrs={'class': 'employee'})
    for element in employee_list:
        name=element.find('div',attrs={'class': 'name'}).get_text()
        job_title = element.find('div', attrs={'class': 'position sub'}).get_text()
        company_contacts.append([name,job_title])
        # print(name,job_title)

    dnb_data_dict = {'company_trade_name_dnb':company_trade_name,'company_address_dnb':company_address,'company_summary_dnb':company_summary,
                     'company_web_dnb':company_web, 'company_tp_dnb':company_phone,'company_type_dnb':company_type,'company_related_industries_dnb':company_related_industries,
                     'company_snapshot_dnb':company_snapshot,'company_revenue_dnb':company_revenue, 'company_contacts_dnb':company_contacts}

    for each_d in dnb_data_dict:
        print(each_d, dnb_data_dict[each_d])
    return dnb_data_dict


# scrape_dnb_profile('https://www.dnb.com/business-directory/company-profiles.caltex_australia_petroleum_pty_ltd.0396ff68b22e2dc4efe23c599456ed68.html')

def get_dnb_data(id_list):
    mycol = refer_collection()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        try:
            dnb_link = data[0]['dnb_cp_info'][1][1]
            print(dnb_link)
            data_dict_dnb = scrape_dnb_profile(dnb_link)
            # print(data_dict_dnb.keys())
            if (len(data_dict_dnb.keys())):
                mycol.update_one({'_id': entry_id},
                                 {'$set': data_dict_dnb})
                print("Successfully extended the data entry with dnb profile information", entry_id)
            else:
                print("No dnb profile found! dict is empty")
        except IndexError:
            print("No dnb profile found!")
        except KeyError:
            print("No dnb profile found!")

# get_dnb_data([ObjectId('5eb1573403cb37de03af8369')])