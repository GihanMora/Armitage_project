from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Tag
import csv


def getGoogleLinksForSearchText(searchText,number_of_results):#given a search query get first n results from google
    """

    :param searchText: query text of searching
    :param number_of_results: how many results required
    :return: save resulted links to csv along with title and description
    """
    options = webdriver.ChromeOptions()#use headless version of chrome to avoid getting blocked
    options.add_argument('headless')
    browser = webdriver.Chrome(options=options,#give the path to selenium executable
            # executable_path='F://Armitage_lead_generation_project//chromedriver.exe'
            executable_path = 'utilities//chromedriver.exe'

                               )

    #buildingsearch query
    searchGoogle = URL = f"https://google.com/search?q={searchText}"+"&num=" + str(number_of_results)

    browser.get(searchGoogle)

    pageSource = browser.page_source

    soup = BeautifulSoup(pageSource, 'html.parser')#bs4
    results = []
    result_div = soup.find_all('div', attrs={'class': 'g'})

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



    with open('first_n_results.csv', mode='w') as results_file:#store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for each_item in results:
            results_writer.writerow([each_item['title'], each_item['link'], each_item['description']])
        results_file.close()
    return results

#To run this scrpit individually use following line and run the script
# searchResults = getGoogleLinksForSearchText(text_to_search,number_of_results_required)
# for searchResult in searchResults:
#     print(searchResult)

