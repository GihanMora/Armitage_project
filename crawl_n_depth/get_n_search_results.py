import requests

from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Tag
import csv
from fake_useragent import UserAgent
import time

def getGoogleLinksForSearchText(searchText,number_of_results):#given a search query get first n results from google
    """

    :param searchText: query text of searching
    :param number_of_results: how many results required
    :return: save resulted links to csv along with title and description
    """
    print("searching on google",searchText)
    searchText=searchText+' -site:businessnews.com -site:facebook.com -site:bloomberg.com -site:asic.hkcorporationsearch.com -site:abnlookup.net -site:aubiz.net -site:auscompanies.com -site:google.com -site:whitepages.com.au -site:abn-lookup.com -site:au.mycompanydetails.com -site:infobel.com -site:truelocal.com.au -site:realestate.com.au -site:localsearch.com.au -site:linkedin.com -site:www.dnb.com -site:wikipedia.org'
    options = webdriver.ChromeOptions()#use headless version of chrome to avoid getting blocked
    options.add_argument('headless')
    # options.add_argument("-user-data-dir=C:\Users\Gihan Gamage\AppData\Local\Google\Chrome\User Data\Default")
    browser = webdriver.Chrome(chrome_options=options,#give the path to selenium executable
            # executable_path='F://Armitage_lead_generation_project//chromedriver.exe'
            executable_path = 'utilities//chromedriver.exe'

                               )
     # initiate the class (you can pass an apikey if you have one)

    # random_proxy_us = api.get_proxy(country="US")
    #buildingsearch query
    searchGoogle = f"https://google.com/search?q={searchText}"+""+"&num=" + str(number_of_results)
    # print(searchGoogle)
    ua = UserAgent()
    userAgent = ua.random
    # print(userAgent)
    # options.add_argument(f'user-agent={userAgent}')

    # proxies = {"http": "http://10.10.1.10:3128",
    #            "https": "http://10.10.1.10:1080"}

    # requests.get("http://example.org", proxies=proxies)
    browser.get(searchGoogle)
    # print(browser.page_source)
    headers = {'User-Agent': userAgent}
    r = requests.get(searchGoogle, headers=headers)
    pageSource = browser.page_source
    # print(pageSource)
    soup = BeautifulSoup(pageSource, 'html.parser')#bs4
    is_captcha_on_page = soup.find("div", id="recaptcha") is not None
    count = 0
    while(is_captcha_on_page):
        count=count+1
        print("captch is detected "+str(count)+" times")
        print("waiting more time",count*300)
        time.sleep(count*300)
        soup = BeautifulSoup(pageSource, 'html.parser')  # bs4
        is_captcha_on_page = soup.find("div", id="recaptcha") is not None



    results = []
    result_div = soup.find_all('div', attrs={'class': 'g'})
    # print(result_div)
    # print(len(result_div))
    for r in result_div:
        # Checks if each element is present, else, raise exception
        try:
            link = r.find('a', href=True)['href']#extracting the link
            title = None
            title = r.find('h3')

            if isinstance(title,Tag):#extracting the title of the link
                title = title.get_text()

            description = None
            description = r.find('span', attrs={'class': 'st'})#extracting the description

            if isinstance(description, Tag):
                description = description.get_text()

            # Check to make sure everything is present before appending
            if (link not in ['',None]) and (title not in ['',None]) and (description not in ['',None]):#remove links if information is not available
                item = {
                    "title": title,
                    "link": link,
                    "description": description,
                }
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

#To run this scrpit individually use following line and run the script
# searchResults = getGoogleLinksForSearchText(text_to_search,number_of_results_required)
# for searchResult in searchResults:
#     print(searchResult)

# #
searchResults = getGoogleLinksForSearchText("gampaha srilanka",3)
for searchResult in searchResults:
    print(searchResult)


