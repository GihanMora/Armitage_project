#update sys path if you want to run this seperately
#check chrome driver exeecutable path
import time
import sys

from Simplified_System.Database.db_connect import refer_collection

sys.path.insert(0, 'F:/Armitage_project/')
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

# from crawl_n_depth.get_n_search_results import getGoogleLinksForSearchText
from selenium.webdriver.support.wait import WebDriverWait
def proxy_generator():
    response = requests.get("https://sslproxies.org/")
    soup = BeautifulSoup(response.content, 'html5lib')
    proxy = {'https': choice(list(map(lambda x:x[0]+':'+x[1], list(zip(map(lambda x:x.text,
	   soup.findAll('td')[::8]), map(lambda x:x.text, soup.findAll('td')[1::8]))))))}
    return proxy

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

def scrape_opencorporates(comp_url):

    browser = get_browser()
    browser.set_page_load_timeout(30)
    try:
        browser.get(comp_url)
        time.sleep(5)
        pageSource = browser.page_source
    except TimeoutException:
        print("browser timeout")
        return []

    browser.quit()
    # browser.close()
    # print(pageSource)
    results=[]
    soup = BeautifulSoup(pageSource, 'html.parser')#bs4
    employee_list = soup.findAll("dd",attrs={'class': 'officers trunc8'})
    for element in employee_list:
        emp_set = element.findAll('li',attrs={'class': 'attribute_item'})
        for each in emp_set:
            if each.find('a', attrs={'class': 'officer inactive'}):
                results.append([each.get_text(),"inactive"])
                # print(each.get_text(),"inactive")
            else:
                results.append([each.get_text(), "active"])
                # print(each.get_text(), "active")


    return results
def scrape_dnb(comp_url):

    browser1 = get_browser()
    # print('check1')
    browser1.set_page_load_timeout(30)
    try:
        browser1.get(comp_url)
        time.sleep(5)
        pageSource = browser1.page_source
    except TimeoutException:
        print("browser timeout")
        return []
    # print('check2')
    # time.sleep(10)
    # wait = WebDriverWait(browser, 10)

    browser1.quit()
    results = []
    # browser.close()
    print(len(pageSource))
    # print(pageSource)
    soup = BeautifulSoup(pageSource, 'html.parser')#bs4
    employee_list = soup.findAll("li",attrs={'class': 'employee'})
    for element in employee_list:
        name=element.find('div',attrs={'class': 'name'}).get_text()
        job_title = element.find('div', attrs={'class': 'position sub'}).get_text()
        results.append([name,job_title])
        # print(name,job_title)


    print(results)
    return results

#how to run seperately

# dnb_url = "https://www.dnb.com/business-directory/company-profiles.gocup_pastoral_pty_ltd.ed6b8f7e3cf23e0a13cb05d2fe1f0d80.html"
# print(scrape_dnb(dnb_url))
# opencorporates_url = "https://opencorporates.com/companies/gb/SC394839"
# print(scrape_opencorporates(opencorporates_url))


# comps_l=['TOOHEYS PTY LIMITED','CALTEX PETROLEUM PTY LTD','PIONEER STEEL PTY LTD','SYDNEY NIGHT PATROL & INQUIRY CO PTY LTD'
# ,'MIRROR NEWSPAPERS PTY LIMITED','BJELKE-PETERSEN BROS PTY LTD','A.C.N. 000 018 342 PTY LIMITED','H.F. LAMPE INVESTMENTS PTY.'
# ,'FOREST COACH LINES PTY LTD','DABEE PTY LTD','PLATYPUS LEATHER INDUSTRIES PTY LTD','J & M MFG PTY LTD','DAVID DONALDSON PTY LTD'
# ,'PIONEER QUARRIES (SYDNEY) PTY LTD','DIWING PTY LTD','ASHCROFT FREEHOLDS PTY LTD','JAC AND JACK PTY LTD','TAHA WAGERING SYSTEMS PTY LTD'
# ,'BRADFORD INSULATION INDUSTRIES PTY. LIMITED','GOCUP PASTORAL PTY LTD']

def get_cp_oc(entry_id,mode):
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    # mydb = myclient["CompanyDatabase"]  # refer the database
    # mycol = mydb["comp_data"]  # refer the collection
    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    # comp_name = data[0]['search_text']
    try:
        if mode=='comp':
            comp_name = data[0]['search_text']
        elif mode == 'query':
            comp_name = data[0]['comp_name']
    except KeyError:
        comp_name = data[0]['link'].split("/")[2]

    det=[comp_name]
    sr = getGoogleLinksForSearchText(comp_name + " opencorporates", 3, 'normal')

    filtered_oc = []
    for p in sr:
        if (('opencorporates.com/companies/nz' in p['link']) or ('opencorporates.com/companies/au' in p['link'])):
            filtered_oc.append([p['title'], p['link']])
    if (len(filtered_oc)):
        print(filtered_oc[0])
        det.append(filtered_oc[0])
        det.append(scrape_opencorporates(filtered_oc[0][1]))
        print(det)
        mycol.update_one({'_id': entry_id},
                         {'$set': {'oc_cp_info': det}})
        print("Successfully extended the data entry with opencorporates contact person data", entry_id)
    else:
        print("No opencorporates profile found!, Try again")
        mycol.update_one({'_id': entry_id},
                         {'$set': {'oc_cp_info': det}})


def get_cp_dnb(entry_id,mode):
    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    # print(comp_data_entry)
    data = [i for i in comp_data_entry]
    # comp_name = data[0]['search_text']
    # print(data)
    try:
        if mode=='comp':
            comp_name = data[0]['search_text']
        elif mode == 'query':
            print(data)
            comp_name = data[0]['comp_name']
    except KeyError:
        comp_name = data[0]['link'].split("/")[2]
    det = [comp_name]
    sr = getGoogleLinksForSearchText(comp_name + " dnb.com", 3, 'normal')
    filtered_dnb = []
    for p in sr:
        if 'dnb.com/business-directory/company-profiles' in p['link']:
            filtered_dnb.append([p['title'], p['link']])
    if (len(filtered_dnb)):
        print("dnb profile found and extracting contact persons..")
        print(filtered_dnb[0])
        det.append(filtered_dnb[0])
        print(filtered_dnb[0][1])
        det.append(scrape_dnb(filtered_dnb[0][1]))
        print(det)
        mycol.update_one({'_id': entry_id},
                         {'$set': {'dnb_cp_info': det}})
        print("Successfully extended the data entry with dnb contact person data", entry_id)
    else:
        print("No dnb profile found!,Try again..")
        print(det)
        mycol.update_one({'_id': entry_id},
                         {'$set': {'dnb_cp_info': det}})

