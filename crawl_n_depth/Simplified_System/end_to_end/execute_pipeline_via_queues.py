import ast
import os
import sys
import threading
import time

import pymongo
from azure.storage.queue import QueueClient
from bson import ObjectId
#fix this path variable when using in another machine
# C:\Users\gihan\AppData\Local\Programs\Python\Python37\python.exe execute_pipeline_via_queues.py


from os.path import dirname as up



three_up = up(up(up(__file__)))
# print('relative',three_up)
sys.path.insert(0, three_up)
sys.path.insert(0,'C:/Project_files/armitage/armitage_worker/crawl_n_depth')
# print(three_up)
# print(sys.path)
from fake_useragent import UserAgent
from selenium import webdriver
from datetime import datetime
from multiprocessing import Process
from Simplified_System.Initial_Crawling.main import search_a_company,search_a_query,search_a_company_alpha,update_a_company
from Simplified_System.Deep_Crawling.main import deep_crawl,add_to_deep_crawling_queue,run_crawlers_via_queue_chain
from Simplified_System.Database.db_connect import refer_collection,refer_query_col,simplified_export,simplified_export_via_queue,add_to_simplified_export_queue,refer_projects_col,simplified_export_with_sources_and_confidence_via_queue,is_query_exist
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
import subprocess





def add_to_query_queue(id_list):

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    query_client = QueueClient.from_connection_string(connect_str, "query-queue")
    for each_id in id_list:
        print(each_id," added to query queue")
        query_client.send_message([str(each_id)], time_to_live=-1)

def fix_entry_counts():
    print("Query state updating queue is live")
    query_collection = refer_query_col()
    mycol = refer_collection()

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    query_client = QueueClient.from_connection_string(connect_str, "query-queue")
    rows = query_client.receive_messages()
    for msg in rows:
        # time.sleep(10)

        row = msg.content
        print(row)
        row = ast.literal_eval(row)
        print('getting_id', row[0])
        entry_id = ObjectId(row[0])
        query_data_entry = query_collection.find({"_id": entry_id})
        data = [i for i in query_data_entry]
        # check_for_the_completion_of_components

        associated_entries = data[0]['associated_entries']
        print('getting associated entries')
        print(len(associated_entries))


def query_state_update_via_queue():
    print("Query state updating queue is live")
    query_collection = refer_query_col()
    mycol = refer_collection()

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    query_client = QueueClient.from_connection_string(connect_str, "query-queue")

    while (True):
        # print('q')
        time.sleep(200)
        rows = query_client.receive_messages()
        for msg in rows:
            time.sleep(10)

            row = msg.content
            print(row)
            row = ast.literal_eval(row)
            print('getting_id',row[0])
            entry_id = ObjectId(row[0])
            query_data_entry = query_collection.find({"_id": entry_id})
            all_entries = []
            #check_for_the_completion_of_components
            try:
                data = [i for i in query_data_entry]
                associated_entries = data[0]['associated_entries']
                print('getting associated entries')

                completed_count = 0
                for each_entry_res in associated_entries:
                    res_entry = mycol.find({"_id": each_entry_res})
                    data_res = [i for i in res_entry]
                    if ('ignore_flag' in data_res[0].keys()):
                        if (data_res[0]['ignore_flag'] == '0'):
                            all_entries.append(each_entry_res)
                            if('simplified_dump_state' in data_res[0].keys()):
                                print(["profile", each_entry_res, data_res[0]['simplified_dump_state']])

                                if(data_res[0]['simplified_dump_state']=='Completed'):
                                    completed_count+=1
                entry_count = len(all_entries)
                print('completed_count',completed_count)
                # print('entry_count',data[0]['entry_count'])
                print('entry_count', entry_count)

                # if(completed_count==data[0]['entry_count']):
                if (completed_count == entry_count):
                    print("All the entries are completed for the query",completed_count)
                    query_collection.update_one({'_id': entry_id},
                                               {'$set': {'state':'Completed'}})
                    query_client.delete_message(msg)
            except pymongo.errors.ServerSelectionTimeoutError:


                serviceName = "MongoDB"


                # start the service
                args = ['sc', 'start', serviceName]
                result = subprocess.run(args)
                # stop the service
                # args[1] = 'stop'
                # result = subprocess.run(args)
                print("pymongo error")
            except KeyError as e:
                print('Query is not yet ready',e)
            except IndexError as e:
                print('Yet query entry not available')
            except Exception as e:
                print("Exception Occured during dumping ",e)

            # for k in data[0].keys():
            #     print(k)
            # print(data)

def project_state_update_via_queue():
    print("Project state updating queue is live")
    proj_collection = refer_projects_col()
    query_collection = refer_query_col()

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    project_comp_client = QueueClient.from_connection_string(connect_str, "project-completion-queue")

    while (True):
        # print('*')
        time.sleep(300)
        rows = project_comp_client.receive_messages()
        for msg in rows:
            time.sleep(10)
            row = msg.content
            row = ast.literal_eval(row)
            print(row[0])
            entry_id = ObjectId(row[0])
            project_data_entry = proj_collection.find({"_id": entry_id})

            #check_for_the_completion_of_components
            try:
                data = [i for i in project_data_entry]
                associated_queries = data[0]['associated_queries']
                completed_count = 0
                for each_query_res in associated_queries:
                    que_entry = query_collection.find({"_id": each_query_res})
                    data_res = [i for i in que_entry]
                    # print(['query',each_query_res,data_res[0]['state']])
                    if(data_res[0]['state']=='Completed'):
                        completed_count+=1
                print(['comp',completed_count,data[0]['query_count']])
                if(completed_count>=data[0]['query_count']):
                    print("All the queries are completed for the project",completed_count)
                    proj_collection.update_one({'_id': entry_id},
                                               {'$set': {'state':'Completed'}})
                    project_comp_client.delete_message(msg)
            except pymongo.errors.ServerSelectionTimeoutError:
                serviceName = "MongoDB"
                # start the service
                args = ['sc', 'start', serviceName]
                result = subprocess.run(args)
                # stop the service
                # args[1] = 'stop'
                # result = subprocess.run(args)
                print("pymongo error")
            except KeyError as e:
                print('Project is not yet ready',e)
            except IndexError as e:
                print('Yet project entry not available')
            except Exception as e:
                print("Exception Occured during dumping ",e)
if __name__ == '__main__':
    # import sys

    # f = open("test_out.txt", 'w')
    # sys.stdout = f
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
    # p8 = Process(target=get_aven_data_via_queue)
    # p8.start()
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
    p14 = Process(target=get_projects_via_queue)
    p14.start()
    p15 = Process(target=project_state_update_via_queue)
    p15.start()
    p16 = Process(target=query_state_update_via_queue)
    p16.start()
    p17 = Process(target=simplified_export_with_sources_and_confidence_via_queue)
    p17.start()


    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    ic_client = QueueClient.from_connection_string(connect_str, "initial-crawling-queue")
    mycol = refer_collection()
    projects_col = refer_projects_col()
    while (True):
        time.sleep(10)
        rows = ic_client.receive_messages()
        for msg in rows:
            time.sleep(10)
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
                    data_q = {'started_time_stamp': dateTimeObj, 'search_query': query, 'state':'incomplete'}
                    record_entry = query_collection.insert_one(data_q)
                    add_to_query_queue([record_entry.inserted_id])
                    print("Started on", dateTimeObj)
                    started = time.time()
                    print("***Initial Crawling Phrase***")
                    entry_id_list = search_a_query(query, 100, mycol, record_entry.inserted_id)
                    if (entry_id_list == None):
                        for i in range(3):
                            print("Initial crawling incomplete..retrying", i)
                            entry_id_list = search_a_query(query, 100, mycol, record_entry.inserted_id)
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
                                                        {'$set': {'associated_entries': qq_data[0]['associated_entries']+entry_id_list}

                                                         })
                        else:
                            query_collection.update_one({'_id': record_entry.inserted_id},
                                                        {'$set': {'associated_entries': entry_id_list}})

                        print("Initial crawling successful")
                        print("Dequeue message from initial crawling queue")
                        ic_client.delete_message(msg)
                        # print("Adding to query queue")

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

                if mode == 'project':
                    id_split = s_text.strip().split("++")
                    project_id = ObjectId(id_split[1].strip())
                    query = id_split[0].strip().replace('”','').replace('“','')
                    # print('QQQ',query)
                    
                    print("Searching a query")
                    dateTimeObj = datetime.now()
                    query_collection = refer_query_col()
                    data_q = {'started_time_stamp': dateTimeObj, 'search_query': query, 'state':'incomplete'}
                    #check if query is already existing

                    res_data = is_query_exist(query)
                    if (len(res_data)):
                        print("Query already existing at " + str(res_data[0]['_id']))
                        query_id = ObjectId(res_data[0]['_id'])
                    else:
                        print("Query not existing")

                        record_entry = query_collection.insert_one(data_q)
                        add_to_query_queue([record_entry.inserted_id])
                        query_id= record_entry.inserted_id
                    proj_data_entry = projects_col.find({"_id": project_id})
                    proj_data = [i for i in proj_data_entry]
                    proj_attribute_keys = list(proj_data[0].keys())
                    if ('associated_queries' in proj_attribute_keys):
                        if(query_id not in proj_data[0]['associated_queries']):
                            projects_col.update_one({'_id': project_id},
                                                        {'$set': {'associated_queries': proj_data[0]['associated_queries'] + [query_id]}})
                    else:
                        projects_col.update_one({'_id': project_id},
                                                        {'$set': {'associated_queries': [query_id]}})

                    print("Started on", dateTimeObj)
                    started = time.time()
                    print("***Initial Crawling Phrase***")
                    entry_id_list = search_a_query(query, 100, mycol, query_id)
                    if (entry_id_list == None):
                        for i in range(3):
                            print("Initial crawling incomplete..retrying", i)
                            entry_id_list = search_a_query(query, 100, mycol, query_id)
                            time.sleep(5)
                            if (entry_id_list != None): break
                    if (entry_id_list == None):
                        print("Initial crawling incomplete..retrying unsuccessful")
                    elif (entry_id_list == 'error'):
                        print("Error occured while executing..")
                    else:
                        entry_id_list = [ObjectId(k) for k in entry_id_list]

                        qq_data_entry = query_collection.find({"_id": query_id})
                        qq_data = [i for i in qq_data_entry]
                        qq_attribute_keys = list(qq_data[0].keys())
                        if ('associated_entries' in qq_attribute_keys):
                            query_collection.update_one({'_id': query_id},
                                                        {'$set': {'associated_entries': qq_data[0]['associated_entries']+entry_id_list}})
                        else:
                            query_collection.update_one({'_id': query_id},
                                                        {'$set': {'associated_entries': entry_id_list}})

                        print("Initial crawling successful")
                        print("Dequeue message from initial crawling queue")
                        ic_client.delete_message(msg)

                        # print("Adding to Crunchbase extraction queue")
                        # add_to_cb_queue(entry_id_list)



                        # print("Adding to deep_crawling_chain(deep_crawling,feature_extraction,classification_model)")
                        # add_to_deep_crawling_queue(entry_id_list)
                        # print("Adding to Owler QA extraction queue")
                        # add_to_qa_queue(entry_id_list)
                        # print("Adding to google contact person extraction queue")
                        # add_to_cp_queue(entry_id_list)
                        # print("Adding to Opencorporates extraction queue")
                        # add_to_oc_queue(entry_id_list)
                        # print("Adding to google address extraction queue")
                        # add_to_ad_queue(entry_id_list)
                        # print("Adding to DNB extraction queue")
                        # add_to_dnb_queue(entry_id_list)
                        # print("Adding to google tp extraction queue")
                        # add_to_tp_queue(entry_id_list)
                        # # print("Adding to Avention extraction queue")
                        # # add_to_avention_queue(entry_id_list)
                        #
                        # print("Adding to linkedin cp extraction queue")
                        # add_to_li_cp_queue(entry_id_list)
                        # print("Adding to simplified dump queue")
                        # add_to_simplified_export_queue(entry_id_list)

                elif mode == 'comp':

                    comp_name = s_text.strip()
                    print("Searching a company")
                    dateTimeObj = datetime.now()
                    query_collection = refer_query_col()
                    data_q = {'started_time_stamp': dateTimeObj, 'search_query': comp_name,'state':'incomplete'}
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
                        # print("Adding to deep_crawling_chain(deep_crawling,feature_extraction,classification_model)")
                        # add_to_deep_crawling_queue([ObjectId(entry_id)])
                        # print("Adding to Owler QA extraction queue")
                        # add_to_qa_queue([ObjectId(entry_id)])
                        # print("Adding to google contact person extraction queue")
                        # add_to_cp_queue([ObjectId(entry_id)])
                        # print("Adding to Opencorporates extraction queue")
                        # add_to_oc_queue([ObjectId(entry_id)])
                        # print("Adding to google address extraction queue")
                        # add_to_ad_queue([ObjectId(entry_id)])
                        # print("Adding to DNB extraction queue")
                        # add_to_dnb_queue([ObjectId(entry_id)])
                        # print("Adding to google tp extraction queue")
                        # add_to_tp_queue([ObjectId(entry_id)])
                        # print("Adding to Avention extraction queue")
                        # add_to_avention_queue([ObjectId(entry_id)])
                        print("Adding to Crunchbase extraction queue")
                        add_to_cb_queue([ObjectId(entry_id)])
                        # print("Adding to linkedin cp extraction queue")
                        # add_to_li_cp_queue([ObjectId(entry_id)])
                        # print("Adding to simplified dump queue")
                        # add_to_simplified_export_queue([ObjectId(entry_id)])

                else:
                    print("Mode did not recognized!")
            except pymongo.errors.ServerSelectionTimeoutError:


                serviceName = "MongoDB"


                # start the service
                args = ['sc', 'start', serviceName]
                result = subprocess.run(args)
                # stop the service
                # args[1] = 'stop'
                # result = subprocess.run(args)
                print("pymongo error")
            except IndexError:
                print("Query is not in required format")


# project_state_update_via_queue()
# query_state_update_via_queue()

# fix_entry_counts()