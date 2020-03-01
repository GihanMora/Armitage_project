import csv
import json
import os
from get_n_search_results import getGoogleLinksForSearchText
from crawl_n_depth.spiders.n_crawler import run_crawler,run_multiple_crawlers
from key_phrase_extractor.kpe_model import key_phrase_extract
from LDA_model.lda_model import run_lda_model
from key_phrase_extractor.Rake_model import run_rake_model
from LDA_model.guided_lda import run_guided_lda_model
from LDA_model.wordnet import run_wordcloud_model
from key_phrase_extractor.textrank import run_textrank_model
from random import randint
from time import sleep


"""
Check path of chrome driver
Check path_to_jsons in main.py
"""
# link_s = ['https://getatomi.com/','https://www.beautycoursesonline.com/','https://www.modernstar.com.au/','https://www.negotiations.com/']
# f = open('evaluation/links.txt','r')
# sites = [item[:-1] for item in f.readlines()]
# print(sites)
# ## get search results
# ## searchResults = getGoogleLinksForSearchText(text_to_search,number_of_results_required)
# # searchResults = getGoogleLinksForSearchText("Information Systems Australia",1)


#reading stored jsons to be given to LDA and Key phrase extraction
json_paths = [os.path.abspath(x) for x in os.listdir("data/extracted_json_files/")]
path_to_jsons = "F:/Armitage_project/crawl_n_depth/data/extracted_json_files/"#specify the path for json files
json_list = os.listdir(path_to_jsons)
j_list = [(path_to_jsons+each_path) for each_path in json_list]
print(j_list)

#

for i,each_json in enumerate(json_list[:100]):#for each search result
    path_f = path_to_jsons+each_json
    with open(path_f) as json_file:
        data_o = json.load(json_file)


    data_dict = data_o[0]
    search_text = data_o[0]['search_text']
    sr = getGoogleLinksForSearchText(search_text, 1)
    search_data = {
        'title': sr[0]['title'],
        'link_corrected': sr[0]['link'],
        'description': sr[0]['description']
    }
    data_dict.update(search_data)
    data = []  # preparing data to dump
    data.append(data_dict)
    domain = sr[0]['link'].split("/")[2]  # getting allowed links from the starting urls itself
    json_name = str(i) + "_" + domain + "_data.json"  # give json file name as domain + iteration
    with open('extracted_json_files/' + json_name, 'w') as outfile:
        json.dump(data, outfile)  # dumping data and save
    sleep(randint(5, 50))



# searchResults = []
if not os.path.exists('extracted_json_files'):
    os.makedirs('extracted_json_files')
# for i,each_l in enumerate(sites[80:]):
#     sr = getGoogleLinksForSearchText(each_l,1)
#
#     print(sr)
#     # searchResults.append(sr[0])
#     if(len(sr)>0):
#         data = []  # preparing data to dump
#         data.append(
#             {
#             'title': sr[0]['title'],
#             'link': sr[0]['link'],
#             'description': sr[0]['description']
#         }
#         )
#         domain=sr[0]['link'].split("/")[2]#getting allowed links from the starting urls itself
#
#         json_name =  str(i+79)+ "_"+domain+"_data.json"  # give json file name as domain + iteration
#         with open('extracted_json_files/' + json_name, 'w') as outfile:
#             json.dump(data, outfile)  # dumping data and save
#     else:
#         print("No Data Found")
#     sleep(5)

#
# all_data = []
# searchResults_links = []
# print(searchResults)
# i=0
# for searchResult in searchResults:
#     link = searchResult['link']
#     searchResults_links.append(link)
#     current_data = {'title':searchResult['title'],'link':searchResult['link'],'description':searchResult['description']}
#     data = [link,current_data]
#     all_data.append(data)










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

#reading stored jsons to be given to LDA and Key phrase extraction
# json_paths = [os.path.abspath(x) for x in os.listdir("extracted_json_files/")]
# path_to_jsons = "F:/Armitage_project/crawl_n_depth/extracted_json_files/"#specify the path for json files
# json_list = os.listdir(path_to_jsons)
# j_list = [(path_to_jsons+each_path) for each_path in json_list]
# print(j_list)
# run_multiple_crawlers(j_list,3,100)






#
#
# for each_json in json_list:#for each search result
#     path_f = path_to_jsons+each_json
#     # # run_lda_model(path to the json object,number_of_topics)
#     # run_lda_model(path_f,10)#run LDA
#     # # key_phrase_extract(path to the json object,number_of_candidates)
#     # key_phrase_extract(path_f,10)#run Key Phrase extraction
#     # run_rake_model(path_f, 50)
#     # run_guided_lda_model(path_f,5)
#     run_textrank_model(path_f,50,5)
#     # run_wordcloud_model(path_f)
