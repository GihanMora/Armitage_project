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


def search_a_company(comp_name, db_collection, query_entry):
    try:
        with open('for_non_listing_websites.csv', mode='w', encoding='utf8',
                  newline='') as results_file:  # store search results in to a csv file
            results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            attributes_a = ['search_text', 'title', 'link', 'description', 'rich_description', 'comp_name']
            results_writer.writerow(attributes_a)
            f = open('not_found.txt','r')
            for k in range(20):
                row = f.readline().strip()
                print(row)
                sr = getGoogleLinksForSearchText(row+" Australia", 5, 'initial')
                if (len(sr) == 0):
                    sr = sr = getGoogleLinksForSearchText(row+" Australia", 5, 'initial')
                    if (len(sr) == 0):
                        sr = sr = getGoogleLinksForSearchText(row+" Australia", 5, 'initial')
                count = 0
                while (sr == 'captcha'):
                    count = count + 1
                    print('captch detected and sleeping for n times n:', count)
                    time.sleep(1200 * count)
                    sr = getGoogleLinksForSearchText(comp_name, 5, 'normal')
                print(sr[0])
                results_writer.writerow([sr[0]['search_text'], sr[0]['title'], sr[0]['link'], sr[0]['description'],sr[0]['rich_description']])
            results_file.close()



    except Exception as e:
        print("Error occured! try again",e)
        return 'error'

search_a_company('ss','ss','ss')