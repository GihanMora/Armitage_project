import ast
import os
from datetime import datetime
import sys

from azure.storage.queue import QueueClient
from bson import ObjectId
from os.path import dirname as up
three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)

from Simplified_System.Database.db_connect import refer_projects_col,refer_collection

def add_to_projects_queue(id_list):

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    projects_client = QueueClient.from_connection_string(connect_str, "projects-queue")
    for each_id in id_list:
        print(each_id," added to projects queue")
        projects_client.send_message([str(each_id)], time_to_live=-1)

def add_to_project_completion_queue(id_list):

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    projects_client = QueueClient.from_connection_string(connect_str, "project-completion-queue")
    for each_id in id_list:
        print(each_id," added to projects completion queue")
        projects_client.send_message([str(each_id)], time_to_live=-1)

def add_to_initial_crawling_queue(name_list):
    mycol = refer_collection()
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    ic_client = QueueClient.from_connection_string(connect_str, "initial-crawling-queue")
    for name in name_list:
        print(name)
        ic_client.send_message([str(name)])

def process_queries(key_phrases):
    queries = []
    for each_phrase in key_phrases:
        query = each_phrase+" in australia or newzealand"
        queries.append(query)
    return queries

def get_projects_via_queue():
    print("Projects queue is live")
    mycol = refer_projects_col()
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    projects_client = QueueClient.from_connection_string(connect_str, "projects-queue")
    while (True):
        rows = projects_client.receive_messages()
        for msg in rows:
            # time.sleep(60)
            row = msg.content
            row = ast.literal_eval(row)
            print(row[0],' processing queries from the key phrases')
            entry_id = ObjectId(row[0])
            proj_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in proj_data_entry]
            print(data[0])
            key_phrases = data[0]['key_phrases']
            queries = process_queries(key_phrases)
            for each_query in queries:
                print(each_query," adding to pipeline execution")
                add_to_initial_crawling_queue([each_query+' ++'+str(entry_id)+' --project'])
            projects_client.delete_message(msg)
            add_to_project_completion_queue([entry_id])


            # try:
            #     comp_name = data[0]['comp_name']
            #     data_dict_aven = scrape_avention(comp_name)
            #     if (data_dict_aven == 'error'):
            #         print("Error has occured..retry")
            #     elif (len(data_dict_aven.keys())):
            #         mycol.update_one({'_id': entry_id},
            #                          {'$set': data_dict_aven})
            #         print("Successfully extended the data entry with avention profile information", entry_id)
            #         avention_client.delete_message(msg)
            #         mycol.update_one({'_id': entry_id},
            #                          {'$set': {'avention_extraction_state': 'Completed'}})
            #     else:
            #         print("No avention profile found! dict is empty")
            #         avention_client.delete_message(msg)
            #         mycol.update_one({'_id': entry_id},
            #                          {'$set': {'avention_extraction_state': 'Completed'}})
            #
            # except IndexError:
            #     print("Indexing error occured!")
            # except KeyError:
            #     print("Key error occured!")

def create_and_queue_project(project_name,key_phrases):
    mycol = refer_projects_col()
    started_time = datetime.now()
    project_dict = {'project_name':project_name,'key_phrases':key_phrases,'created_time':started_time,'state':'queued'}
    record_entry = mycol.insert_one(project_dict)
    print("Project stored in db: ", record_entry.inserted_id)
    print("Adding to projects queue")
    add_to_projects_queue([record_entry.inserted_id])

# create_and_queue_project('Educational softwares project',['Hazard management'])
# get_projects_via_queue()