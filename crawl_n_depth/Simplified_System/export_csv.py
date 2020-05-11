#check mongo client string
#check dump csv path

import pymongo
from bson import ObjectId
import csv


def refer_collection():
  myclient = pymongo.MongoClient("mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
  mydb = myclient["miner"]  # creates a database
  mycol = mydb["simplified_dump"]  # creates a collection
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
    dump_name = 'company_dump.csv'
    with open(dump_name, mode='w',encoding='utf8', newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        attributes_a = ['_id','search_text','title', 'link','description','rich_description','comp_name','addresses', 'emails',
                                'social_media_links','telephone_numbers','kpe_results',
                                'dnb_cp_info','oc_cp_info','linkedin_cp_info','comp_type_pred','company_size_li',
                                'description_li','founded_li','headquarters_li','image_li','industry_li',
                                 'name_li','num_employees_li','specialties_li','type_li','website_li','business_number_oc',
                                 'company_number_oc','company_type_oc','incorporation_date_oc','jurisdiction_oc',
                                 'registered_address_adr_oc','registry_page_oc','status_oc','agent_name','agent_address',
                                 'dissolution_date_oc', 'annual_return_last_made_up_date_oc', 'directors_or_officers_oc',
                                 'company_trade_name_dnb', 'company_address_dnb', 'company_summary_dnb',
                                 'company_web_dnb', 'company_tp_dnb', 'company_type_dnb',
                                 'company_related_industries_dnb', 'company_snapshot_dnb', 'company_revenue_dnb','company_contacts_dnb' ]
        results_writer.writerow(attributes_a)
        for i,entry_id in enumerate(id_list):
            print("dumping record",i)
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            data_list = []
            for each_a in attributes_a:
                try:
                    if((each_a=='addresses') or (each_a=='emails') or (each_a=='social_media_links') or (each_a=='telephone_numbers')):
                        data_list.append(data[0][each_a][:5])#truncating addresses
                    elif((each_a=='wordcloud_results_tri')):
                        data_list.append(data[0][each_a][:10])#trucating tokens
                    else:
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



#give ids in simplified_dump collection.
# export_profiles([ObjectId('5eb44a5818e5aaac743c1e50'),ObjectId('5eb44c3386ed61b292cd7528')])

#to export all records
# export_all()