#make sure black_list.txt path is correct
#fix sys path if you want to run this seperately
import sys

from bson import ObjectId

sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
from Simplified_System.Initial_Crawling.get_n_search_results import getGoogleLinksForSearchText

import csv
import json
import os
import time
import pymongo
from Simplified_System.Database.db_connect import refer_collection,is_profile_exist
# from ..Database.db_connect import refer_collection

def search_a_company_alpha(comp_name, db_collection, query_entry,c_name):
    sr = getGoogleLinksForSearchText(comp_name, 3, 'normal')
    count = 0
    while (sr == 'captcha'):
        count = count + 1
        print('captch detected and sleeping for n times n:', count)
        time.sleep(1200 * count)
        sr = getGoogleLinksForSearchText(comp_name, 3, 'normal')

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

        res_data = is_profile_exist(filtered_sr[0]['link'])

        if (len(res_data)):
            print("Profile " + filtered_sr[0]['link'] + " already existing at " + str(res_data[0]['_id']))
            return 'exist'

        filtered_sr[0]['comp_name'] = c_name
        filtered_sr[0]['query_id'] = query_entry
        record_entry=db_collection.insert_one(filtered_sr[0])
        print(filtered_sr[0])
        print("search record stored in db: ",record_entry.inserted_id)
        return record_entry.inserted_id
    else:
        print("No results found!")
        return None



def search_a_company(comp_name, db_collection, query_entry):
    try:
        sr = getGoogleLinksForSearchText(comp_name+" Australia", 5, 'normal')
        count = 0
        while (sr == 'captcha'):
            count = count + 1
            print('captch detected and sleeping for n times n:', count)
            time.sleep(1200 * count)
            sr = getGoogleLinksForSearchText(comp_name, 5, 'normal')

        b_list_file = open('F:\Armitage_project\crawl_n_depth\Simplified_System\Initial_Crawling\\black_list.txt','r')
        black_list = b_list_file.read().splitlines()
        # 'www.dnb.com'
        received_links = [i['link'] for i in sr]
        print(received_links)
        #filter the links
        filtered_sr_a = []
        filtered_received_links = []
        for i,each_l in enumerate(received_links):
            if (('.com/' in each_l) or ('.education/' in each_l) or ('.io/' in each_l) or ('.com.au/' in each_l) or (
                    '.net/' in each_l) or ('.org/' in each_l) or ('.co.nz/' in each_l) or ('.nz/' in each_l) or (
                    '.au/' in each_l) or ('.biz/' in each_l)):
                # print(each)
                filtered_received_links.append(each_l)
                filtered_sr_a.append(sr[i])

        print(filtered_sr_a)
        received_domains = [i.split("/")[2] for i in filtered_received_links]
        filtered_sr = []

        print('rd', received_domains)
        for i, each in enumerate(received_domains):
            # print(each)
            if (('.gov.' in each) or ('.govt.' in each) or ('.edu.' in each) or ('.uk' in each)):  # filter non wanted websites
                continue
            if each not in black_list:
                filtered_sr.append(filtered_sr_a[i])

        if(len(filtered_sr)):
            #is the link already taken
            res_data =is_profile_exist(filtered_sr[0]['link'])

            if(len(res_data)):
                print("Profile "+filtered_sr[0]['link']+" already existing at "+str(res_data[0]['_id']))
                return 'exist'
            #should fix comp name
            # print('fixing comp name')
            c_n_link = filtered_sr[0]['link']
            c_n_dom = c_n_link.split("/")[2]
            try:
                c_name = c_n_dom.split("www.")[1]
            except IndexError:
                c_name = c_n_dom
            if ('.com' in c_name):
                cc_name = c_name.split(".com")[0]
            elif ('.org' in c_name):
                cc_name = c_name.split(".org")[0]
            elif ('.io' in c_name):
                cc_name = c_name.split(".io")[0]
            elif ('.net' in c_name):
                cc_name = c_name.split(".net")[0]
            else:
                cc_name = c_name
            # print(filtered_sr[0]['link'])
            filtered_sr[0]['comp_name'] = cc_name
            filtered_sr[0]['query_id'] = query_entry
            record_entry=db_collection.insert_one(filtered_sr[0])
            print(filtered_sr[0])
            print("search record stored in db: ",record_entry.inserted_id)
            return record_entry.inserted_id
        else:
            print("No results found!")
            return None
    except Exception as e:
        print("Error occured! try again",e)
        return 'error'


    #store data in a csv file
    # with open('search_results.csv', mode='w',encoding='utf8') as results_file:  # store search results in to a csv file
    #     results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     # print(filtered_sr[0])
    #     for each_item in filtered_sr:
    #         results_writer.writerow([each_item['title'], each_item['link'], each_item['description']])
    #         break
    #     results_file.close()


def update_a_company(comp_name, db_collection, entry_id):
    print(entry_id)
    sr = getGoogleLinksForSearchText(comp_name, 50, 'normal')
    count = 0
    while (sr == 'captcha'):
        count = count + 1
        print('captch detected and sleeping for n times n:', count)
        time.sleep(1200 * count)
        sr = getGoogleLinksForSearchText(comp_name, 50, 'normal')

    b_list_file = open('F:\Armitage_project\crawl_n_depth\Simplified_System\Initial_Crawling\\black_list.txt','r')
    black_list = b_list_file.read().splitlines()
    # 'www.dnb.com'
    received_links = [i['link'] for i in sr]
    print(received_links)
    #filter the links
    filtered_received_links = []
    filtered_sr_a = []
    for i,each_l in enumerate(received_links):
        if (('.com/' in each_l) or ('.education/' in each_l) or ('.io/' in each_l) or ('.com.au/' in each_l) or (
                '.net/' in each_l) or ('.org/' in each_l) or ('.co.nz/' in each_l) or ('.nz/' in each_l) or (
                '.au/' in each_l) or ('.biz/' in each_l)):
            # print(each)
            filtered_received_links.append(each_l)
            filtered_sr_a.append(sr[i])

    print(filtered_received_links)
    print(filtered_sr_a)
    received_domains = [i.split("/")[2] for i in filtered_received_links]
    filtered_sr = []

    print('rd', received_domains)
    for i, each in enumerate(received_domains):
        print(each)
        if (('.gov.' in each) or ('.govt.' in each) or ('.edu.' in each) or ('.uk' in each)):  # filter non wanted websites
            continue
        if each not in black_list:
            filtered_sr.append(filtered_sr_a[i])

    if(len(filtered_sr)):
        #is the link already taken
        res_data =is_profile_exist(filtered_sr[0]['link'])
        print('sss',filtered_sr[0])

        if(len(res_data)):
            print("Profile "+filtered_sr[0]['link']+" already existing at "+str(res_data[0]['_id']))
            return 'exist'

        filtered_sr[0]['comp_name'] = filtered_sr[0]['search_text']
        # filtered_sr[0]['query_id'] = query_entry

        db_collection.update_one({'_id': ObjectId(entry_id)}, {'$set': filtered_sr[0]})
        # record_entry=db_collection.insert_one(filtered_sr[0])
        print(filtered_sr[0])
        print("search record stored in db updated ")
        print(entry_id)
        return entry_id
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
# search_a_company('https://courselink.uoguelph.ca/','col','121')

def search_a_query(search_query,number_of_results,db_collection,query_entry):
    try:
        sr = getGoogleLinksForSearchText(search_query, number_of_results, 'normal')
        count = 0
        while (sr == 'captcha'):
            count = count + 1
            print('captch detected and sleeping for n times n:', count)
            time.sleep(1200 * count)
            sr = getGoogleLinksForSearchText(search_query, number_of_results, 'normal')

        if (len(sr)):
            # print(sr)
            # record_entry = db_collection.insert_many(sr)

            for each_sr in sr:
                print(each_sr)
            received_links = [i['link'] for i in sr]
            filtered_received_links = []
            for each_l in received_links:
                if (('.com/' in each_l) or ('.education/' in each_l) or ('.io/' in each_l) or ('.com.au/' in each_l) or (
                        '.net/' in each_l) or ('.org/' in each_l) or ('.co.nz/' in each_l) or ('.nz/' in each_l) or (
                        '.au/' in each_l) or ('.biz/' in each_l)):
                    # print(each)
                    filtered_received_links.append(each_l)


            received_domains = [i.split("/")[2] for i in filtered_received_links]
            print("received_domains",received_domains)
            received_domains = list(set(received_domains))
            print("received_domains", received_domains)
            ids_list=[]
            for k in range(len(received_domains)):
                time.sleep(10)
                print(received_links[k],received_domains[k])
                b_list_file = open('F:\Armitage_project\crawl_n_depth\Simplified_System\Initial_Crawling\\black_list.txt','r')
                black_list = b_list_file.read().splitlines()
                if(received_domains[k] in black_list):#filter non wanted websites
                    continue
                if (('.gov.' in received_domains[k]) or ('.govt.' in received_domains[k]) or ('.edu.' in received_domains[k]) or ('.uk' in received_domains[k]) ):  # filter non wanted websites
                    continue
                sr = getGoogleLinksForSearchText(received_domains[k], 3, 'normal')
                if (len(sr) == 0):
                    sr = getGoogleLinksForSearchText(received_domains[k], 3, 'normal')
                    if (len(sr) == 0):
                        sr = getGoogleLinksForSearchText(received_domains[k], 3, 'normal')
                if(len(sr)>0):
                    print(sr[0])
                    res_data = is_profile_exist(sr[0]['link'])
                    if (len(res_data)):
                        print("Profile " + sr[0]['link'] + " already existing at " + str(res_data[0]['_id']))
                        continue
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
                    print("Cannot find results, skipping company")
            print(ids_list)
            return ids_list
            # print("search records stored in db: ", record_entry.inserted_ids)
        else:
            print("No results found!")
            return None
    except Exception as e:
        print("Error occured! try again", e)
        return 'error'

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