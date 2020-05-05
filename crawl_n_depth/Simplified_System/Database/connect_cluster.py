import pymongo

myclient = pymongo.MongoClient("mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
mydb = myclient["miner"]  # creates a database
dblist = myclient.list_database_names()
print(dblist)#all databases
mycol = mydb["comp_data"]  # creates a collection
print(mydb.list_collection_names())
