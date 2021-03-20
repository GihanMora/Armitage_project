import urllib.parse

import pymongo



def refer_projects_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient(
        "mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["projects"]  # creates a collection
    return mycol

print(refer_projects_col())

# Collection(Database(MongoClient(host=['armitage-shard-00-02.bw3vp.mongodb.net:27017', 'armitage-shard-00-00.bw3vp.mongodb.net:27017', 'armitage-shard-00-01.bw3vp.mongodb.net:27017'], document_class=dict, tz_aware=False, connect=True, retrywrites=True, w='majority', authsource='admin', replicaset='atlas-2r3qr6-shard-0', ssl=True), 'miner'), 'projects')
