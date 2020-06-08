#check mongo client string
#check dump csv path

import pymongo
from bson import ObjectId
import csv


def refer_collection():
  myclient = pymongo.MongoClient("mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
  mydb = myclient["miner"]  # creates a database
  mycol = mydb["simplified_dump_min"]  # creates a collection
  return mycol


def get_all_ids():
    mycol = refer_collection()
    lst = []
    y = mycol.find()
    for k in y:
        lst.append(k['_id'])
    return lst

#this function will export csv given list of ids
def export_profiles(id_list):
    mycol = refer_collection()
    # store data in a csv file
    dump_name = 'company_dump_min.csv'
    with open(dump_name, mode='w',encoding='utf8', newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)


        attributes_a = ['_id','search_text','title','link'
        ,'description','comp_name','email','keywords'
        ,'founded_year','revenue'
        ,'funding','No_of_employees','headquarters'
        ,'telephone_number','contact_person'
        ,'address','type_or_sector']

        results_writer.writerow(attributes_a)
        for i,entry_id in enumerate(id_list):
            print("dumping record",i)
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            data_list = []
            for each_a in attributes_a:
                try:
                    data_list.append(data[0][each_a])#do not trunctate anything else
                except KeyError:
                        data_list.append('None')#If data not there mark it as none

            results_writer.writerow(data_list)
        results_file.close()
    print("CSV export completed!")


#this will export all records in collection
def export_all():
    all_ids = get_all_ids()
    print(len(all_ids),"records received")
    print(all_ids)
    export_profiles(all_ids)

export_all()

#give ids in simplified_dump collection.
# export_profiles([ObjectId('5eb44a5818e5aaac743c1e50'),ObjectId('5eb44c3386ed61b292cd7528')])

#to export all records
# export_all()