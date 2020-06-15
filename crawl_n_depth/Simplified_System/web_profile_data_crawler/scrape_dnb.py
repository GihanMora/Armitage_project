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
    return is_valid

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
    # options.add_argument(f'user-agent={userAgent}')
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
    print(len(pageSource))
    # print(pageSource)
    soup = BeautifulSoup(pageSource, 'html.parser')#bs4

    #getting company summary
    company_contacts = []
    company_summary = []
    company_trade_name = []
    company_address = []
    company_phone = []
    company_web = []
    company_type = []
    company_revenue = []
    company_snapshot = []
    company_related_industries = []


    com_sum = soup.findAll("span",attrs={'class': 'company_summary'})
    for each_ele in com_sum:
        para = each_ele.text.replace("D&B Hoovers provides sales leads and sales intelligence data on over 120 million companies like CALTEX AUSTRALIA PETROLEUM PTY LTD around the world, including contacts, financials, and competitor information. To witness the full depth and breadth of our data and for industry leading sales intelligence tools, take D&B Hoovers for a test drive. Try D&B Hoovers Free","").strip()
        # paras = para.split("<br/><br/
        company_summary.append(para)
        # print(para)
    #getting trade_name

    t_name = soup.findAll("div", attrs={'class': 'tradeName'})
    for k in t_name:
        t_data = k.text.strip()
        company_trade_name.append(t_data)
        # print(t_data)

    #getting address

    address = soup.findAll("div", attrs={'class': 'address'})
    for element in address:
        ad_data = element.text.split()
        ad_data = " ".join(ad_data)
        company_address.append(ad_data)
        # print(ad_data)

    # getting phone numbers

    phone = soup.findAll("div", attrs={'class': 'phone'})
    for p in phone:
        p_data = p.text.strip()
        company_phone.append(p_data)
        # print(p_data)


    #getting web address

    web = soup.findAll("div", attrs={'class': 'web'})
    for w in web:
        for links in  w.findAll("a", href=True):
            # print(links['href'])
            company_web.append(links['href'])

    # getting company type

    type_r = soup.findAll("div", attrs={'class': 'type-role'})
    for r in type_r:
        r_data = r.text.strip()
        # print(r_data.replace("\n"," "))
        company_type.append(r_data.replace("\n"," "))

    # getting company revenue

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

    snap = soup.findAll("div", attrs={'class': 'company_info_body module_body'})

    for s in snap:
        for uls in s.findAll("ul"):
            for lis in uls.findAll("li"):
                company_snapshot.append("|".join(lis.text.strip().split()))
                # print(" ".join(lis.text.strip().split()))
        #     s_data = s.text.strip().replace("\n", " ")

        # print(s_data)


    related_ind = soup.findAll("li", attrs={'class': 'related_industry'})
    for ri in related_ind:
        ri_data = ri.text.strip().split("\n")
        # print("ssasas")
        # print(ri_data)
        company_related_industries.append(ri_data)


    employee_list = soup.findAll("li",attrs={'class': 'employee'})
    for element in employee_list:
        name=element.find('div',attrs={'class': 'name'}).get_text()
        job_title = element.find('div', attrs={'class': 'position sub'}).get_text()
        company_contacts.append([name,job_title])
        # print(name,job_title)
    dnb_data_dict = {}
    dnb_data_dict['link_dnb'] = comp_url
    if(len(company_trade_name)):dnb_data_dict['company_trade_name_dnb']=company_trade_name
    if (len(company_address)): dnb_data_dict['company_address_dnb'] = company_address
    if (len(company_summary)): dnb_data_dict['company_summary_dnb'] = company_summary
    if (len(company_web)): dnb_data_dict['company_web_dnb'] = company_web
    if (len(company_phone)): dnb_data_dict['company_tp_dnb'] = company_phone
    if (len(company_type)): dnb_data_dict['company_type_dnb'] = company_type
    if (len(company_related_industries)): dnb_data_dict['company_related_industries_dnb'] = company_related_industries
    if (len(company_snapshot)): dnb_data_dict['company_snapshot_dnb'] = company_snapshot
    if (len(company_revenue)): dnb_data_dict['company_revenue_dnb'] = company_revenue
    if (len(company_contacts)): dnb_data_dict['company_contacts_dnb'] = company_contacts

    for each_d in dnb_data_dict:
        print(each_d, dnb_data_dict[each_d])

    if ('company_address_dnb' in dnb_data_dict.keys()):
        if (isvalid_hq(dnb_data_dict['company_address_dnb'][0].lower())):
            return dnb_data_dict
        else:
            print("Profile seems to be incorrect!")
            return {}
    else:return dnb_data_dict


# scrape_dnb_profile('https://www.dnb.com/business-directory/company-profiles.caltex_australia_petroleum_pty_ltd.0396ff68b22e2dc4efe23c599456ed68.html')

def get_dnb_data(id_list):
    mycol = refer_collection()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        print(data)
        comp_name = data[0]['comp_name']
        print(entry_id)
        try:
            sr = getGoogleLinksForSearchText(comp_name + " dnb.com", 5, 'normal')
            if (len(sr) == 0):
                sr = getGoogleLinksForSearchText(comp_name + " dnb.com", 5, 'normal')
                if (len(sr) == 0):
                    sr = getGoogleLinksForSearchText(comp_name + " dnb.com", 5, 'normal')
            filtered_dnb = []
            print(sr)
            for p in sr:
                if 'dnb.com/business-directory/company-profiles' in p['link']:
                    filtered_dnb.append(p['link'])
            if (len(filtered_dnb)):
                dnb_link = filtered_dnb[0]
                print(dnb_link)
                data_dict_dnb = scrape_dnb_profile(dnb_link)
                # print(data_dict_dnb.keys())
                if (len(data_dict_dnb.keys())):
                    mycol.update_one({'_id': entry_id},
                                     {'$set': data_dict_dnb})
                    print("Successfully extended the data entry with dnb profile information", entry_id)
                else:
                    print("No dnb profile found! dict is empty")
            else:
                print("No dnb profile found! dict is empty")
        except IndexError:
            print("No dnb profile found!")
        except KeyError:
            print("No dnb profile found!")


edu_set = [ObjectId('5eb62e2a134cc6fb9536e93d'), ObjectId('5eb630147afe26eca4ba7bfa'), ObjectId('5eb6311c86662885174692de'), ObjectId('5eb631f1fac479799dedd1f8'), ObjectId('5eb6331597c8f5512179c4f1'), ObjectId('5eb634492802acb8c48e02aa'), ObjectId('5eb63539be65b70e5af0c7a9'), ObjectId('5eb6363894bd0b097f9c2734'), ObjectId('5eb6378b772150870b5c8d27'), ObjectId('5eb639ee2c60aae411d1ae8b'), ObjectId('5eb63aff81de1c4846fd91ab'), ObjectId('5eb63c1e9c69232f6ed6edd8'), ObjectId('5eb63d1b9d2ec0b892c42dd5'), ObjectId('5eb63e1ee805d1cff3d80a25'), ObjectId('5eb63ee743b668cb27ef8137'), ObjectId('5eb640560732058562a400b3'), ObjectId('5eb646ce3b4442b4da91c057'), ObjectId('5eb6479687b6932b9e6de098'), ObjectId('5eb648bf6bc924ef46ab60da'), ObjectId('5eb64a8e96bdd2bbbb3287e5'), ObjectId('5eb64bc810a22fecd4eca987'), ObjectId('5eb64cfc8c94747a21f39855'), ObjectId('5eb64e13158973dfa9982019'), ObjectId('5eb64f4ea0549166c51ca057'), ObjectId('5eb650acab06d680d6990351'), ObjectId('5eb651bc5fa088c453991725'), ObjectId('5eb652de55de509b4a9efaf4'), ObjectId('5eb65433af5bcc3efe32c504'), ObjectId('5eb6556c29c37695bc97bec4'), ObjectId('5eb6567909d0de1b6b708cf8'), ObjectId('5eb657e754ee9cbe1a7388c8'), ObjectId('5eb65942b46918d079adebe9'), ObjectId('5eb65a927cb5b3a1ff4ae362'), ObjectId('5eb65b645417d406270e7e63'), ObjectId('5eb65d83728ad01002b3a5f6'), ObjectId('5eb65f2cde8cab37cd68dffd'), ObjectId('5eb6603b6e69c6f2e1092cf8'), ObjectId('5eb661a6796445df9bfd756d'), ObjectId('5eb6631b245b7e033d0f92ed'), ObjectId('5eb66401b0e60a643fae0467'), ObjectId('5eb6651284c93e9e1b685024'), ObjectId('5eb66682dc99a524418da337'), ObjectId('5eb667a554cc6bc47dbfea44'), ObjectId('5eb6688cf9acda3a876322e4'), ObjectId('5eb669883e6dc49bd6f1540f'), ObjectId('5eb66a9b90f9dd06f1107866'), ObjectId('5eb66bb449a0728d932475bc'), ObjectId('5eb66ce4535d821544a14dee'), ObjectId('5eb66dabf3d5b58ef16a4c74'), ObjectId('5eb66e99e95b7d86f2518828'), ObjectId('5eb66fa738555190120005d2'), ObjectId('5eb670c2382a70cea3c90149'), ObjectId('5eb672382cf60f5b673dc845'), ObjectId('5eb6734f61272a1489607d7c'), ObjectId('5eb6746b3f8078c646a32068'), ObjectId('5eb675384beae11731a0ce35'), ObjectId('5eb676209d0d155a1c6530f3'), ObjectId('5eb6777b140e783b3524f4d9'), ObjectId('5eb6783b3dd775bea489b02d'), ObjectId('5eb67952c38498d75c86627f'), ObjectId('5eb67a4c109ddab70aec7b2d'), ObjectId('5eb67bc12373d9a910e8750f'), ObjectId('5eb67d3dd9818bcd44884d39'), ObjectId('5eb67e66b7921dcf1c2e6805'), ObjectId('5eb67fa821374c1c36ea76bb'), ObjectId('5eb680d98c70c48229cd26b6'), ObjectId('5eb6820dcc1fecfea5009f48'), ObjectId('5eb682ecd810c81378eb806d'), ObjectId('5eb68405b8f3f1e1b3084a52'), ObjectId('5eb6853a626f824ef428e315'), ObjectId('5eb688a782ee2ac4699515f2'), ObjectId('5eb689814e048265dd507dbc'), ObjectId('5eb68a771a268ae85ef97960'), ObjectId('5eb68b52298db2bd4cebdd0e'), ObjectId('5eb68c65501e64174bede873'), ObjectId('5eb68d458e708541f4671189'), ObjectId('5eb68e2fab2ce0451e2b4056'), ObjectId('5eb68edce0b5b75b05fba1e6'), ObjectId('5eb690038f7f6e26b6253fd5'), ObjectId('5eb690bd8d99ac316303ffb6'), ObjectId('5eb6918fa2e66438837c2d83'), ObjectId('5eb6925a31a5f94e1207b916'), ObjectId('5eb6944565d7b2466379f198'), ObjectId('5eb694f59c10ae1d407b7c2a'), ObjectId('5eb695e1ffe996bbe09292fe'), ObjectId('5eb696f6ef36438bec383b7e'), ObjectId('5eb697cac579ca076779cb0f'), ObjectId('5eb698a46de98c90f95a497d'), ObjectId('5eb699a671806057e76f0141'), ObjectId('5eb69a7d5587c492135fd56c'), ObjectId('5eb69b6fc6cad85bd913e12a'), ObjectId('5eb69c52d1ecab806f2beead'), ObjectId('5eb69cefc81bdf1aac4bf6a1'), ObjectId('5eb69e087e9ea4385e20beed'), ObjectId('5eb69f48a04ce33b509b4895'), ObjectId('5eb6a058cd265d6ef2ee766f'), ObjectId('5eb6a12f7ef80a97c531cc67'), ObjectId('5eb6a21fe632eaf0b1d593db'), ObjectId('5eb6a63fc0820e4534126e94'), ObjectId('5eb6a72dfc5d1c47d4ca9cd1'), ObjectId('5eb6a8462d272649f7b4df95'), ObjectId('5eb6a930b440ebf60d42d6c2'), ObjectId('5eb6aa15b5b4db2c7393254c'), ObjectId('5eb6ab260aef4a583d77118f'), ObjectId('5eb6ac1bfff106a6f58c42e7'), ObjectId('5eb6ad1662db4e6c180a378b'), ObjectId('5eb6ae390bdb0b194f41f9b3'), ObjectId('5eb6af2a6012ca09c1728130'), ObjectId('5eb6afc4e15b344d1a3aafa0'), ObjectId('5eb6b19b1c6e630676c62445'), ObjectId('5eb6b2a5a9211572420260e9'), ObjectId('5eb6b38eeb5e21b75a0d7cdb'), ObjectId('5eb6b45f4dab807be8d7a28a'), ObjectId('5eb6b53fd8471918b43146b7'), ObjectId('5eb6b61fabf00d5fdb2d05a3'), ObjectId('5eb6b71e5cd9b7b54c7d9961'), ObjectId('5eb6b9158f232307ce0bdc13'), ObjectId('5eb6b9dbb8b6b03010c4dcc6'), ObjectId('5eb6bad32c05d6f34cf32652'), ObjectId('5eb6bbbee2f17c3f3238cec8'), ObjectId('5eb6bca1b68e7672cd0ef210'), ObjectId('5eb6bdb1e7b6cc4614eb0edb'), ObjectId('5eb6beca47492aa1e0553de4'), ObjectId('5eb6bfc707fd60d7d77844de'), ObjectId('5ed3846f023b726e6d17d4f0'), ObjectId('5ed38b25d439f58cc06e5825'), ObjectId('5ed38d5420653aee6e3220c8'), ObjectId('5ed38efe1838c05e0c6fb6e4'), ObjectId('5ed3900863e5bffa1d2b4e2f'), ObjectId('5ed391925d33c4975503bb94'), ObjectId('5ed394144eb75866dfdcdc0d'), ObjectId('5ed39521d784bdc428779a0f'), ObjectId('5ed3966ae5903d41b23471ba'), ObjectId('5ed3980c016ddd49b0f4c304'), ObjectId('5ed3996045e3020d63762dce'), ObjectId('5ed39b1195eba19024e714bf'), ObjectId('5ed39d3781f6df0d82e6bfda'), ObjectId('5ed39f30fc1a9fd5e77e332f'), ObjectId('5ed3a07a5dbe3d7cdbc0a11f'), ObjectId('5ed3a21a7deae88594ebebcb'), ObjectId('5ed3a430b15357da758e9aaf'), ObjectId('5ed3a65cc612795088fb19b8'), ObjectId('5ed3a8655fa4a60f979e1f88'), ObjectId('5ed3aaa7285d71b28cc6d49b'), ObjectId('5ed3ac8b4daab633d19b58d8'), ObjectId('5ed3add3461496c2716f7235'), ObjectId('5ed3af522f225fd825bf711a'), ObjectId('5ed3b088624645fcbe0374c5'), ObjectId('5ed3b2383758cc50c8bdd137'), ObjectId('5ed3b766a882d958e63eb52e')]
edu_left = [ObjectId('5ed3846f023b726e6d17d4f0'), ObjectId('5ed38b25d439f58cc06e5825'), ObjectId('5ed38d5420653aee6e3220c8'), ObjectId('5ed38efe1838c05e0c6fb6e4'), ObjectId('5ed3900863e5bffa1d2b4e2f'), ObjectId('5ed391925d33c4975503bb94'), ObjectId('5ed394144eb75866dfdcdc0d'), ObjectId('5ed39521d784bdc428779a0f'), ObjectId('5ed3966ae5903d41b23471ba'), ObjectId('5ed3980c016ddd49b0f4c304'), ObjectId('5ed3996045e3020d63762dce'), ObjectId('5ed39b1195eba19024e714bf'), ObjectId('5ed39d3781f6df0d82e6bfda'), ObjectId('5ed39f30fc1a9fd5e77e332f'), ObjectId('5ed3a07a5dbe3d7cdbc0a11f'), ObjectId('5ed3a21a7deae88594ebebcb'), ObjectId('5ed3a430b15357da758e9aaf'), ObjectId('5ed3a65cc612795088fb19b8'), ObjectId('5ed3a8655fa4a60f979e1f88'), ObjectId('5ed3aaa7285d71b28cc6d49b'), ObjectId('5ed3ac8b4daab633d19b58d8'), ObjectId('5ed3add3461496c2716f7235'), ObjectId('5ed3af522f225fd825bf711a'), ObjectId('5ed3b088624645fcbe0374c5'), ObjectId('5ed3b2383758cc50c8bdd137'), ObjectId('5ed3b766a882d958e63eb52e')]
# print(edu_set.index(ObjectId('5eb6bbbee2f17c3f3238cec8')))
# print(edu_set.index(ObjectId('5eb6bbbee2f17c3f3238cec8')))
# get_dnb_data(edu_set[120:])
to_fix_edu = [ObjectId('5eb64cfc8c94747a21f39855'),ObjectId('5eb6b61fabf00d5fdb2d05a3'),ObjectId('5eb6b71e5cd9b7b54c7d9961'),ObjectId('5eb6b9158f232307ce0bdc13'),ObjectId('5eb6b9dbb8b6b03010c4dcc6'),ObjectId('5eb6bbbee2f17c3f3238cec8'),ObjectId('5eb6bca1b68e7672cd0ef210'),ObjectId('5eb6bdb1e7b6cc4614eb0edb'),ObjectId('5eb6beca47492aa1e0553de4'),ObjectId('5eb6bfc707fd60d7d77844de')]
get_dnb_data(to_fix_edu)