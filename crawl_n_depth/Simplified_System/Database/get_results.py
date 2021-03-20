import urllib.parse

import pymongo
from bson import ObjectId


def refer_collection():
  myclient = pymongo.MongoClient("mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
  # myclient = pymongo.MongoClient(
  #     "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
  # mydb = myclient["CompanyDatabase"]  # creates a database
  mydb = myclient["miner"]  # creates a database

  mycol = mydb["comp_data_cleaned"]  # creates a collection
  return mycol

def refer_simplified_dump_col_min():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient("mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["simplified_dump_min"]  # creates a collection
    return mycol

def refer_query_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient(
        "mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["search_queries"]  # creates a collection
    return mycol


def get_results_for_a_query(query_id):
    mycol = refer_collection()
    comp_data_entry = mycol.find({"query_id": query_id})
    mapped_entries = []
    for k in comp_data_entry:
        print(k['_id'])
        mapped_entries.append(ObjectId(k['_id']))
        # data = [i for i in k]
        # print(data['_id'])
    # print(list(comp_data_entry))
    return mapped_entries


get_results_for_a_query(ObjectId('5f183d6c464603f10dce0d9c'))
idss = [ObjectId('5f183d6c464603f10dce0d9c'),ObjectId('5f186b1db448d46665f7fefd'),ObjectId('5f187416182dbb7a59a62638'),ObjectId('5f18829b35a2278f64f9e5e1'),ObjectId('5f188b6035a2278f64f9e603'),ObjectId('5f18949c35a2278f64f9e635'),ObjectId('5f189c9635a2278f64f9e666'),ObjectId('5f18ebc835a2278f64f9e6a2'),ObjectId('5f18ed7035a2278f64f9e6cc'),ObjectId('5f1906135fe76f8f85f401eb')]

entire_l = []
for k in idss:
    entire_l.extend(get_results_for_a_query(k))

print(entire_l)