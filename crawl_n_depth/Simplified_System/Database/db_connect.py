import pymongo
from bson import ObjectId



def refer_collection():
  myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  mydb = myclient["CompanyDatabase"]  # creates a database
  mycol = mydb["comp_data"]  # creates a collection
  return mycol
mycol = refer_collection()
# mycol.delete_many({})

#display all existing records
def display_all_records():
  y=mycol.find()
  for k in y:
    print(k)
# display_all_records()

def clear_the_collection():
  mycol = refer_collection()
  mycol.delete_many({})
  print("collection is cleared!")

# clear_the_collection()



# mydb = myclient["mydatabase"]#creates a database
# mycol = mydb["customers"]#creates a collection
# myusers = mydb["users"]
# #
# mydict = { "name": [], "address": [] }#data should be in a dictionary format
# # myuin = { "name": "user", "address": "user address 123" }#data should be in a dictionary format
# #
# # myusers.insert_one(myuin)
# x = mycol.insert_one(mydict)
# print(x.inserted_id)
# y= mycol.find()
# for k in y:
#     print(k)
#
# # n_depth_data = {'crawled_links': ["sss","12121","sasasas"], 'header_text': [], 'paragraph_text': [], 'emails': [], 'addresses': [], 'social_media_links': [], 'telephone_numbers': []}
# # mycol.update_one({'_id': ObjectId('5ea103df1b02e3ee52d87988')},
# #                          {'$set': n_depth_data})
# # mycol.insert_one(n_depth_data)
# # mycol.update_one({'_id' : x.inserted_id},
# #                      {'$set' : {'new_attr' : "attry new" }})
# #
# y= mycol.find()
# for k in y:
#     print(k)
# # # mylist = [
# # #   { "_id": 1, "name": "John", "address": "Highway 37"},
# # #   { "_id": 2, "name": "Peter", "address": "Lowstreet 27"},
# # #   { "_id": 3, "name": "Amy", "address": "Apple st 652"},
# # #   { "_id": 4, "name": "Hannah", "address": "Mountain 21"},
# # #   { "_id": 5, "name": "Michael", "address": "Valley 345"},
# # #   { "_id": 6, "name": "Sandy", "address": "Ocean blvd 2"},
# # #   { "_id": 7, "name": "Betty", "address": "Green Grass 1"},
# # #   { "_id": 8, "name": "Richard", "address": "Sky st 331"},
# # #   { "_id": 9, "name": "Susan", "address": "One way 98"},
# # #   { "_id": 10, "name": "Vicky", "address": "Yellow Garden 2"},
# # #   { "_id": 11, "name": "Ben", "address": "Park Lane 38"},
# # #   { "_id": 12, "name": "William", "address": "Central st 954"},
# # #   { "_id": 13, "name": "Chuck", "address": "Main Road 989"},
# # #   { "_id": 14, "name": "Viola", "address": "Sideway 1633"}
# # # ]
# # # x = mycol.insert_many(mylist)
# # # print(x.inserted_ids)
# #
# # # y = mycol.find_one()
# # # y = mycol.find()
# # # print(y.count())
# # # for k in y:
# # #     print(k)
# # # for x in mycol.find({},{ "address": 0 }):#0 if not required, 1 if required
# # #   print(x)
# #
# # # myquery = { "address": "Park Lane 38" }
# # #
# # # mydoc = mycol.find(myquery)
# # #
# # # for x in mydoc:
# # #   print(x)
# #
# # # myquery = { "address": { "$gt": "S" } }
# # #
# # # mydoc = mycol.find(myquery)
# # #
# # # for x in mydoc:
# # #   print(x)
# # #find with regex
# # # myquery = { "address": { "$regex": "^M" } }
# # #
# # # mydoc = mycol.find(myquery)
# # #
# # # for x in mydoc:
# # #   print(x)
# # #delete entries
# # # myquery = { "address": "Mountain 21" }
# # #
# # # mycol.delete_one(myquery)
# #
# # #check the database existance
# # # dblist = myclient.list_database_names()
# # # # print(dblist)#all databases
# # # if "mydatabase" in dblist:
# # #   print("The database exists.")
# # #
# # #
# # # #check the collection existance
# # # print(mydb.list_collection_names())
# # # # myusers.drop() dropping the collection
# # # print(mydb.list_collection_names())
# # # collist = mydb.list_collection_names()
# # #
# # # if "customers" in collist:
# # #   print("The collection exists.")
# #
