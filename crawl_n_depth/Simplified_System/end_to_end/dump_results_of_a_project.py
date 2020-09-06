#check mongo client string
#dump csv path
import ast
import os
import sys
import time
from datetime import datetime, timedelta
import gensim

import spacy

import pymongo
from azure.storage.queue import QueueClient
from bson import ObjectId
import csv

from os.path import dirname as up



three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)
from Simplified_System.Database.db_connect import refer_projects_col,refer_query_col,simplified_export,simplified_export_with_sources
from Simplified_System.evaluate_results.row_accuracy import simplified_dump_with_confidence



def get_entries_project(project_id):
    projects_col= refer_projects_col()
    query_collection = refer_query_col()
    proj_data_entry = projects_col.find({"_id": project_id})
    proj_data = [i for i in proj_data_entry]
    proj_attribute_keys = list(proj_data[0].keys())
    if ('associated_queries' in proj_attribute_keys):
        associated_queries = proj_data[0]['associated_queries']
        for each_query in associated_queries:
            query_data_entry = query_collection.find({"_id": ObjectId(each_query)})
            query_data = [i for i in query_data_entry]
            query_attribute_keys = list(query_data[0].keys())
            if ('associated_entries' in query_attribute_keys):
                associated_entries = query_data[0]['associated_entries']
                obs_ids = [ObjectId(i) for i in associated_entries]
                return obs_ids


    else:
        print("This project do not have any queries yet")
        return []

def project_simplified_dump(project_id):
    entry_ids = get_entries_project(project_id)
    # print(entry_ids)
    simplified_export(entry_ids,'F:/from git/Armitage_project/crawl_n_depth/Simplified_System/end_to_end/out.csv')

def project_simplified_dump_with_sources(project_id):
    entry_ids = get_entries_project(project_id)
    # print(entry_ids)
    simplified_export_with_sources(entry_ids,'F:/from git/Armitage_project/crawl_n_depth/Simplified_System/end_to_end/with_sources.csv')
# project_simplified_dump(ObjectId('5f52316619a6398cb19d564e'))

project_simplified_dump_with_sources(ObjectId('5f52316619a6398cb19d564e'))