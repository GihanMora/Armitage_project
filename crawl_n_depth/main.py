import csv
import os
from get_n_search_results import getGoogleLinksForSearchText
from crawl_n_depth.spiders.n_crawler import run_crawler,run_multiple_crawlers
from key_phrase_extractor.kpe_model import key_phrase_extract
from LDA_model.lda_model import run_lda_model
from random import randint
from time import sleep


"""
Check path of chrome driver
Check path_to_jsons in main.py
"""

# f = open('evaluation/websites.txt','r')
# sites = [item[:-1] for item in f.readlines()]
# print(sites)
## get search results
## searchResults = getGoogleLinksForSearchText(text_to_search,number_of_results_required)
searchResults = getGoogleLinksForSearchText("Information Systems Australia",1)

all_data = []
searchResults_links = []
i=0
for searchResult in searchResults:
    link = searchResult['link']
    searchResults_links.append(link)
    current_data = {'title':searchResult['title'],'link':searchResult['link'],'description':searchResult['description']}
    data = [link,current_data]
    all_data.append(data)


# searchResults_links = []
# for searchResult in searchResults:
#     link = searchResult['link']
#     searchResults_links.append(link)
#
# for each_link in searchResults_links:
#     print(each_link)
#
#
# fff = open('ss.txt','w',encoding='utf8')
# fff.write(str(all_data))
# fff.close()
# s = open('ss.txt', 'r').read()
# data_re = eval(s)
# print(data_re)
# run_multiple_crawlers(data_re,3,100)

# f = open('evaluation/links.txt','r')
# sites = [item[:-1] for item in f.readlines()]
# set1=sites[75:]
# run_crawler(['https://au.gradconnection.com/'],2,50)


# searchResults_links = [each_result['link'] for each_result in searchResults]#extract links
# print("searching on google")
# print("found ",str(len(searchResults_links))," links")
# print(searchResults_links)

#crawl each result for n depth
# run_crawler(list_of_urls,crawling_depth,crawling_limit)
run_multiple_crawlers(all_data,10,1000)

#
#reading stored jsons to be given to LDA and Key phrase extraction
json_paths = [os.path.abspath(x) for x in os.listdir("extracted_json_files/")]
path_to_jsons = "F:/Armitage_project/crawl_n_depth/extracted_json_files/"#specify the path for json files
json_list = os.listdir(path_to_jsons)
for each_json in json_list:#for each search result
    path_f = path_to_jsons+each_json
    # run_lda_model(path to the json object,number_of_topics)
    run_lda_model(path_f,10)#run LDA
    # key_phrase_extract(path to the json object,number_of_candidates)
    key_phrase_extract(path_f,10)#run Key Phrase extraction
