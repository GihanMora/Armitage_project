#check mongo client string
#dump csv path

import pymongo
from bson import ObjectId
import csv


def refer_collection():
  # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  myclient = pymongo.MongoClient(
      "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
  # mydb = myclient["CompanyDatabase"]  # creates a database
  mydb = myclient["miner"]  # creates a database

  mycol = mydb["comp_data"]  # creates a collection
  return mycol

def refer_simplified_dump_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient(
        "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["simplified_dump"]  # creates a collection
    return mycol

def refer_query_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient(
        "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["search_queries"]  # creates a collection
    return mycol
# mycol = refer_query_col()
# mycol.delete_many({})

#display all existing records
def display_all_records():
  mycol = refer_collection()
  y=mycol.find()
  for k in y:
    print(k)
# display_all_records()

def get_all_ids():
    mycol = refer_collection()
    lst = []
    y = mycol.find()
    for k in y:
        lst.append(k['_id'])
        # print(k['_id'])
    print(lst)
# get_all_ids()
def clear_the_collection():
  mycol = refer_collection()
  mycol.delete_many({})
  print("collection is cleared!")
# clear_the_collection()


def export_profiles(id_list,query_id):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col()
    # store data in a csv file
    dump_name = 'F:\Armitage_project\crawl_n_depth\Simplified_System\end_to_end\data_dump\\'+str(query_id)+'_company_dump.csv'
    with open(dump_name, mode='w',encoding='utf8', newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        attributes_a = ['_id','search_text','title', 'link','description','rich_description','comp_name','addresses', 'emails',
                                 'social_media_links','telephone_numbers','kpe_results',
                                 'dnb_cp_info','oc_cp_info','linkedin_cp_info','comp_type_pred','company_size_li',
                                 'description_li','founded_li','headquarters_li','image_li','industry_li',
                        'name_li','num_employees_li','specialties_li','type_li','website_li','business_number_oc',
                        'company_number_oc','company_type_oc','incorporation_date_oc','jurisdiction_oc',
                        'registered_address_adr_oc','registry_page_oc','status_oc',
'agent_name','agent_address',
                                 'dissolution_date_oc', 'annual_return_last_made_up_date_oc', 'directors_or_officers_oc',
                                 'company_trade_name_dnb', 'company_address_dnb', 'company_summary_dnb',
                                 'company_web_dnb', 'company_tp_dnb', 'company_type_dnb',
                                 'company_related_industries_dnb', 'company_snapshot_dnb', 'company_revenue_dnb','company_contacts_dnb'
                                 ]
        results_writer.writerow(attributes_a)
        for entry_id in id_list:
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            data_list = []
            for each_a in attributes_a:
                try:
                    if((each_a=='addresses') or (each_a=='emails') or (each_a=='social_media_links') or (each_a=='telephone_numbers')):
                        data_list.append(data[0][each_a][:5])
                    elif((each_a=='wordcloud_results_tri')):
                        data_list.append(data[0][each_a][:10])
                    else:
                        data_list.append(data[0][each_a])
                except KeyError:
                        data_list.append('None')

            results_writer.writerow(data_list)
            dict_to_dump = {}
            for i in range(len(attributes_a)):
                dict_to_dump[attributes_a[i]]= data_list[i]
            # dict_to_dump = {'id':data[0]['_id'],
            #                 'search_text':data[0]['search_text'],
            #                 'title':data[0]['title'],
            #                 'link':data[0]['link'],
            #                 'description':data[0]['description'],
            #                 'Company Name':data[0]['comp_name'],
            #                 'addresses':data[0]['addresses'][:3],
            #                 'emails':data[0]['emails'][:3],
            #                 'social_media_links':data[0]['social_media_links'][:5],
            #                 'telephone_numbers':data[0]['telephone_numbers'][:5],
            #                 'tokens':data[0]['wordcloud_results_tri'][:10],
            #                 'contact_persons_dnb':data[0]['dnb_cp_info'],
            #                 'contact_persons_opencorporates':data[0]['oc_cp_info'],
            #                 'contact_persons_li':data[0]['linkedin_cp_info'],
            #                 'company type':data[0]['comp_type_pred']}
            record_entry = csv_dump_col.insert_one(dict_to_dump)
            print("simplified dump completed", record_entry.inserted_id)
        results_file.close()
    print("CSV export completed!")
# export_profiles([ObjectId('5eb3fe2233b62d98401f8944')],ObjectId('5eb3fde433b62d98401f8943'))

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
