# pip install git+git://github.com/austinoboyle/scrape-linkedin-selenium.git
#chrome driver should contain in the folder
#fix sys path if you want to run this script individually
#replace linkedin live cookie value
# sudo apt install chromium-chromedriver incase of need
import sys, os
import time

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
        with CompanyScraper( cookie='AQEDATFG6sIE3LEoAAABctHCZhMAAAFy9c7qE1YAf88Gqlb0pR0x5Cp0gNCIAracLuI5FYe6CS5_1mY8qbHl7IlnzmRhN_i40IElSZ2TptvO9Ls-y1-dqGSRRDZMmEA8tet8eHHlQ6lHIWIbSNAlejo1') as scraper:
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
    except SyntaxError:
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
        sr = getGoogleLinksForSearchText( comp_name + " linkedin australia", 5, 'normal')
        if (len(sr) == 0):
            sr = getGoogleLinksForSearchText(comp_name + " linkedin australia", 5, 'normal')
            if (len(sr) == 0):
                sr = getGoogleLinksForSearchText(comp_name + " linkedin australia", 5, 'normal')

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
        time.sleep(60)
        li_url = get_li_url(entry_id)
        if(li_url):
            print(li_url)
            # blockPrint()
            comp_li_data = scrape_company(li_url)
            # enablePrint()
            # print(comp_li_data)
            corrected_dict = {k+'_li': v for k, v in comp_li_data.items()}
            # corrected_dict['li_url']=li_url
            if('headquarters_li' in corrected_dict.keys()):
                # print(corrected_dict['headquarters_li'])
                if(not isvalid_hq(corrected_dict['headquarters_li'])):
                    corrected_dict = {}


            # for k in corrected_dict:
            #     print("'"+str(k)+"'")
            print(corrected_dict)
            if (len(corrected_dict.keys())):
                corrected_dict['li_url'] = li_url
                mycol.update_one({'_id': entry_id},
                                 {'$set': corrected_dict})
                print("Successfully extended the data entry with linkedin profile information", entry_id)
            else:
                print("No correct linkedin profile found! dict is empty")
        # else:
        #     print()
            # mycol.update_one({'_id': entry_id},
            #                  {'$set': {'linkedin_cp_info': []}})
edu_set = [ObjectId('5eb62e2a134cc6fb9536e93d'), ObjectId('5eb630147afe26eca4ba7bfa'), ObjectId('5eb6311c86662885174692de'), ObjectId('5eb631f1fac479799dedd1f8'), ObjectId('5eb6331597c8f5512179c4f1'), ObjectId('5eb634492802acb8c48e02aa'), ObjectId('5eb63539be65b70e5af0c7a9'), ObjectId('5eb6363894bd0b097f9c2734'), ObjectId('5eb6378b772150870b5c8d27'), ObjectId('5eb639ee2c60aae411d1ae8b'), ObjectId('5eb63aff81de1c4846fd91ab'), ObjectId('5eb63c1e9c69232f6ed6edd8'), ObjectId('5eb63d1b9d2ec0b892c42dd5'), ObjectId('5eb63e1ee805d1cff3d80a25'), ObjectId('5eb63ee743b668cb27ef8137'), ObjectId('5eb640560732058562a400b3'), ObjectId('5eb646ce3b4442b4da91c057'), ObjectId('5eb6479687b6932b9e6de098'), ObjectId('5eb648bf6bc924ef46ab60da'), ObjectId('5eb64a8e96bdd2bbbb3287e5'), ObjectId('5eb64bc810a22fecd4eca987'), ObjectId('5eb64cfc8c94747a21f39855'), ObjectId('5eb64e13158973dfa9982019'), ObjectId('5eb64f4ea0549166c51ca057'), ObjectId('5eb650acab06d680d6990351'), ObjectId('5eb651bc5fa088c453991725'), ObjectId('5eb652de55de509b4a9efaf4'), ObjectId('5eb65433af5bcc3efe32c504'), ObjectId('5eb6556c29c37695bc97bec4'), ObjectId('5eb6567909d0de1b6b708cf8'), ObjectId('5eb657e754ee9cbe1a7388c8'), ObjectId('5eb65942b46918d079adebe9'), ObjectId('5eb65a927cb5b3a1ff4ae362'), ObjectId('5eb65b645417d406270e7e63'), ObjectId('5eb65d83728ad01002b3a5f6'), ObjectId('5eb65f2cde8cab37cd68dffd'), ObjectId('5eb6603b6e69c6f2e1092cf8'), ObjectId('5eb661a6796445df9bfd756d'), ObjectId('5eb6631b245b7e033d0f92ed'), ObjectId('5eb66401b0e60a643fae0467'), ObjectId('5eb6651284c93e9e1b685024'), ObjectId('5eb66682dc99a524418da337'), ObjectId('5eb667a554cc6bc47dbfea44'), ObjectId('5eb6688cf9acda3a876322e4'), ObjectId('5eb669883e6dc49bd6f1540f'), ObjectId('5eb66a9b90f9dd06f1107866'), ObjectId('5eb66bb449a0728d932475bc'), ObjectId('5eb66ce4535d821544a14dee'), ObjectId('5eb66dabf3d5b58ef16a4c74'), ObjectId('5eb66e99e95b7d86f2518828'), ObjectId('5eb66fa738555190120005d2'), ObjectId('5eb670c2382a70cea3c90149'), ObjectId('5eb672382cf60f5b673dc845'), ObjectId('5eb6734f61272a1489607d7c'), ObjectId('5eb6746b3f8078c646a32068'), ObjectId('5eb675384beae11731a0ce35'), ObjectId('5eb676209d0d155a1c6530f3'), ObjectId('5eb6777b140e783b3524f4d9'), ObjectId('5eb6783b3dd775bea489b02d'), ObjectId('5eb67952c38498d75c86627f'), ObjectId('5eb67a4c109ddab70aec7b2d'), ObjectId('5eb67bc12373d9a910e8750f'), ObjectId('5eb67d3dd9818bcd44884d39'), ObjectId('5eb67e66b7921dcf1c2e6805'), ObjectId('5eb67fa821374c1c36ea76bb'), ObjectId('5eb680d98c70c48229cd26b6'), ObjectId('5eb6820dcc1fecfea5009f48'), ObjectId('5eb682ecd810c81378eb806d'), ObjectId('5eb68405b8f3f1e1b3084a52'), ObjectId('5eb6853a626f824ef428e315'), ObjectId('5eb688a782ee2ac4699515f2'), ObjectId('5eb689814e048265dd507dbc'), ObjectId('5eb68a771a268ae85ef97960'), ObjectId('5eb68b52298db2bd4cebdd0e'), ObjectId('5eb68c65501e64174bede873'), ObjectId('5eb68d458e708541f4671189'), ObjectId('5eb68e2fab2ce0451e2b4056'), ObjectId('5eb68edce0b5b75b05fba1e6'), ObjectId('5eb690038f7f6e26b6253fd5'), ObjectId('5eb690bd8d99ac316303ffb6'), ObjectId('5eb6918fa2e66438837c2d83'), ObjectId('5eb6925a31a5f94e1207b916'), ObjectId('5eb6944565d7b2466379f198'), ObjectId('5eb694f59c10ae1d407b7c2a'), ObjectId('5eb695e1ffe996bbe09292fe'), ObjectId('5eb696f6ef36438bec383b7e'), ObjectId('5eb697cac579ca076779cb0f'), ObjectId('5eb698a46de98c90f95a497d'), ObjectId('5eb699a671806057e76f0141'), ObjectId('5eb69a7d5587c492135fd56c'), ObjectId('5eb69b6fc6cad85bd913e12a'), ObjectId('5eb69c52d1ecab806f2beead'), ObjectId('5eb69cefc81bdf1aac4bf6a1'), ObjectId('5eb69e087e9ea4385e20beed'), ObjectId('5eb69f48a04ce33b509b4895'), ObjectId('5eb6a058cd265d6ef2ee766f'), ObjectId('5eb6a12f7ef80a97c531cc67'), ObjectId('5eb6a21fe632eaf0b1d593db'), ObjectId('5eb6a63fc0820e4534126e94'), ObjectId('5eb6a72dfc5d1c47d4ca9cd1'), ObjectId('5eb6a8462d272649f7b4df95'), ObjectId('5eb6a930b440ebf60d42d6c2'), ObjectId('5eb6aa15b5b4db2c7393254c'), ObjectId('5eb6ab260aef4a583d77118f'), ObjectId('5eb6ac1bfff106a6f58c42e7'), ObjectId('5eb6ad1662db4e6c180a378b'), ObjectId('5eb6ae390bdb0b194f41f9b3'), ObjectId('5eb6af2a6012ca09c1728130'), ObjectId('5eb6afc4e15b344d1a3aafa0'), ObjectId('5eb6b19b1c6e630676c62445'), ObjectId('5eb6b2a5a9211572420260e9'), ObjectId('5eb6b38eeb5e21b75a0d7cdb'), ObjectId('5eb6b45f4dab807be8d7a28a'), ObjectId('5eb6b53fd8471918b43146b7'), ObjectId('5eb6b61fabf00d5fdb2d05a3'), ObjectId('5eb6b71e5cd9b7b54c7d9961'), ObjectId('5eb6b9158f232307ce0bdc13'), ObjectId('5eb6b9dbb8b6b03010c4dcc6'), ObjectId('5eb6bad32c05d6f34cf32652'), ObjectId('5eb6bbbee2f17c3f3238cec8'), ObjectId('5eb6bca1b68e7672cd0ef210'), ObjectId('5eb6bdb1e7b6cc4614eb0edb'), ObjectId('5eb6beca47492aa1e0553de4'), ObjectId('5eb6bfc707fd60d7d77844de'), ObjectId('5ed3846f023b726e6d17d4f0'), ObjectId('5ed38b25d439f58cc06e5825'), ObjectId('5ed38d5420653aee6e3220c8'), ObjectId('5ed38efe1838c05e0c6fb6e4'), ObjectId('5ed3900863e5bffa1d2b4e2f'), ObjectId('5ed391925d33c4975503bb94'), ObjectId('5ed394144eb75866dfdcdc0d'), ObjectId('5ed39521d784bdc428779a0f'), ObjectId('5ed3966ae5903d41b23471ba'), ObjectId('5ed3980c016ddd49b0f4c304'), ObjectId('5ed3996045e3020d63762dce'), ObjectId('5ed39b1195eba19024e714bf'), ObjectId('5ed39d3781f6df0d82e6bfda'), ObjectId('5ed39f30fc1a9fd5e77e332f'), ObjectId('5ed3a07a5dbe3d7cdbc0a11f'), ObjectId('5ed3a21a7deae88594ebebcb'), ObjectId('5ed3a430b15357da758e9aaf'), ObjectId('5ed3a65cc612795088fb19b8'), ObjectId('5ed3a8655fa4a60f979e1f88'), ObjectId('5ed3ac8b4daab633d19b58d8'), ObjectId('5ed3add3461496c2716f7235'), ObjectId('5ed3af522f225fd825bf711a'), ObjectId('5ed3b088624645fcbe0374c5'), ObjectId('5ed3b2383758cc50c8bdd137'), ObjectId('5ed3b766a882d958e63eb52e')]
# print(edu_set.index(ObjectId('5eb6783b3dd775bea489b02d')))
# get_li_data(edu_set[59:60])