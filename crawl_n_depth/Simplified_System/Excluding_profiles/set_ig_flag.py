
import sys
import urllib.parse

from os.path import dirname as up

import pymongo

three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)

# link_list = []
#
# f = open("C:\\Project_files\\armitage\\armitage_worker\\Armitage_project_v1\\crawl_n_depth\\Simplified_System\\Database\\links_fm.txt","r")
# for k in f.readlines():
#     link_list.append(k.strip())

def refer_collection():
  # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  myclient = pymongo.MongoClient(
      "mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
  # mydb = myclient["CompanyDatabase"]  # creates a database
  mydb = myclient["miner"]  # creates a database

  mycol = mydb["comp_data_cleaned"]  # creates a collection
  return mycol

def adding_ig(link_list):

    mycol = refer_collection()
    for id_a in link_list:
        entry = mycol.find({"link": id_a})
        data = [d for d in entry]
        print(data[0]['_id'],data[0]['link'])
        mycol.update_one({"link": id_a}, {'$set': {'ignore_flag': '1'}})


# adding_ig(link_list)