import sys
import threading
import time

from bson import ObjectId
#fix this path variable when using in another machine
sys.path.insert(0, 'F:\Armitage_project\crawl_n_depth\\')
from fake_useragent import UserAgent
from selenium import webdriver
from datetime import datetime
from Simplified_System.Initial_Crawling.main import search_a_company,search_a_query,search_a_company_alpha,update_a_company
from Simplified_System.Deep_Crawling.main import deep_crawl
from Simplified_System.Database.db_connect import refer_collection,export_profiles,refer_query_col,simplified_export
from Simplified_System.Feature_Extraction.main import extract_features
from Simplified_System.Extract_contact_persons.main import extract_contact_persons
from Classification.predict_class import predict_class_tags
from Simplified_System.web_profile_data_crawler.scrape_dnb import get_dnb_data
from Simplified_System.web_profile_data_crawler.scrape_oc import get_oc_data
from Simplified_System.web_profile_data_crawler.scrape_crunchbase import get_cb_data
from Simplified_System.linkedin_data_crawler.linkedin_crawling import get_li_data
from Simplified_System.address_extraction.address_from_google import get_ad_from_google
from Simplified_System.contacts_from_google.get_contacts_google import get_cp_from_google
from Simplified_System.phone_number_extraction.get_tp_num import get_tp_from_google
from Simplified_System.google_for_data.testbs import get_qa_from_google
# # from crawl_n_depth.Simplified_System.Deep_Crawling.main import deep_crawl
import os, uuid
from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage
# from Feature_Extraction.main import extract_features

# from crawl_n_depth.spiders.n_crawler import run_crawlers_m
# sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
# from crawl_n_depth.crawl_n_depth.spiders.n_crawler import run_crawlers_m
# from crawl_n_depth.spiders.n_crawler import run_crawlers_m


# sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
# from crawl_n_depth.spiders.n_crawler import run_crawlers_m
#
# mycol = refer_collection()
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
comp_name_client = QueueClient.from_connection_string(connect_str, "companynames")
initial_crawl_completed_client = QueueClient.from_connection_string(connect_str, "incrawldone")

def i_c(comp_name):
    return len(comp_name)

def execute_for_company_q():
    while(True):
        comp_names = comp_name_client.receive_messages()
        initial_crawl_completed = initial_crawl_completed_client.receive_messages()
        for comp_name in comp_names:
            time.sleep(30)
            entry_id = 12123
            # mycol = refer_collection()
            print("Searching a company")
            print(comp_name.content)
            # dateTimeObj = datetime.now()
            # query_collection = refer_query_col()
            # data_q = {'started_time_stamp': dateTimeObj, 'search_query': comp_name}
            # record_entry = query_collection.insert_one(data_q)
            # print("Started on", dateTimeObj)
            # started = time.time()
            # print("***Initial Crawling Phrase***")
            # entry_id = search_a_company(comp_name, mycol, record_entry.inserted_id)
            if (entry_id == None):
                for i in range(3):
                    print("Initial crawling incomple..retrying", i)
                    # entry_id = search_a_company(comp_name, mycol, record_entry.inserted_id)
                    time.sleep(5)
                    if (entry_id != None): break
            if (entry_id == None):
                print("Initial crawling incomple..retrying unsuccessful")

            elif (entry_id == 'exist'):
                print("Existing profile found. pipeline exits")
                comp_names.delete_message(comp_name)
            else:
                comp_names.delete_message(comp_name)
                initial_crawl_completed_client.send_message(str(entry_id))
        for each_i_c_c in initial_crawl_completed:
            print('Doing feature extraction')
execute_for_company_q()
#
def execute_for_a_company(comp_name):
    mycol = refer_collection()
    print("Searching a company")
    dateTimeObj = datetime.now()
    query_collection = refer_query_col()
    data_q = {'started_time_stamp': dateTimeObj, 'search_query': comp_name}
    record_entry = query_collection.insert_one(data_q)
    print("Started on", dateTimeObj)
    started = time.time()
    print("***Initial Crawling Phrase***")
    entry_id = search_a_company(comp_name,mycol,record_entry.inserted_id)
    if (entry_id == None):
        for i in range(3):
            print("Initial crawling incomple..retrying", i)
            entry_id = search_a_company(comp_name,mycol,record_entry.inserted_id)
            time.sleep(5)
            if (entry_id != None): break
    if (entry_id == None):
        print("Initial crawling incomple..retrying unsuccessful")
    elif(entry_id == 'exist'):
        print("Existing profile found. pipeline exits")
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

        print(("***Extract crunchbase profile data***"))
        get_cb_data([entry_id])

        print(("***Extract linkedin profile data***"))
        get_li_data([entry_id])

        print(("***Extract opencorporates profile data***"))
        get_oc_data([entry_id])

        print(("***Extract dnb profile data***"))
        get_dnb_data([entry_id])

        print("***Addresses from google***")
        get_ad_from_google([entry_id])
        print("***Addresses extraction completed***")

        print("***cp from google***")
        get_cp_from_google([entry_id])
        print("***cp extraction completed***")

        print("***phone numbers from google***")
        get_tp_from_google([entry_id])
        print("***tp extraction completed***")

        print("***frequent questions google***")
        get_qa_from_google([entry_id])
        print("***qa extraction completed***")

        print(("***Dumping the results***"))
        # export_profiles([entry_id],record_entry.inserted_id)
        simplified_export([entry_id])
        ended = time.time()
        duration = ended - started
        dateTimeObj_e = datetime.now()
        completion_data = {'completed_time_stamp': dateTimeObj_e,'elapsed_time': duration}
        print(completion_data)
        query_collection.update_one({'_id': record_entry.inserted_id},
                         {'$set': completion_data})
        print("Pipeline execution completed, elapsed time:", duration)