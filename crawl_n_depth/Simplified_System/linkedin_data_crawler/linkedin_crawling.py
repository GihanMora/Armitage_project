# pip install git+git://github.com/austinoboyle/scrape-linkedin-selenium.git
#chrome driver should contain in the folder
#fix sys path if you want to run this script individually
#replace linkedin live cookie value
# sudo apt install chromium-chromedriver incase of need
import sys, os


sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')

from Simplified_System.Initial_Crawling.get_n_search_results import getGoogleLinksForSearchText
from Simplified_System.Database.db_connect import refer_collection
from scrape_linkedin import ProfileScraper,HEADLESS_OPTIONS
from scrape_linkedin import CompanyScraper


from bson import ObjectId
# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


def scrape_person(url):
    user_name = url.split('in/')[1]
    user_name = user_name.split('/')[0]
    print(user_name)
    # scrape a person
    with ProfileScraper(driver_options=HEADLESS_OPTIONS,cookie='AQEDATCqAAsEnwLsAAABceUL55UAAAFyCRhrlVYAHF3D2I07SBdYzkXulfZyZSL6M5Y_Ap17KE5qIXPGP5MiebSzuJFFIiQNI6Gj3LREGMgwtZdTtQk09LHenXAOIC9zEkedjhbHxoZDGC2ejC0MfNwS') as scraper:
        profile = scraper.scrape(user=user_name)
    print(profile.to_dict())

# scrape_person('https://www.linkedin.com/in/gihangamage2015/')

def scrape_company(url):
    try:
        user_name = url.split('company/')[1]
        user_name = user_name.split('/')[0]
        # scrape a company
        with CompanyScraper( cookie='AQEDASFhktAB1cT_AAABbKA6VksAAAFysxri4VEAxZ7LEdUO8ZBWU7YYCzNzMSJ7J3E_bNHW-Tzf1_Jn1dH12XrTApiHesI2FoNy6M_CLj5rb7lqD-nbH_IsywW6cPBcBfGnVCd_XW3vjteLW9L6iCZO') as scraper:
            company = scraper.scrape(company=user_name)
        blockPrint()
        try:
            comp_overview = company.overview
        except Exception:
            comp_overview = {}
        enablePrint()
        print("******Linkedin crawling results******")
        # print(comp_overview)
        # for each_key in comp_overview:
        #     data_c = comp_overview[each_key]
        #     if(type(data_c)==str): data_c.replace('\n\n', '\n')
        #     print(each_key + " : ", data_c)

        # print(company.overview)
        return comp_overview
    except Exception:
        return {}



#
# def get_li_data(url):
#     blockPrint()
#     comp_overview = scrape_company(url)
#     enablePrint()
#     print("******Linkedin crawling results******")
#     for each_key in comp_overview:
#         print(each_key+" : ",comp_overview[each_key].replace('\n\n','\n'))


# scrape_company('https://www.linkedin.com/company/armitage-associates-pty-ltd/')



def get_li_url(entry_id):

    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
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
    else:
        comp_name = data[0]['comp_name']
        print(data[0]['comp_name'])
        sr = getGoogleLinksForSearchText('"' + comp_name + '"' + " linkedin australia or newzealand", 5, 'normal')
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


def get_li_data(id_list):
    mycol = refer_collection()
    for entry_id in id_list:
        li_url = get_li_url(entry_id)
        if(li_url):
            print(li_url)
            # blockPrint()
            comp_li_data = scrape_company(li_url)
            # enablePrint()
            # print(comp_li_data)
            corrected_dict = {k+'_li': v for k, v in comp_li_data.items()}
            # for k in corrected_dict:
            #     print("'"+str(k)+"'")
            # print(corrected_dict)
            if (len(corrected_dict.keys())):
                mycol.update_one({'_id': entry_id},
                                 {'$set': corrected_dict})
                print("Successfully extended the data entry with linkedin profile information", entry_id)
            else:
                print("No linkedin profile found! dict is empty")
        # else:
        #     print()
            # mycol.update_one({'_id': entry_id},
            #                  {'$set': {'linkedin_cp_info': []}})

# get_li_data([ObjectId('5eb6b53fd8471918b43146b7')])