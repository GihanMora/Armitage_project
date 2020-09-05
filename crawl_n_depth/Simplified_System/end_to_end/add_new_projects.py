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
from Simplified_System.end_to_end.create_projects import add_to_projects_queue


def create_and_queue_project(project_name,key_phrases):
    mycol = refer_projects_col()
    started_time = datetime.now()
    project_dict = {'project_name':project_name,'key_phrases':key_phrases,'created_time':started_time,'state':'queued'}
    record_entry = mycol.insert_one(project_dict)
    print("Project stored in db: ", record_entry.inserted_id)
    print("Adding to projects queue")
    add_to_projects_queue([record_entry.inserted_id])


create_and_queue_project('Educational softwares project',['school management', 'educational software'])