import sys
from datetime import datetime
from bson import ObjectId
import csv
import json
import os
import time
import pymongo

from os.path import dirname as up
three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)
from Simplified_System.Initial_Crawling.get_n_search_results import getGoogleLinksForSearchText
from Simplified_System.Database.db_connect import refer_collection,is_profile_exist,refer_query_col


def search_a_query(search_query,number_of_results,db_collection,query_entry):

    try:
        with open('check_relevence_risk_rich_1.csv', mode='w', encoding='utf8',
                  newline='') as results_file:  # store search results in to a csv file
            results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            attributes_a = ['search_text', 'title', 'link', 'description','rich_description', 'comp_name', 'match_count']
            results_writer.writerow(attributes_a)
            sr = getGoogleLinksForSearchText(search_query, number_of_results, 'normal')
            # print('sr',sr)
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
                print("received_domains_no_duplicates", received_domains)
                ids_list=[]
                for k in range(len(received_domains)):
                    print("*****")
                    time.sleep(10)
                    print(received_links[k],received_domains[k])
                    b_list_file = open(three_up+'//Simplified_System//Initial_Crawling//black_list.txt','r')
                    black_list = b_list_file.read().splitlines()
                    if(received_domains[k] in black_list):#filter non wanted websites
                        print("skipping as included in blacklist")
                        continue
                    if (('.gov.' in received_domains[k]) or ('.govt.' in received_domains[k]) or ('.edu.' in received_domains[k]) or ('.uk' in received_domains[k]) ):  # filter non wanted websites
                        print("skipping as govt site")
                        continue
                    sr = getGoogleLinksForSearchText(received_domains[k], 3, 'initial')
                    if (len(sr) == 0):
                        sr = getGoogleLinksForSearchText(received_domains[k], 3, 'initial')
                        if (len(sr) == 0):
                            sr = getGoogleLinksForSearchText(received_domains[k], 3, 'initial')
                    if(len(sr)>0):
                        print(sr[0])
                        res_data = is_profile_exist(sr[0]['link'])
                        if (len(res_data)):
                            print("Profile " + sr[0]['link'] + " already existing at " + str(res_data[0]['_id']))
                            #updating associates
                            # query_collection = refer_query_col()
                            # qq_data_entry = query_collection.find({"_id": query_entry})
                            # qq_data = [i for i in qq_data_entry]
                            # qq_attribute_keys = list(qq_data[0].keys())
                            # if ('associated_entries' in qq_attribute_keys):
                            #     print('in main',)
                            #     query_collection.update_one({'_id': query_entry},
                            #                                 {'$set': {
                            #                                     'associated_entries': qq_data[0]['associated_entries'] +
                            #                                         [res_data[0]['_id']]}})
                            # else:
                            #     query_collection.update_one({'_id': query_entry},
                            #                                 {'$set': {'associated_entries': [res_data[0]['_id']]}})
                            # continue
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
                        print("search_text",sr[0]['search_text'])
                        print("rich_description",sr[0]['rich_description'])
                        print("selected_result ",sr[0])
                        s_text_fixed = sr[0]['search_text'].replace('australia','')
                        print('filtered', s_text_fixed)
                        match_count = calculate_score(s_text_fixed,sr[0]['rich_description'])
                        results_writer.writerow([sr[0]['search_text'],sr[0]['title'],sr[0]['link'],sr[0]['description'],sr[0]['rich_description'],sr[0]['comp_name'],match_count])
                        # sr[0]['query_id'] = query_entry
                        # record_entry = db_collection.insert_one(sr[0])
                        # print("search record stored in db: ", record_entry.inserted_id)
                        # ids_list.append(record_entry.inserted_id)
                    else:
                        print("Cannot find results, skipping company")
                print(ids_list)
                results_file.close()
                return ids_list
                # print("search records stored in db: ", record_entry.inserted_ids)
            else:
                print("No results found!")
                return None
    except Exception as e:
        print("Error occured! try again", e)
        return 'error'

def calculate_score(search_text,description):
    search_tokens = search_text.lower().strip().split(" ")
    description_tokens = description.lower().strip().split(" ")
    match_count = 0
    for each_search_token in search_tokens:
        match_count+= description_tokens.count(each_search_token)
        # print(each_search_token,description_tokens.count(each_search_token))
    return match_count
started = datetime.now()
search_a_query('hazard management software australia',100,'sss','sss')
ended = datetime.now()
duration = ended-started
print(duration)