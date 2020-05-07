import sys
import threading
import time

from bson import ObjectId

sys.path.insert(0, 'F:\Armitage_project\crawl_n_depth\\')

from datetime import datetime
from Simplified_System.Initial_Crawling.main import search_a_company,search_a_query
from Simplified_System.Deep_Crawling.main import deep_crawl
from Simplified_System.Database.db_connect import refer_collection,export_profiles,refer_query_col
from Simplified_System.Feature_Extraction.main import extract_features
from Simplified_System.Extract_contact_persons.main import extract_contact_persons
from Classification.predict_class import predict_class_tags
from Simplified_System.web_profile_data_crawler.scrape_dnb import get_dnb_data
from Simplified_System.web_profile_data_crawler.scrape_oc import get_oc_data
from Simplified_System.linkedin_data_crawler.linkedin_crawling import get_li_data
# # from crawl_n_depth.Simplified_System.Deep_Crawling.main import deep_crawl

# from Feature_Extraction.main import extract_features

# from crawl_n_depth.spiders.n_crawler import run_crawlers_m
# sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
# from crawl_n_depth.crawl_n_depth.spiders.n_crawler import run_crawlers_m
# from crawl_n_depth.spiders.n_crawler import run_crawlers_m


# sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
# from crawl_n_depth.spiders.n_crawler import run_crawlers_m
#
mycol = refer_collection()
#
def execute_for_a_company(comp_name):
    print("Searching a company")
    dateTimeObj = datetime.now()
    query_collection = refer_query_col()
    data_q = {'started_time_stamp': dateTimeObj, 'search_query': comp_name}
    record_entry = query_collection.insert_one(data_q)
    print("Started on", dateTimeObj)
    started = time.time()
    print("***Initial Crawling Phrase***")
    entry_id = search_a_company(comp_name,mycol,record_entry.inserted_id)
    if(entry_id==None):
        print("Initial crawling incomple..pipeline exits.try again")
    else:
        print("entry id received ",entry_id)
        print("***Deep Crawling Phrase***")
        deep_crawl([entry_id],3,100)
        print("Deep crawling completed and record extended with crawled_links,header_text,paragraph_text,social_media_links,telephone numbers,emails,addresses")
        print("***Feature Extraction Phrase***")
        extract_features([entry_id])
        print("***Contact Person Extraction Phrase***")
        extract_contact_persons([entry_id],'comp')
        print(("***Predict the company type***"))
        predict_class_tags([entry_id])
        print(("***Extract linkedin profile data***"))
        get_li_data([entry_id])
        print(("***Extract opencorporates profile data***"))
        get_oc_data([entry_id])
        print(("***Extract dnb profile data***"))
        get_dnb_data([entry_id])
        print(("***Dumping the results***"))
        export_profiles([entry_id],record_entry.inserted_id)
        ended = time.time()
        duration = ended - started
        dateTimeObj_e = datetime.now()
        completion_data = {'completed_time_stamp': dateTimeObj_e,'elapsed_time': duration}
        print(completion_data)
        query_collection.update_one({'_id': record_entry.inserted_id},
                         {'$set': completion_data})
        print("Pipeline execution completed, elapsed time:", duration)

    # entry_id = search_a_company(comp_name, mycol)
    # print("entry id received ", entry_id)


def execute_for_a_query(query):
    print("Searching a query")
    dateTimeObj = datetime.now()
    query_collection = refer_query_col()
    data_q = {'started_time_stamp':dateTimeObj, 'search_query':query}
    record_entry = query_collection.insert_one(data_q)
    print("Started on",dateTimeObj)
    started = time.time()
    print("***Initial Crawling Phrase***")
    entry_id_list = search_a_query(query,5, mycol,record_entry.inserted_id)
    if(entry_id_list==None):
        print("Initial crawling incomple..pipeline exits.try again")
    else:
        print("entry ids received ", entry_id_list)
        print("***Deep Crawling Phrase***")
        deep_crawl(entry_id_list, 3, 100)
        print(
            "Deep crawling completed and record extended with crawled_links,header_text,paragraph_text,social_media_links,telephone numbers,emails,addresses")
        print("***Feature Extraction Phrase***")
        extract_features(entry_id_list)
        print("***Contact Person Extraction Phrase***")
        extract_contact_persons(entry_id_list, 'query')
        print(("***Predicting the company type***"))
        predict_class_tags(entry_id_list)
        print(("***Extract linkedin profile data***"))
        get_li_data(entry_id_list)
        print(("***Extract opencorporates profile data***"))
        get_oc_data(entry_id_list)
        print(("***Extract dnb profile data***"))
        get_dnb_data(entry_id_list)
        print(("***Dumping the results***"))
        export_profiles(entry_id_list,record_entry.inserted_id)
        ended = time.time()
        dateTimeObj_e = datetime.now()
        duration = ended - started
        completion_data = {'completed_time_stamp': dateTimeObj_e, 'elapsed_time': duration}
        query_collection.update_one({'_id': record_entry.inserted_id},
                         {'$set': completion_data})
        print("Pipeline execution completed, elapsed time:",duration)


queries = ['Medical equipment repair','Digital advertisement and marketing analytics services company',
           'In-home care software and services for NDIS / CDC',
           'Risk and Compliance management software','Enterprise asset management software',
            'Asset & fleet management software','Education software and services',
            'specialist educators for video games developers','Software to manage relief teachers',
            'Veterinary diagnostics','Medical equipment repair']
from multiprocessing import Process
# if __name__ == '__main__':
#     for k in queries[8:9]:
#         p = Process(target=execute_for_a_query, args=(k, ))
#         p.start()
#         p.join() # this blocks until the process terminates


execute_for_a_company('Caltex Australia Ltd')
# execute_for_a_query('Digital advertisement and marketing analytics services company')
# execute_for_a_query('In-home care software and services for NDIS / CDC')
# execute_for_a_query('Risk and Compliance management software')
# execute_for_a_query('Enterprise asset management software')
# execute_for_a_query('Asset & fleet management software')
# execute_for_a_query('Education software and services')
# execute_for_a_query('pecialist educators for video games developers')
# execute_for_a_query('Specialist content and material development')
# execute_for_a_query('Software to manage relief teachers')
# execute_for_a_query('Veterinary diagnostics')
# execute_for_a_query('Medical equipment repair Australia')
