# import ast
# import os
# import sys
# import threading
# import time
#
# from azure.storage.queue import QueueClient
# from bson import ObjectId
# #fix this path variable when using in another machine
# # C:\Users\gihan\AppData\Local\Programs\Python\Python37\python.exe execute_pipeline_via_queues.py
#
# from os.path import dirname as up
# three_up = up(up(up(__file__)))
# # print('relative',three_up)
# sys.path.insert(0, three_up)
# sys.path.insert(0,'C:/Project_files/armitage/armitage_worker/crawl_n_depth')
# from Simplified_System.Initial_Crawling.main import search_a_company,search_a_query,search_a_company_alpha,update_a_company
# connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
# ic_client = QueueClient.from_connection_string(connect_str, "initial-crawling-queue")
# project_comp_client = QueueClient.from_connection_string(connect_str, "project-completion-queue")

# rows = project_comp_client.receive_messages()
# for msg in rows:
#     # time.sleep(120)
#     row = msg.content
#     row = ast.literal_eval(row)
#     # print(row[0])
#     if('a1c' in row[0]):
#         print(row[0])
#
#         print("Dequeue message from initial crawling queue")
#         project_comp_client.delete_message(msg)