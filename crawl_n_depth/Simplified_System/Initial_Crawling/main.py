from get_n_search_results import getGoogleLinksForSearchText
import csv
import json
import os
import time
import pymongo

from crawl_n_depth.Simplified_System.Database.db_connect import refer_collection


def search_a_company(comp_name, db_collection):
    sr = getGoogleLinksForSearchText(comp_name, 3)
    count = 0
    while (sr == 'captcha'):
        count = count + 1
        print('captch detected and sleeping for n times n:', count)
        time.sleep(1200 * count)
        sr = getGoogleLinksForSearchText(comp_name, 3)

    b_list_file = open('black_list.txt','r')
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
        record_entry=db_collection.insert_one(filtered_sr[0])
        print(filtered_sr[0])
        print("search record stored in db: ",record_entry.inserted_id)
    else:
        print("No results found!")

    #store data in a csv file
    # with open('search_results.csv', mode='w',encoding='utf8') as results_file:  # store search results in to a csv file
    #     results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     # print(filtered_sr[0])
    #     for each_item in filtered_sr:
    #         results_writer.writerow([each_item['title'], each_item['link'], each_item['description']])
    #         break
    #     results_file.close()


def search_a_query(comp_name,number_of_results,db_collection):
    sr = getGoogleLinksForSearchText(comp_name, number_of_results)
    count = 0
    while (sr == 'captcha'):
        count = count + 1
        print('captch detected and sleeping for n times n:', count)
        time.sleep(1200 * count)
        sr = getGoogleLinksForSearchText(comp_name, 3)

    if (len(sr)):
        # print(sr)
        record_entry = db_collection.insert_many(sr)
        for each_sr in sr:
            print(each_sr)
        print("search records stored in db: ", record_entry.inserted_ids)
    else:
        print("No results found!")
    #store file to a csv file
    # with open('search_results.csv', mode='w',encoding='utf8') as results_file:  # store search results in to a csv file
    #     results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #
    #     for each_item in sr:
    #         results_writer.writerow([each_item['title'], each_item['link'], each_item['description']])
    #     results_file.close()




mycol = refer_collection()
search_a_company('TOOHEYS PTY LIMITED',mycol)
search_a_company('CALTEX PETROLEUM PTY LTD',mycol)
# search_a_query('Education Systems Australia',3,mycol)