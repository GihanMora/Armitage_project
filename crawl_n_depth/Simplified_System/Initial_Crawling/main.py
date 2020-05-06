import sys
sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
from Simplified_System.Initial_Crawling.get_n_search_results import getGoogleLinksForSearchText

import csv
import json
import os
import time
import pymongo
from Simplified_System.Database.db_connect import refer_collection
# from ..Database.db_connect import refer_collection


def search_a_company(comp_name, db_collection, query_entry):
    sr = getGoogleLinksForSearchText(comp_name, 3, 'initial')
    count = 0
    while (sr == 'captcha'):
        count = count + 1
        print('captch detected and sleeping for n times n:', count)
        time.sleep(1200 * count)
        sr = getGoogleLinksForSearchText(comp_name, 3, 'initial')

    b_list_file = open('F:\Armitage_project\crawl_n_depth\Simplified_System\Initial_Crawling\\black_list.txt','r')
    black_list = b_list_file.read().splitlines()
    # 'www.dnb.com'
    received_links = [i['link'] for i in sr]

    received_domains = [i.split("/")[2] for i in received_links]
    filtered_sr = []

    print('rd', received_domains)
    for i, each in enumerate(received_domains):
        if each not in black_list:
            filtered_sr.append(sr[i])

    if(len(filtered_sr)):
        filtered_sr[0]['comp_name'] = filtered_sr[0]['search_text']
        filtered_sr[0]['query_id'] = query_entry
        record_entry=db_collection.insert_one(filtered_sr[0])
        print(filtered_sr[0])
        print("search record stored in db: ",record_entry.inserted_id)
        return record_entry.inserted_id
    else:
        print("No results found!")
        return None
    #store data in a csv file
    # with open('search_results.csv', mode='w',encoding='utf8') as results_file:  # store search results in to a csv file
    #     results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     # print(filtered_sr[0])
    #     for each_item in filtered_sr:
    #         results_writer.writerow([each_item['title'], each_item['link'], each_item['description']])
    #         break
    #     results_file.close()


def search_a_query(search_query,number_of_results,db_collection,query_entry):
    sr = getGoogleLinksForSearchText(search_query, number_of_results, 'initial')
    count = 0
    while (sr == 'captcha'):
        count = count + 1
        print('captch detected and sleeping for n times n:', count)
        time.sleep(1200 * count)
        sr = getGoogleLinksForSearchText(search_query, number_of_results, 'initial')

    if (len(sr)):
        # print(sr)
        # record_entry = db_collection.insert_many(sr)

        for each_sr in sr:
            print(each_sr)
        received_links = [i['link'] for i in sr]
        received_domains = [i.split("/")[2] for i in received_links]
        ids_list=[]
        for k in range(len(received_domains)):
            time.sleep(20)
            print(received_links[k],received_domains[k])
            if(received_domains[k] in ['www.capterra.com','www.softwareadvice.com','www.gartner.com','en.wikipedia.org','www.predictiveanalyticstoday.com','comparesoft.com',
            'technologyadvice.com','www.edsys.in','www.softwareadvisoryservice.com','www.trustradius.com','books.google.lk','www.noodle.com','www.researchgate.net','www.futurebridge.com','www.neoteryx.com','www.businesswire.com'
                                       ,'www.marketsandmarkets.com','www.ibisworld.com','www.slideshare.net','builtin.com']):
                continue
            sr = getGoogleLinksForSearchText(received_domains[k], 3, 'initial')
            if(len(sr)>0):
                print(sr[0])
                sr[0]['search_text'] = search_query
                try:
                    c_name = received_domains[k].split("www.")[1]
                except IndexError:
                    c_name = received_domains[k]
                if('.com' in c_name):
                    sr[0]['comp_name'] = c_name.split(".com")[0]
                elif('.org' in c_name):
                    sr[0]['comp_name'] = c_name.split(".org")[0]
                elif ('.co' in c_name):
                    sr[0]['comp_name'] = c_name.split(".co")[0]
                elif ('.edu' in c_name):
                    sr[0]['comp_name'] = c_name.split(".edu")[0]
                else:
                    sr[0]['comp_name'] = c_name
                print(sr[0])
                sr[0]['query_id'] = query_entry
                record_entry = db_collection.insert_one(sr[0])
                print("search record stored in db: ", record_entry.inserted_id)
                ids_list.append(record_entry.inserted_id)
            else:
                print("try again")
        print(ids_list)
        return ids_list
        # print("search records stored in db: ", record_entry.inserted_ids)
    else:
        print("No results found!")
        return None
    #store file to a csv file
    # with open('search_results.csv', mode='w',encoding='utf8') as results_file:  # store search results in to a csv file
    #     results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #
    #     for each_item in sr:
    #         results_writer.writerow([each_item['title'], each_item['link'], each_item['description']])
    #     results_file.close()




# mycol = refer_collection()
# search_a_company('TOOHEYS PTY LIMITED',mycol)
# search_a_company('CALTEX PETROLEUM PTY LTD',mycol)
# search_a_query('Digital advertisement and marketing analytics services company',5,mycol)