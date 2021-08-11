#fix sys path if you want to run this script individually
#check chrome driver exeecutable path
import time
import sys

from bson import ObjectId

sys.path.insert(0, 'F:/Armitage_project_v1/crawl_n_depth/')
from Simplified_System.Database.db_connect import refer_collection


import pymongo
from selenium.common.exceptions import TimeoutException
import requests
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
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
    # PROXY = proxy_generator()
    # PROXY = {'https': '123.231.86.102'}
    # print(PROXY)
    userAgent = ua.random #get a random user agent
    # userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    options = webdriver.ChromeOptions()  # use headless version of chrome to avoid getting blocked
    # options.add_argument('headless')
    # options.add_argument(f'user-agent={userAgent}')
    options.add_argument("user-data-dir=C:\\myuserdata")
    # options.add_argument("start-maximized")# // open Browser in maximized mode
    # options.add_argument("disable-infobars")# // disabling infobars
    # options.add_argument("--disable-extensions")# // disabling extensions
    # options.add_argument("--disable-gpu")# // applicable to windows os only
    # options.add_argument("--disable-dev-shm-usage")# // overcome limited resource problems
    # options.add_argument('--proxy-server=%s' % PROXY['https'])
    # options.add_argument("--incognito")
    browser = webdriver.Chrome(chrome_options=options,  # give the path to selenium executable
                                   # executable_path='F://Armitage_lead_generation_project//chromedriver.exe'
                                   executable_path='F://Armitage_project_v1//crawl_n_depth//utilities//chromedriver.exe',
                                    service_args=["--verbose", "--log-path=D:\\qc1.log"]
                                   )
    return browser

def isvalid_hq(loc):
    is_valid = False
    check_list_a = ['VIC', 'NSW', 'ACT', 'QLD', 'NT', 'SA', 'TAS', 'WA', 'AU', 'NZ', 'AUS']
    check_list_b = ['new south wales', 'victoria', 'queensland', 'western australia', 'south australia', 'tasmania',
                    'northland', 'auckland', 'waikato', 'bay of plenty', 'gisborne', "hawkes bay", 'taranaki',
                    'manawatu-whanganui', 'wellington', 'tasman', 'nelson', 'marlborough', 'west coast', 'canterbury',
                    'otago', 'southland', 'australia',
                    'new zealand', 'newzealand']
    for c_c in check_list_a:
        if c_c == 'SA':
            if (((c_c in loc) and ('USA' not in loc))):
                # print(((c_c in hq_li) and ('USA' not in hq_li)),((c_c in j_oc) and ('USA' not in j_oc)),((c_c in hq_g) and ('USA' not in hq_g)))
                is_valid = True
        else:
            if ((c_c in loc)):
                is_valid = True

    for c_i in check_list_b:
        if ((c_i in loc.lower())):
            is_valid = True
    if('united states' in loc.lower()):
        is_valid = False
    return is_valid


def get_li_url(entry_id):

    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    attribute_keys = list(data[0].keys())
    try:
        sm_links = data[0]['social_media_links']
    except Exception:
        sm_links = []
    linked_in_comp_urls = []
    for each in sm_links:
        if('linkedin.com/company' in each):linked_in_comp_urls.append(each)
    if(len(linked_in_comp_urls)):
        print("Linkedin profile collected from crawled data")
        print("linkedin taken from crawling")
        return linked_in_comp_urls[0]
    elif ('LinkedIn_cb' in attribute_keys):
        print("Linkedin profile collected from crunchbase")
        return data[0]['LinkedIn_cb']
    else:
        comp_name = data[0]['comp_name']
        print(data[0]['comp_name'])
        sr = getGoogleLinksForSearchText('"' + comp_name + '"' + " linkedin company australia", 5, 'normal')
        filtered_li = []
        for p in sr:
            # print(p['link'])
            if 'linkedin.com/company' in p['link']:
                filtered_li.append(p['link'])
        if (len(filtered_li)):
            return filtered_li[0]
        else:
            print("No linkedin contacts found!, Try again")
            return False


# headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0" , "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
#
# response = requests.get('https://www.linkedin.com/company/armitage-associates-pty-ltd', headers=headers)
# soup = BeautifulSoup(response.text, 'html.parser')#bs4

def scrape_li_ano(url):
    browser = get_browser()
    browser.get(url)
    pageSource = browser.page_source
    print(len(pageSource))
    # browser.quit()
    soup = BeautifulSoup(pageSource, 'html.parser')  # bs4

    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0",
    #            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    #            "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1",
    #            "Connection": "close", "Upgrade-Insecure-Requests": "1"}
    #
    # response = requests.get(url, headers=headers)
    # soup = BeautifulSoup(response.text, 'html.parser')  # bs4
    # print(len(response.text))
    # print(response.text)
    linkedin_data_list = {}

    com_sum = soup.findAll("p",attrs={'class': 'about-us__description'})

    for each_ele in com_sum:
        texts = [text.strip().replace("\n", " ") for text in each_ele.find_all(text=True)]
        texts = [text for text in texts if text]
        # print('description_li',(" ").join(texts))
        linkedin_data_list['description_li'] = (" ").join(texts)
        # print(each_ele.get_text())

    basic_info = soup.findAll("dl",attrs={'class': 'about-us__basic-info-list'})
    for each_bil in basic_info:
        all_bi = each_bil.findAll("div",attrs={'class':'basic-info-item'})
        for each_bi in all_bi:
            term_bi = each_bi.find("dt",attrs={'class':'basic-info-item__term'}).get_text()
            des_bi = each_bi.find("dd",attrs={'class':'basic-info-item__description'}).get_text()
            if(term_bi=='Website'):linkedin_data_list['website_li']=des_bi
            if (term_bi == 'Industries'):linkedin_data_list['industry_li']=des_bi
            if (term_bi == 'Company size'):linkedin_data_list['company_size_li']=des_bi
            if (term_bi == 'Headquarters'):linkedin_data_list['headquarters_li']=des_bi
            if (term_bi == 'Type'):linkedin_data_list['type_li']=des_bi
            if (term_bi == 'Founded'):linkedin_data_list['founded_li']=des_bi
            if (term_bi == 'Specialties'):linkedin_data_list['specialties_li']=des_bi



    location_info = soup.findAll("section",attrs={'class': 'locations section-container'})
    for each_lo in location_info:
        l_items = each_lo.findAll("ul", attrs={'class':'show-more-less__list show-more-less__list--no-hidden-elems'})
        for i,each_li in enumerate(l_items):
            locs = each_li.findAll("p", attrs={'class': 'locations__address-line'})
            # t_tags = each_li.findAll(text=True)
            # texts = [text.strip().replace("\n", " ") for text in each_li.find_all(text=True)]
            # texts = [text for text in texts if text]
            # print('cc',texts)
            add_lines = []
            for i,each_add in enumerate(locs):
                # print(each_add)
                locations = each_add.get_text()
                add_lines.append(locations)
            linkedin_data_list['location_li_'+str(i)]=(" ").join(add_lines)

    employee_list = []
    emp_info = soup.findAll("section",attrs={'class': 'employees-at section-container'})
    for each_em in emp_info:
        e_items = each_em.findAll("ul", attrs={'class':'employees__list'})
        for each_emp in e_items:

            emps = each_emp.findAll("li", attrs={'class': 'result-card profile-result-card'})
            for i,each_em_li in enumerate(emps):
                emp_name = each_em_li.find("h3",attrs={'class':'result-card__title profile-result-card__title'}).get_text()
                emp_role = each_em_li.find("h4", attrs={'class': 'result-card__subtitle profile-result-card__subtitle'}).get_text()
                employee_list.append([emp_name,emp_role])

    if(len(employee_list)):
        linkedin_data_list['contacts_li']=employee_list
    if(len(linkedin_data_list.keys())):
        linkedin_data_list['url_li']=url
    print(linkedin_data_list)

    #validation
    if('headquarters_li' in linkedin_data_list.keys()):
        if(isvalid_hq(linkedin_data_list['headquarters_li'])):
            return linkedin_data_list
        else:return {}
    if ('location_li_0' in linkedin_data_list.keys()):
        if (isvalid_hq(linkedin_data_list['location_li_0'])):
            return linkedin_data_list
        else:
            return {}



    return linkedin_data_list
#     para = each_ele.text.replace("D&B Hoovers provides sales leads and sales intelligence data on over 120 million companies like CALTEX AUSTRALIA PETROLEUM PTY LTD around the world, including contacts, financials, and competitor information. To witness the full depth and breadth of our data and for industry leading sales intelligence tools, take D&B Hoovers for a test drive. Try D&B Hoovers Free","").strip()
#      # paras = para.split("<br/><br/
#

def get_li_data_ano(id_list):
    mycol = refer_collection()
    for entry_id in id_list:
        # time.sleep(120)
        print(entry_id)
        li_url = get_li_url(entry_id)
        if(li_url):
            print(li_url)
            # blockPrint()
            comp_li_data = scrape_li_ano(li_url)
            # enablePrint()
            # print(comp_li_data)
            corrected_dict = comp_li_data
            # for k in corrected_dict:
            #     print("'"+str(k)+"'")
            # print(corrected_dict)
            if (len(corrected_dict.keys())):
                mycol.update_one({'_id': entry_id},
                                 {'$set': corrected_dict})
                print("Successfully extended the data entry with linkedin profile information", entry_id)
            else:
                print("No linkedin profile found! dict is empty")
# scrape_li_ano('https://au.linkedin.com/company/2and2')
to_li = [ObjectId('5ed3846f023b726e6d17d4f0'), ObjectId('5ed38b25d439f58cc06e5825'), ObjectId('5ed38d5420653aee6e3220c8'), ObjectId('5ed38efe1838c05e0c6fb6e4'), ObjectId('5ed3900863e5bffa1d2b4e2f'), ObjectId('5ed391925d33c4975503bb94'), ObjectId('5ed394144eb75866dfdcdc0d'), ObjectId('5ed39521d784bdc428779a0f'), ObjectId('5ed3966ae5903d41b23471ba'), ObjectId('5ed3980c016ddd49b0f4c304'), ObjectId('5ed3996045e3020d63762dce'), ObjectId('5ed39b1195eba19024e714bf'), ObjectId('5ed39d3781f6df0d82e6bfda'), ObjectId('5ed39f30fc1a9fd5e77e332f'), ObjectId('5ed3a07a5dbe3d7cdbc0a11f'), ObjectId('5ed3a21a7deae88594ebebcb'), ObjectId('5ed3a430b15357da758e9aaf'), ObjectId('5ed3a65cc612795088fb19b8'), ObjectId('5ed3a8655fa4a60f979e1f88'), ObjectId('5ed3aaa7285d71b28cc6d49b'), ObjectId('5ed3ac8b4daab633d19b58d8'), ObjectId('5ed3add3461496c2716f7235'), ObjectId('5ed3af522f225fd825bf711a'), ObjectId('5ed3b088624645fcbe0374c5'), ObjectId('5ed3b2383758cc50c8bdd137'), ObjectId('5ed3b766a882d958e63eb52e')]
edu_left = [ObjectId('5ed3846f023b726e6d17d4f0'), ObjectId('5ed38b25d439f58cc06e5825'), ObjectId('5ed38d5420653aee6e3220c8'), ObjectId('5ed38efe1838c05e0c6fb6e4'), ObjectId('5ed3900863e5bffa1d2b4e2f'), ObjectId('5ed391925d33c4975503bb94'), ObjectId('5ed394144eb75866dfdcdc0d'), ObjectId('5ed39521d784bdc428779a0f'), ObjectId('5ed3966ae5903d41b23471ba'), ObjectId('5ed3980c016ddd49b0f4c304'), ObjectId('5ed3996045e3020d63762dce'), ObjectId('5ed39b1195eba19024e714bf'), ObjectId('5ed39d3781f6df0d82e6bfda'), ObjectId('5ed39f30fc1a9fd5e77e332f'), ObjectId('5ed3a07a5dbe3d7cdbc0a11f'), ObjectId('5ed3a21a7deae88594ebebcb'), ObjectId('5ed3a430b15357da758e9aaf'), ObjectId('5ed3a65cc612795088fb19b8'), ObjectId('5ed3a8655fa4a60f979e1f88'), ObjectId('5ed3aaa7285d71b28cc6d49b'), ObjectId('5ed3ac8b4daab633d19b58d8'), ObjectId('5ed3add3461496c2716f7235'), ObjectId('5ed3af522f225fd825bf711a'), ObjectId('5ed3b088624645fcbe0374c5'), ObjectId('5ed3b2383758cc50c8bdd137'), ObjectId('5ed3b766a882d958e63eb52e')]
# get_li_data_ano(edu_left[2:])
# print(to_li.index(ObjectId('5ed3996045e3020d63762dce')))
# for k in edu_left:
#     print(k)
#     get_li_data_ano([k])
#     time.sleep(200)