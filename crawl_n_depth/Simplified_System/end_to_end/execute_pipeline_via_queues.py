import ast
import os
import sys
import threading
import time

from azure.storage.queue import QueueClient
from bson import ObjectId
#fix this path variable when using in another machine



from os.path import dirname as up
three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)
from fake_useragent import UserAgent
from selenium import webdriver
from datetime import datetime
from multiprocessing import Process
from Simplified_System.Initial_Crawling.main import search_a_company,search_a_query,search_a_company_alpha,update_a_company
from Simplified_System.Deep_Crawling.main import deep_crawl,add_to_deep_crawling_queue,run_crawlers_via_queue_chain
from Simplified_System.Database.db_connect import refer_collection,refer_query_col,simplified_export,simplified_export_via_queue,add_to_simplified_export_queue
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




if __name__ == '__main__':
    print("Pipeline execution started via queues")
    p1 = Process(target=run_crawlers_via_queue_chain)
    p1.start()
    p2 = Process(target=extract_features_via_queue_chain)
    p2.start()
    p3 = Process(target=predict_class_tags_via_queue)
    p3.start()
    p4 = Process(target=get_qa_from_google_via_queue)
    p4.start()
    p5 = Process(target=get_li_emp_via_queue)
    p5.start()
    p6 = Process(target=get_cp_from_google_via_queue)
    p6.start()
    p7 = Process(target=get_oc_data_via_queue)
    p7.start()
    p8 = Process(target=get_aven_data_via_queue)
    p8.start()
    p9 = Process(target=get_ad_from_google_via_queue)
    p9.start()
    p10 = Process(target=get_dnb_data_via_queue)
    p10.start()
    p11 = Process(target=get_tp_from_google_via_queue)
    p11.start()
    p12 = Process(target=get_cb_data_via_queue)
    p12.start()
    p13 = Process(target=simplified_export_via_queue)
    p13.start()

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    ic_client = QueueClient.from_connection_string(connect_str, "initial-crawling-queue")
    mycol = refer_collection()
    while (True):
        rows = ic_client.receive_messages()
        for msg in rows:
            # time.sleep(120)
            row = msg.content
            row = ast.literal_eval(row)
            print(row[0])

            input_d = row[0].split("--")
            try:
                mode = input_d[1]
                s_text = input_d[0]
                if mode == 'query':
                    query = s_text.strip()
                    print("Searching a query")
                    dateTimeObj = datetime.now()
                    query_collection = refer_query_col()
                    data_q = {'started_time_stamp': dateTimeObj, 'search_query': query}
                    record_entry = query_collection.insert_one(data_q)
                    print("Started on", dateTimeObj)
                    started = time.time()
                    print("***Initial Crawling Phrase***")
                    entry_id_list = search_a_query(query, 15, mycol, record_entry.inserted_id)
                    if (entry_id_list == None):
                        for i in range(3):
                            print("Initial crawling incomplete..retrying", i)
                            entry_id_list = search_a_query(query, 15, mycol, record_entry.inserted_id)
                            time.sleep(5)
                            if (entry_id_list != None): break
                    if (entry_id_list == None):
                        print("Initial crawling incomplete..retrying unsuccessful")
                    elif (entry_id_list == 'error'):
                        print("Error occured while executing..")
                    else:
                        entry_id_list = [ObjectId(k) for k in entry_id_list]

                        qq_data_entry = query_collection.find({"_id": record_entry.inserted_id})
                        qq_data = [i for i in qq_data_entry]
                        qq_attribute_keys = list(qq_data[0].keys())
                        if ('associated_entries' in qq_attribute_keys):
                            query_collection.update_one({'_id': record_entry.inserted_id},
                                                        {'$set': {'associated_entries': qq_data[0]['associated_entries']+entry_id_list}})
                        else:
                            query_collection.update_one({'_id': record_entry.inserted_id},
                                                        {'$set': {'associated_entries': entry_id_list}})

                        print("Initial crawling successful")
                        print("Dequeue message from initial crawling queue")
                        ic_client.delete_message(msg)
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
                        print("Adding to Avention extraction queue")
                        add_to_avention_queue(entry_id_list)
                        print("Adding to Crunchbase extraction queue")
                        add_to_cb_queue(entry_id_list)
                        print("Adding to linkedin cp extraction queue")
                        add_to_li_cp_queue(entry_id_list)
                        print("Adding to simplified dump queue")
                        add_to_simplified_export_queue(entry_id_list)



                elif mode == 'comp':

                    comp_name = s_text.strip()
                    print("Searching a company")
                    dateTimeObj = datetime.now()
                    query_collection = refer_query_col()
                    data_q = {'started_time_stamp': dateTimeObj, 'search_query': comp_name}
                    record_entry = query_collection.insert_one(data_q)
                    print("Started on", dateTimeObj)
                    started = time.time()
                    print("***Initial Crawling Phrase***")
                    entry_id = search_a_company(comp_name, mycol, record_entry.inserted_id)
                    if (entry_id == None):
                        for i in range(3):
                            print("Initial crawling incomplete..retrying", i)
                            entry_id = search_a_company(comp_name, mycol, record_entry.inserted_id)
                            time.sleep(5)
                            if (entry_id != None): break
                    if (entry_id == None):
                        print("Initial crawling incomple..retrying unsuccessful")
                    elif (entry_id == 'error'):
                        print("Error occured while executing..")
                    elif (entry_id == 'exist'):
                        print("Existing profile found. pipeline exits")
                        print("Dequeue message from initial crawling queue")
                        ic_client.delete_message(msg)
                    else:

                        query_collection.update_one({'_id': record_entry.inserted_id},
                                                    {'$set': {'associated_entries': [entry_id]}})
                        print("Initial crawling successful")
                        print("Dequeue message from initial crawling queue")
                        ic_client.delete_message(msg)
                        print("Adding to deep_crawling_chain(deep_crawling,feature_extraction,classification_model)")
                        add_to_deep_crawling_queue([ObjectId(entry_id)])
                        print("Adding to Owler QA extraction queue")
                        add_to_qa_queue([ObjectId(entry_id)])
                        print("Adding to google contact person extraction queue")
                        add_to_cp_queue([ObjectId(entry_id)])
                        print("Adding to Opencorporates extraction queue")
                        add_to_oc_queue([ObjectId(entry_id)])
                        print("Adding to google address extraction queue")
                        add_to_ad_queue([ObjectId(entry_id)])
                        print("Adding to DNB extraction queue")
                        add_to_dnb_queue([ObjectId(entry_id)])
                        print("Adding to google tp extraction queue")
                        add_to_tp_queue([ObjectId(entry_id)])
                        print("Adding to Avention extraction queue")
                        add_to_avention_queue([ObjectId(entry_id)])
                        print("Adding to Crunchbase extraction queue")
                        add_to_cb_queue([ObjectId(entry_id)])
                        print("Adding to linkedin cp extraction queue")
                        add_to_li_cp_queue([ObjectId(entry_id)])
                        print("Adding to simplified dump queue")
                        add_to_simplified_export_queue([ObjectId(entry_id)])

                else:
                    print("Mode did not recognized!")
            except IndexError:
                print("Query is not in required format")