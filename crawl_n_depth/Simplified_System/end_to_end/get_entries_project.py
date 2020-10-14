import pymongo
from bson import ObjectId

def refer_projects_col():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    # myclient = pymongo.MongoClient(
    #     "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["projects"]  # creates a collection
    return mycol

def refer_simplified_dump_col_min():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    # myclient = pymongo.MongoClient(
    #     "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["simplified_dump_min"]  # creates a collection
    return mycol

def refer_query_col():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    # myclient = pymongo.MongoClient(
    #     "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["search_queries"]  # creates a collection
    return mycol

def refer_collection():
  myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  # myclient = pymongo.MongoClient(
  #     "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
  # mydb = myclient["CompanyDatabase"]  # creates a database
  mydb = myclient["miner"]  # creates a database

  mycol = mydb["comp_data_cleaned"]  # creates a collection
  return mycol

def get_entries_project(project_id):
    all_entires = []
    profile_col = refer_collection()
    projects_col= refer_projects_col()
    query_collection = refer_query_col()
    proj_data_entry = projects_col.find({"_id": project_id})
    print('proj',proj_data_entry)
    proj_data = [i for i in proj_data_entry]
    print('data',len(proj_data))
    proj_attribute_keys = list(proj_data[-1].keys())
    if ('associated_queries' in proj_attribute_keys):
        associated_queries = proj_data[-1]['associated_queries']
        for each_query in associated_queries:
            query_data_entry = query_collection.find({"_id": ObjectId(each_query)})
            query_data = [i for i in query_data_entry]
            print([query_data[0]['search_query'],query_data[0]['state'],query_data[0]['_id']])
            query_attribute_keys = list(query_data[0].keys())
            if ('associated_entries' in query_attribute_keys):
                associated_entries = query_data[0]['associated_entries']
                # print('kk',associated_entries)
                obs_ids = [ObjectId(i) for i in associated_entries]
                all_entires.extend(obs_ids)
                # completed_count = 0
                # incomplete_count = 0
                # incompletes = []
                # problems = []
                # for k in obs_ids:
                #     prof_data_entry = profile_col.find({"_id": k})
                #     # print('proj', proj_data_entry)
                #     prof_data = [i for i in prof_data_entry]
                #     prof_attribute_keys = list(prof_data[0].keys())
                #
                #     if ('simplified_dump_state' in prof_attribute_keys):
                #         if(prof_data[0]['simplified_dump_state']=='Completed'):
                #             completed_count+=1
                #         # else:print(prof_data[0]['simplified_dump_state'])
                #         elif (prof_data[0]['simplified_dump_state'] == 'Incomplete'):
                #             incomplete_count+= 1
                #             incompletes.append(k)
                #         else:
                #             problems.append(k)
                #     else:
                #         problems.append(k)
                #
                # print(['completed',completed_count,'all',len(obs_ids),'incompleted',incomplete_count,incompletes,'prob',problems])
                # # filt = []
                # # for k in obs_ids:
                # #     if(k not in problems):
                # #         filt.append(k)
                # # print('filt',filt)
                # if(completed_count==len(obs_ids)):
                #     query_collection.update_one({'_id': ObjectId(each_query)}, {'$set': {'state': 'Completed'}})

                # return obs_ids

        all_entires = list(set(all_entires))
        return all_entires
    else:
        print("This project do not have any queries yet")
        return []


# print(get_entries_project(ObjectId('5f7558e6fce4b64506137661')))