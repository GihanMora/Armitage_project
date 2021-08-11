#make sure chrome driver's executable path is correct
#make sure gecko driver's executable path is correct(optional)
#fix sys path if you want to run this seperately
import time
import sys

from selenium.common.exceptions import WebDriverException

from os.path import dirname as up
three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)


#Requests Users


# print(result)
import requests
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Tag
# from fake_useragent import UserAgent
from random import choice

def proxy_generator():
    response = requests.get("https://sslproxies.org/")
    soup = BeautifulSoup(response.content, 'html5lib')
    proxy = {'https': choice(list(map(lambda x:x[0]+':'+x[1], list(zip(map(lambda x:x.text,
	   soup.findAll('td')[::8]), map(lambda x:x.text, soup.findAll('td')[1::8]))))))}
    return proxy

def use_chrome():
    # ua = UserAgent()
    # userAgent = ua.random #get a random user agent
    options = webdriver.ChromeOptions()  # use headless version of chrome to avoid getting blocked
    options.add_argument('headless')
    # options.add_argument(f'user-agent={userAgent}')
    options.add_argument('--no-sandbox')
    # options.add_argument("start-maximized")# // open Browser in maximized mode
    # options.add_argument("disable-infobars")# // disabling infobars
    # options.add_argument("--disable-extensions")# // disabling extensions
    # options.add_argument("--disable-gpu")# // applicable to windows os only
    # options.add_argument("--disable-dev-shm-usage")# // overcome limited resource problems

    browser = webdriver.Chrome(chrome_options=options,  # give the path to selenium executable
                               # executable_path='F://Armitage_lead_generation_project//chromedriver.exe'
                               executable_path=three_up+'//utilities//chromedriver.exe',
                               )
    return browser

def use_firefox():
    profile = webdriver.FirefoxProfile()
    # profile.set_preference("browser.privatebrowsing.autostart", True)
    proxies = ['54.213.66.208', "43.250.242.251", "192.248.15.153"
               ]
    prx = choice(proxies)
    print(prx)
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", prx)
    profile.set_preference("network.proxy.http_port", 80)
    options = Options()
    options.headless = True

    profile.update_preferences()
    browser = webdriver.Firefox(firefox_options=options, firefox_profile=profile,
                                executable_path=three_up+'utilities/geckodriver')
    return browser

def getGoogleLinksForSearchText(searchText,number_of_results,mode):#given a search query get first n results from google
    """

    :param searchText: query text of searching
    :param number_of_results: how many results required
    :return: save resulted links to csv along with title and description
    """
    print("searching on google",searchText)

    #buildingsearch query
    searchGoogle = URL = f"https://google.com/search?q={searchText}"+"&num=" + str(number_of_results)

    try:

        #our scraper
        browser = use_chrome()#get a chrome instance
        browser.get(searchGoogle)
        time.sleep(5)
        pageSource = browser.page_source
        # print(pageSource)
        browser.quit()

        soup = BeautifulSoup(pageSource, 'html.parser')#bs4
        is_captcha_on_page = soup.find("div", id="recaptcha") is not None

        # if(is_captcha_on_page):#a captcha triggered
        #     return 'captcha'
        count = 0
        while (is_captcha_on_page):
            count = count + 1
            print("captch is detected " + str(count) + " times")
            print("waiting more time", count * 120)
            time.sleep(count * 120)
            browser = use_chrome()#get a chrome instance
            browser.get(searchGoogle)

            pageSource = browser.page_source
            time.sleep(5)
            browser.quit()
            soup = BeautifulSoup(pageSource, 'html.parser')#bs4
            is_captcha_on_page = soup.find("div", id="recaptcha") is not None


        #scraper_API
        # from scraper_api import ScraperAPIClient
        # client = ScraperAPIClient('71e54dccbd8d60be19191bbfded3c7b2')
        # pageSource = client.get(url='https://www.google.com/search?q=caltex+australia', render=True).text
        # soup = BeautifulSoup(pageSource, 'html.parser')  # bs4






        results = []
        result_div = soup.find_all('div', attrs={'class': 'g'})
        print('len_res',len(result_div))
        # print(result_div)
        for r in result_div:
            # print('vvv',r)
            # Checks if each element is present, else, raise exception
            try:
                link = r.find('a', href=True)['href']#extracting the link
                print('link',link)
                title = None
                title = r.find('h3')

                if isinstance(title,Tag):#extracting the title of the link
                    title = title.get_text()
                print('title', title)
                description = None
                description = r.find('div', attrs={'class': 'VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf'})#extracting the description
                if(description==None):#VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf
                    description = r.find('div', attrs={'class' :'LGOjhe'})
                # print('ddd',description)
                if isinstance(description, Tag):
                    description = description.get_text()
                print('des',description)
                # Check to make sure everything is present before appending
                if (link not in ['',None]) and (title not in ['',None]) and (description not in ['',None]):#remove links if information is not available
                    rich_description = []
                    if(mode=='initial'):
                        print("initial")
                        browser = use_chrome()
                        browser.get(link)
                        time.sleep(5)
                        pageSource = browser.page_source
                        browser.quit()
                        # browser.close()
                        soup = BeautifulSoup(pageSource, 'html.parser')
                        metas = soup.find_all('meta')
                        # print(metas)
                        meta_description = [meta.attrs['content'] for meta in metas if
                                            'name' in meta.attrs and meta.attrs['name'] == 'description']
                        og_description = [meta.attrs['content'] for meta in metas if
                                          'property' in meta.attrs and meta.attrs['property'] == 'og:description']
                        # twitter_description =  [meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'twitter:description']
                        if (meta_description != og_description):
                            rich_description = meta_description + og_description
                        else:
                            rich_description = meta_description

                        rich_description = '_'.join(rich_description)
                        rich_description = rich_description.replace(',',' ')
                        print('***',rich_description)

                    item = {
                        "search_text":searchText,
                        "title": title.replace(',','_'),
                        "link": link,
                        "description": description.replace(',',' '),
                        "rich_description":rich_description
                    }

                    # rich_descriptions = list(set(rich_descriptions))
                    # print(rich_descriptions)
                    # print(item)


                    # print("*************************************************")
                    results.append(item)



            # Next loop if one element is not present
            except Exception as e:
                print(e)
                continue

        # with open('first_n_results.csv', mode='w', encoding='utf8') as results_file:#store search results in to a csv file
        #     results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #
        #     for each_item in results:
        #         results_writer.writerow([each_item['title'], each_item['link'], each_item['description']])
        #     results_file.close()
        print("got "+str(len(results))+" results")
        return results


    except WebDriverException as e:
        print("Browser Issue Occured!",e)
        return 'error'
    except Exception as e:
        print("Exception Occured!", e)
        return 'error'

#To run this scrpit individually use following line and run the script
# searchResults = getGoogleLinksForSearchText(text_to_search,number_of_results_required)
# for searchResult in searchResults:
#     print(searchResult)

#example
# searchResults = getGoogleLinksForSearchText("caltext australia",3,'normal')
# for searchResult in searchResults:
#     print(searchResult)


