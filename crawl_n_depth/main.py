import csv
import json
import os
import time

import pandas as pd
from get_n_search_results import getGoogleLinksForSearchText
from urllib.parse import urlparse
from crawl_n_depth.spiders.n_crawler import run_crawler,run_multiple_crawlers,run_crawler_given_csv,conf_runf
from key_phrase_extractor.kpe_model import key_phrase_extract
# from LDA_model.lda_model import run_lda_model
from key_phrase_extractor.Rake_model import run_rake_model
# from LDA_model.guided_lda import run_guided_lda_model
# from LDA_model.wordnet import run_wordcloud_model
from key_phrase_extractor.textrank import run_textrank_model
from random import randint
from time import sleep

import csv
import re


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)

def build_jsons_given_csv(csv_path,json_destination):
    if not os.path.exists(json_destination):
        os.makedirs(json_destination)
    with open(csv_path, "r", encoding='utf-8') as f:
        reader = csv.reader(f, delimiter="\t")
        for i,line in enumerate(reader):#going for n depth for the each google search result
            row_line = line[0].split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)")

            if (i == 10): break
            print(row_line)
            data_dict = {
                'ABN': row_line[0],
                 'EntityTypeInd':row_line[1],
                 'EntityTypeText':row_line[2],
                 'NonIndividualNameText':row_line[3],
                 'GivenName':row_line[4],
                 'FamilyName':row_line[5],
                 'State':row_line[6],
                 'Postcode':row_line[7],
                 'ASICNumber':row_line[8],
                 'OtherEntity':row_line[9],
                 'title':row_line[10],
                 'link':row_line[11],
                 'description':row_line[12]
                 }
            data = []  # preparing data to dump
            data.append(data_dict)
            # print(data)
            e_name = row_line[3].replace(" ","_").replace('"',"").replace("/","_")
            print(e_name)
            j_name = '\\'+str(i)+'_'+row_line[0]+'_'+row_line[1]+'_'+ e_name+'.json'
            # with open(json_destination + j_name, 'w+') as outfile:
            #     json.dump(data, outfile)
def build_jsons_given_csv_pd(csv_path,json_destination):
    if not os.path.exists(json_destination):
        os.makedirs(json_destination)

    df = pd.read_csv(csv_path)
    df.head()
    if not os.path.exists(json_destination):
        os.makedirs(json_destination)
    for i in range(len(df)):#going for n depth for the each google search result
            row_line = df.values[i]
            # row_line = line[0].split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)")


            print(row_line)
            data_dict = {
                'ABN': row_line[0],
                 'EntityTypeInd':row_line[1],
                 'EntityTypeText':row_line[2],
                 'NonIndividualNameText':row_line[3],
                 'GivenName':row_line[4],
                 'FamilyName':row_line[5],
                 'State':row_line[6],
                 'Postcode':row_line[7],
                 'ASICNumber':row_line[8],
                 'OtherEntity':row_line[9],
                 'title':row_line[10],
                 'link':row_line[11],
                 'description':row_line[12]
                 }
            data = []  # preparing data to dump
            data.append(data_dict)
            # print(data)
            e_name = row_line[3].replace(" ","_").replace('"',"").replace("/","_")
            print(e_name)
            j_name = '\\'+str(i)+'_'+str(row_line[0])+'_'+str(row_line[1])+'_'+ e_name+'.json'
            with open(json_destination + j_name, 'w+') as outfile:
                json.dump(data, outfile)
    # with open(csv_path, "r", encoding='utf-8') as f:
    #     reader = csv.reader(f, delimiter="\t")
    #     for i,line in enumerate(reader):#going for n depth for the each google search result
    #         row_line = line[0].split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)")
    #
    #         if (i == 10): break
    #         print(row_line)
    #         data_dict = {
    #             'ABN': row_line[0],
    #              'EntityTypeInd':row_line[1],
    #              'EntityTypeText':row_line[2],
    #              'NonIndividualNameText':row_line[3],
    #              'GivenName':row_line[4],
    #              'FamilyName':row_line[5],
    #              'State':row_line[6],
    #              'Postcode':row_line[7],
    #              'ASICNumber':row_line[8],
    #              'OtherEntity':row_line[9],
    #              'title':row_line[10],
    #              'link':row_line[11],
    #              'description':row_line[12]
    #              }
    #         data = []  # preparing data to dump
    #         data.append(data_dict)
    #         # print(data)
    #         e_name = row_line[3].replace(" ","_").replace('"',"").replace("/","_")
    #         print(e_name)
    #         j_name = '\\'+str(i)+'_'+row_line[0]+'_'+row_line[1]+'_'+ e_name+'.json'
    #         # with open(json_destination + j_name, 'w+') as outfile:
    #         #     json.dump(data, outfile)

# build_jsons_given_csv_pd('F:\Armitage_project\crawl_n_depth\data\public_comp\Public_companies.csv','F:\Armitage_project\crawl_n_depth\data\public_comp_extracted_json_files')
def initial_crawl():
    with open("data/public_comp/Australian Public Company.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        # for i in range(232):  # count from 0 to 7
        #     next(reader)  # and discard the rows
        # reader = next(reader)
        with open('private_comp_urls_quality.csv', 'a+', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for i,line in enumerate(reader):
                line = line[0].split(',')
                if(i==0):
                    print(line+['title', 'link', 'description'])
                    writer.writerow(line+['title', 'link', 'description'])
                else:
                    comp_name = line[3].replace(" ","+")
                    if comp_name=='None':
                        continue
                    print(comp_name)
                    sr = getGoogleLinksForSearchText(comp_name, 3)
                    count=0
                    while(sr=='captcha'):
                        count=count+1
                        print('captch detected and sleeping for n times n:',count)
                        time.sleep(1200*count)
                        sr = getGoogleLinksForSearchText(comp_name, 3)
                    if(len(sr)):
                        print(line + [sr[0]['title'], sr[0]['link'], sr[0]['description']])
                        writer.writerow(line + [sr[0]['title'], sr[0]['link'], sr[0]['description']])
                    else:
                        print(line + ["None","None","None"])
                        writer.writerow(line + ["None","None","None"])


def initial_quality_crawl():
    with open("data/private_comp/Australian Private Company.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for i in range(2254):  # count from 0 to 7
            next(reader)  # and discard the rows
        # reader = next(reader)
        with open('private_qualty_comp_urls.csv', 'a+', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['resarting']+['title', 'link', 'description'])
            for i,line in enumerate(reader):
                line = line[0].split(',')


                # if i==1040:break

                if(False):
                    print(line+['title', 'link', 'description'])
                    writer.writerow(line+['title', 'link', 'description'])
                else:
                    comp_name = line[3].replace(" ","+")
                    if comp_name=='None':
                        continue
                    print(comp_name)
                    sr = getGoogleLinksForSearchText(comp_name, 3)
                    count=0
                    while(sr=='captcha'):
                        count=count+1
                        print('captch detected and sleeping for n times nx1000:',count)
                        time.sleep(1000*count)
                        sr = getGoogleLinksForSearchText(comp_name, 3)
                    black_list = ['businessnews.com','www.facebook.com' ,'www.bloomberg.com' ,'companycheck.co.uk','www.businessnews.com.au',
                                  'asic.hkcorporationsearch.com' ,'abnlookup.net' ,'aubiz.net' ,'auscompanies.com' ,'abr.business.gov.au','creditorwatch.com.au',
                                  'google.com' ,'whitepages.com.au','abn-lookup.com','au.mycompanydetails.com','infobel.com' ,'www.tripadvisor.com',
                                  'truelocal.com.au','realestate.com.au','localsearch.com.au','linkedin.com' ,'au.kompass.com','smart-tours.net','www.thredbo.com.au',
                                  'en.wikipedia.org','au.linkedin.com','books.google.com','books.google.lk','wikipedia.org','au.linkedin.com','www.yellowpages.com.au',
                                  'www.whereis.com', 'www.whitepages.com.au', 'www.clarencevalleynews.com.au','beta.companieshouse.gov.uk','companycheck.co.uk',
                                  'issuu.com','app.duedil.com','www.thredbo.com.au','opengovau.com','theinteriorsaddict.com','pty-ltd.net','opencorporates.com','www.nzlbusiness.com',
                                  'touch.facebook.com','en-gb.facebook.com','www.truelocal.com.au']

                    # 'www.dnb.com'
                    received_links = [i['link'] for i in sr]

                    received_domains = [i.split("/")[2] for i in received_links]
                    filtered_sr = []

                    print('rd',received_domains)
                    for i,each in enumerate(received_domains):
                        if each not in black_list:
                            filtered_sr.append(sr[i])
                    # print('fd', filtered_sr)
                    print()
                    sr = filtered_sr
                    if(len(sr)):
                        print(line + [sr[0]['title'], sr[0]['link'], sr[0]['description']])
                        writer.writerow(line + [sr[0]['title'], sr[0]['link'], sr[0]['description']])
                    else:
                        print(line + ["None","None","None"])
                        writer.writerow(line + ["None","None","None"])

# initial_quality_crawl()
"""
Check path of chrome driver
Check path_to_jsons in main.py
"""
def given_df_to_json(df,each_json):
    for each_p in df['NonIndividualNameText'][:10]:
        each_p=each_p.replace(" ","+")
        sr = getGoogleLinksForSearchText(each_p, 3)
        print(sr)
        search_data = {
                    'title': sr[0]['title'],
                    'link_corrected': sr[0]['link'],
                    'description': sr[0]['description'],
                }
        data = []  # preparing data to dump
        data.append(search_data)
        with open('left_json_files/' + each_json, 'w+') as outfile:
                    json.dump(data, outfile)  # dumping data and save

def read_links_from_text_and_search_dump_as_jsons():
    f = open('evaluation/links.txt','r')
    sites = [item[:-1] for item in f.readlines()]
    print(sites)
    if not os.path.exists('extracted_json_files'):
        os.makedirs('extracted_json_files')
    for i,each_l in enumerate(sites[80:]):
        sr = getGoogleLinksForSearchText(each_l,1)

        print(sr)
        # searchResults.append(sr[0])
        if(len(sr)>0):
            data = []  # preparing data to dump
            data.append(
                {
                'title': sr[0]['title'],
                'link': sr[0]['link'],
                'description': sr[0]['description']
            }
            )
            domain=sr[0]['link'].split("/")[2]#getting allowed links from the starting urls itself

            json_name =  str(i+79)+ "_"+domain+"_data.json"  # give json file name as domain + iteration
            with open('extracted_json_files/' + json_name, 'w') as outfile:
                json.dump(data, outfile)  # dumping data and save
        else:
            print("No Data Found")
        sleep(5)
# ## get search results
## searchResults = getGoogleLinksForSearchText(text_to_search,number_of_results_required)
# searchResults = getGoogleLinksForSearchText("Information Systems Australia",1)
# print(searchResults)



#reading stored jsons to be given to LDA and Key phrase extraction
# json_paths = [os.path.abspath(x) for x in os.listdir("F:\Armitage_project\crawl_n_depth\data\public_comp_extracted_json_files")]
# sorted_j_list = sorted_alphanumeric(json_paths)
# print('s',json_paths)
# path_to_jsons = "F:/Armitage_project/crawl_n_depth/extracted_json_files/"#specify the path for json files
# json_list = os.listdir(path_to_jsons)
# sorted_json_list = sorted_alphanumeric(json_list)
# j_list = [(path_to_jsons+each_path) for each_path in json_list]

# sorted_j_list = sorted_alphanumeric(json_paths)
# print('sxx',sorted_j_list)
# print(sorted_j_list)
#
def update_jsons_with_search_results(path_to_jsons,sorted_json_list):
    for i,each_json in enumerate(sorted_json_list):#for each search result
        path_f = path_to_jsons+each_json
        with open(path_f) as json_file:
            data_o = json.load(json_file)


        data_dict = data_o[0]
        search_text = data_o[0]['search_text']
        if(search_text=='tbc'):
            print(path_f)
            search_text = data_dict['company']+" Australia New Zealand company"

            sr = getGoogleLinksForSearchText(search_text, 3)
            search_data = {
                'title': sr[0]['title'],
                'link_corrected': sr[0]['link'],
                'description': sr[0]['description'],
                'search_text': search_text,
            }
            data_dict.update(search_data)
            data = []  # preparing data to dump
            data.append(data_dict)
            with open('left_json_files/' + each_json, 'w+') as outfile:
                json.dump(data, outfile)  # dumping data and save




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
# for each in sorted_j_list[121:300]:
#     print(each)

# F:\Armitage_project\crawl_n_depth\quality_json_files\1158_11006839087_PRV_MONDAN_PTY._LTD..json



json_paths = ['F:\Armitage_project\crawl_n_depth\quality_json_files\\'+x for x in os.listdir("F:\Armitage_project\crawl_n_depth\quality_json_files")]
print(json_paths)
sorted_j_list = sorted_alphanumeric(json_paths)
conf_runf(sorted_j_list[1131:1132],10,50)
# run_multiple_crawlers(sorted_j_list[0:5],3,5)
print('aassasa')
#
# la = ['F:\Armitage_project\crawl_n_depth\extracted_json_files\\585_Expressway_Spares_data.json']
# run_multiple_crawlers(la,3,100)

# run_crawler_given_csv('F:\Armitage_project\crawl_n_depth\data\public_comp\Public_companies.csv',3,100)


#
# #
# for each_json in sorted_json_list[1314:]:#for each search result
#     path_f = path_to_jsons+each_json
#     # # run_lda_model(path to the json object,number_of_topics)
#     run_lda_model(path_f,10)#run LDA
    # # # key_phrase_extract(path to the json object,number_of_candidates)
    # key_phrase_extract(path_f,10)#run Key Phrase extraction
    # run_rake_model(path_f, 50)
    # run_guided_lda_model(path_f,5)
    # run_textrank_model(path_f,50,5)
    # run_wordcloud_model(path_f,'bi')
