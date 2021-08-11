import urllib

import pymongo
from bson import ObjectId
import sys
from os.path import dirname as up
import pandas as pd


three_up = up(up(up(__file__)))

sys.path.insert(0, three_up)
from Simplified_System.end_to_end.repair_profiles import get_entries_project
from Simplified_System.Database.db_connect import refer_collection,refer_query_col,simplified_export,simplified_export_via_queue,add_to_simplified_export_queue,refer_projects_col,simplified_export_with_sources_and_confidence
from Simplified_System.web_profile_data_crawler.avention_scraper import get_aven_data,add_to_avention_queue,get_aven_data_via_queue

def refer_collection():
  myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  # myclient = pymongo.MongoClient("mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
  # mydb = myclient["CompanyDatabase"]  # creates a database
  mydb = myclient["miner"]  # creates a database

  mycol = mydb["comp_data_cleaned"]  # creates a collection
  return mycol

mycol = refer_collection()
list_c = ['fujit','constructivesoftware','jonaspremier','webuildcs','mahi','clickhome','neointelligence','rendernetworks']

for comp in list_c:
    comp_res = mycol.find({"link" : {'$regex' : ".*"+comp+".*"}})
    data = [d for d in comp_res]
    print(comp)
    if(len(data)):
        print(data[0]['link'])
        print(data[0]['ignore_flag'])
    else:
        print('None')