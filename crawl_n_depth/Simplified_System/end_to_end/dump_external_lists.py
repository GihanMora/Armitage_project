import ast
import os
from datetime import datetime
import sys
import time
from azure.storage.queue import QueueClient
from bson import ObjectId
from os.path import dirname as up



three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)

from Simplified_System.Database.db_connect import simplified_export_with_sources_and_confidence,refer_collection,refer_query_col,simplified_export,simplified_export_via_queue,add_to_simplified_export_queue,refer_projects_col

id_list = []
f = open('results_new_run.txt','r',encoding='utf-8')

for line in f.readlines():
    print('*******',line.strip().split('_')[-1])
    ob_id_str = str(line.strip().split('_')[-1])
    id_list.append(ObjectId(ob_id_str))
print(id_list)
filered_l = []
mycol = refer_collection()
for id_v in id_list:
    # print(id_v)
    entry = mycol.find({"_id": id_v})
    data = [d for d in entry]
    # print(data)
    if(data[0]['ignore_flag']=='1'):
        print(data[0]['link'])
    else:
        filered_l.append(id_v)



# simplified_export_with_sources_and_confidence(filered_l,'C:\Project_files\\armitage\\armitage_worker\Armitage_project\crawl_n_depth\Simplified_System\end_to_end\comp_export.csv')