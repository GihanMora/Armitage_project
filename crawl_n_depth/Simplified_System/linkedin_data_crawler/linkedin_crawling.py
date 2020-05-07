# pip install git+git://github.com/austinoboyle/scrape-linkedin-selenium.git
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
    user_name = url.split('company/')[1]
    user_name = user_name.split('/')[0]
    # scrape a company
    with CompanyScraper(driver_options=HEADLESS_OPTIONS, cookie='AQEDATCqAAsEnwLsAAABceUL55UAAAFyCRhrlVYAHF3D2I07SBdYzkXulfZyZSL6M5Y_Ap17KE5qIXPGP5MiebSzuJFFIiQNI6Gj3LREGMgwtZdTtQk09LHenXAOIC9zEkedjhbHxoZDGC2ejC0MfNwS') as scraper:
        company = scraper.scrape(company=user_name)
    blockPrint()
    comp_overview = company.overview
    enablePrint()
    print("******Linkedin crawling results******")
    # print(comp_overview)
    # for each_key in comp_overview:
    #     data_c = comp_overview[each_key]
    #     if(type(data_c)==str): data_c.replace('\n\n', '\n')
    #     print(each_key + " : ", data_c)

    # print(company.overview)
    return comp_overview


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
    sm_links = data[0]['social_media_links']
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
        sr = getGoogleLinksForSearchText('"' + comp_name + '"' + " linkedin", 5, 'normal')
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
            mycol.update_one({'_id': entry_id},
                             {'$set': corrected_dict})
            print("Successfully extended the data entry with linkedin profile information", entry_id)
        # else:
        #     print()
            # mycol.update_one({'_id': entry_id},
            #                  {'$set': {'linkedin_cp_info': []}})

# get_li_data([ObjectId('5eb13c97263ac8cb52b400e8')])