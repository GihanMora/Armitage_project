
import sys
import urllib.parse

from os.path import dirname as up

import pymongo
from bson import ObjectId

three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)

# link_list = []
#
# f = open("C:\\Project_files\\armitage\\armitage_worker\\Armitage_project_v1\\crawl_n_depth\\Simplified_System\\Database\\links_fm.txt","r")
# for k in f.readlines():
#     link_list.append(k.strip())
def refer_projects_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient("mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["projects"]  # creates a collection
    return mycol

def refer_query_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient("mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["search_queries"]  # creates a collection
    return mycol

def get_entries_project(project_id):
    projects_col= refer_projects_col()
    query_collection = refer_query_col()
    proj_data_entry = projects_col.find({"_id": project_id})

    print('proj',proj_data_entry)
    proj_data = [i for i in proj_data_entry]
    print('data',len(proj_data))
    print('project_id',project_id)
    selected_project = proj_data[-1]
    # if(proj_data[0]['project_name']=='NDIS & community care software'):
    #     for k in proj_data:
    #         if(k['_id']==ObjectId('5f7558e6fce4b64506137661')):
    #             selected_project= k


    # print('projs',[proj_data[-1],proj_data[0]])
    # proj_attribute_keys = list(proj_data[-1].keys())
    proj_attribute_keys = list(selected_project.keys())
    assosiated_profiles = []
    if ('associated_queries' in proj_attribute_keys):
        # associated_queries = proj_data[-1]['associated_queries']
        associated_queries = selected_project['associated_queries']
        print('associated_queries',associated_queries)
        for each_query in associated_queries:

            query_data_entry = query_collection.find({"_id": ObjectId(each_query)})
            query_data = [i for i in query_data_entry]
            query_attribute_keys = list(query_data[0].keys())
            if ('associated_entries' in query_attribute_keys):
                associated_entries = query_data[0]['associated_entries']
                # print('kk',associated_entries)
                obs_ids = [ObjectId(i) for i in associated_entries]
                assosiated_profiles.extend(obs_ids)
        print('done')



    else:
        print("This project do not have any queries yet")
    # f = open('check.txt','w+')
    # print('all',len(associated_entries))
    # print('unique',len(associated_entries))
    # f.write('all'+str(len(assosiated_profiles))+'\\n')
    # f.write('unique' + str(len(set(assosiated_profiles))))
    # f.close()
    return assosiated_profiles



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
print(get_entries_project(ObjectId('60cf5241df8355fbc5544a6c')))