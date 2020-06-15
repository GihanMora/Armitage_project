import pymongo
from bson import ObjectId
from Simplified_System.Database.db_connect import refer_collection
from Simplified_System.Initial_Crawling.get_n_search_results import getGoogleLinksForSearchText




def get_li_emp(entry_id,mode):
    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    # comp_name = data[0]['search_text']
    try:
        if mode=='comp':
            comp_name = data[0]['search_text']
        elif mode == 'query':
            comp_name = data[0]['comp_name']
    except KeyError:
        comp_name = data[0]['link'].split("/")[2]

    sr = getGoogleLinksForSearchText('"' + comp_name + '"' + " manager linkedin australia or newzealand", 10, 'normal')
    if(len(sr)==0):
        sr = getGoogleLinksForSearchText('"' + comp_name + '"' + " manager linkedin australia or newzealand", 10,
                                         'normal')
        if(len(sr)==0):
            sr = getGoogleLinksForSearchText('"' + comp_name + '"' + " manager linkedin australia or newzealand", 10,
                                             'normal')
    filtered_li = []
    for p in sr:
        if 'linkedin.com' in p['link']:
            filtered_li.append([p['title'], p['link']])
    if(len(filtered_li)):
        print(filtered_li)
        mycol.update_one({'_id': entry_id},
                         {'$set': {'linkedin_cp_info': filtered_li}})
        print("Successfully extended the data entry with linkedin contact person data", entry_id)
    else:
        print("No linkedin contacts found!, Try again")
        mycol.update_one({'_id': entry_id},
                         {'$set': {'linkedin_cp_info': []}})
