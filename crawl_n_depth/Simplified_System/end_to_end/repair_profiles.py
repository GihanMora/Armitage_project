import threading
import time

from azure.storage.queue import QueueClient
from bson import ObjectId
#fix this path variable when using in another machine
# C:\Users\gihan\AppData\Local\Programs\Python\Python37\python.exe execute_pipeline_via_queues.py

import sys
from os.path import dirname as up



three_up = up(up(up(__file__)))
# print('relative',three_up)
sys.path.insert(0, three_up)
sys.path.insert(0,'C:/Project_files/Armitage_project/crawl_n_depth')
# print(three_up)
# print(sys.path)
from fake_useragent import UserAgent
from selenium import webdriver
from datetime import datetime
from multiprocessing import Process
from Simplified_System.Initial_Crawling.main import search_a_company,search_a_query,search_a_company_alpha,update_a_company
from Simplified_System.Deep_Crawling.main import deep_crawl,add_to_deep_crawling_queue,run_crawlers_via_queue_chain
from Simplified_System.Database.db_connect import refer_collection,refer_query_col,simplified_export,simplified_export_via_queue,add_to_simplified_export_queue,refer_projects_col
from Simplified_System.Feature_Extraction.main import extract_features,extract_features_via_queue_chain
from Classification.predict_class import predict_class_tags,predict_class_tags_via_queue
from Simplified_System.web_profile_data_crawler.scrape_dnb import get_dnb_data,add_to_dnb_queue,get_dnb_data_via_queue
from Simplified_System.web_profile_data_crawler.scrape_oc import get_oc_data,add_to_oc_queue,get_oc_data_via_queue
from Simplified_System.web_profile_data_crawler.scrape_crunchbase import get_cb_data,add_to_cb_queue,get_cb_data_via_queue
from Simplified_System.web_profile_data_crawler.avention_scraper import get_aven_data,add_to_avention_queue,get_aven_data_via_queue
# from Simplified_System.linkedin_data_crawler.linkedin_crawling import get_li_data
from Simplified_System.google_for_data.address_extraction.address_from_google import get_ad_from_google,add_to_ad_queue,get_ad_from_google_via_queue
from Simplified_System.google_for_data.contacts_from_google.get_contacts_google import get_cp_from_google,add_to_cp_queue,get_cp_from_google_via_queue
from Simplified_System.google_for_data.scrape_owler_data.owler_extractor import get_qa_from_google,add_to_qa_queue,get_qa_from_google_via_queue
from Simplified_System.google_for_data.get_li_employees.scrape_linkedin_employees import get_li_emp,add_to_li_cp_queue,get_li_emp_via_queue
from Simplified_System.google_for_data.phone_number_extraction.get_tp_num import get_tp_from_google,add_to_tp_queue,get_tp_from_google_via_queue
from Simplified_System.end_to_end.create_projects import get_projects_via_queue




def repair_profiles(entry_id_list):
    print("Adding to deep_crawling_chain(deep_crawling,feature_extraction,classification_model)")
    add_to_deep_crawling_queue(entry_id_list)
    print("Adding to Owler QA extraction queue")
    add_to_qa_queue(entry_id_list)
    print("Adding to google contact person extraction queue")
    add_to_cp_queue(entry_id_list)
    print("Adding to Opencorporates extraction queue")
    add_to_oc_queue(entry_id_list)
    print("Adding to google address extraction queue")
    add_to_ad_queue(entry_id_list)
    print("Adding to DNB extraction queue")
    add_to_dnb_queue(entry_id_list)
    print("Adding to google tp extraction queue")
    add_to_tp_queue(entry_id_list)
    # print("Adding to Avention extraction queue")
    # add_to_avention_queue(entry_id_list)
    print("Adding to Crunchbase extraction queue")
    add_to_cb_queue(entry_id_list)
    print("Adding to linkedin cp extraction queue")
    add_to_li_cp_queue(entry_id_list)
    print("Adding to simplified dump queue")
    add_to_simplified_export_queue(entry_id_list)



# repair_profiles([ObjectId('5f7c8b46536aa6fa39039179'), ObjectId('5f7a7eb3b01f5030d514b2e4'), ObjectId('5f7c8db3536aa6fa3903918f'), ObjectId('5f7a846eb01f5030d514b30a')])