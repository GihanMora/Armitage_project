import json
import urllib.parse
from bson.json_util import loads
import pymongo
from pymongo import MongoClient

def refer_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient(
        "mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["simplified_dump_min"]  # creates a collection
    return mycol

collection_currency = refer_col()

with open('C:\Project_files\\armitage\\armitage_worker\Armitage_project\crawl_n_depth\Simplified_System\Database\out_json_simple.json') as f:
    fil = f.read().strip()
    file_data = loads(fil)

# if pymongo < 3.0, use insert()
# collection_currency.insert(file_data)
# # if pymongo >= 3.0 use insert_one() for inserting one document
# collection_currency.insert_one(file_data)
# if pymongo >= 3.0 use insert_many() for inserting many documents
collection_currency.insert_many(file_data)

# client.close()