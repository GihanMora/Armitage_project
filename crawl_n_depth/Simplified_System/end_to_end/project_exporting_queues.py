
from bson import ObjectId
import sys
from os.path import dirname as up
import ast


three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)

import time
from Simplified_System.end_to_end.send_emails import send_dump

from Simplified_System.Database.db_connect import refer_projects_col,csv_exp_s_c, refer_query_col, simplified_export, simplified_export_with_sources,simplified_export_with_sources_and_confidence,refer_collection
import os
from azure.storage.queue import QueueClient
from bson import ObjectId

def get_entries_project(project_id):
    projects_col= refer_projects_col()
    query_collection = refer_query_col()
    proj_data_entry = projects_col.find({"_id": ObjectId(project_id)})

    print('proj',proj_data_entry)
    proj_data = [i for i in proj_data_entry]
    print(proj_data)
    print('data',len(proj_data))
    print('project_id',project_id)
    selected_project = proj_data[-1]
    # if(proj_data[0]['project_name']=='NDIS & community care software'):
    #     for k in proj_data:
    #         if(k['_id']==ObjectId('5f7558e6fce4b64506137661')):
    #             selected_project= k


    # print('projs',[proj_data[-1],proj_data[0]])
    # proj_attribute_keys = list(proj_data[-1].keys())
    proj_attribute_keys = list(selected_project.keys())
    assosiated_profiles = []
    if ('associated_queries' in proj_attribute_keys):
        # associated_queries = proj_data[-1]['associated_queries']
        associated_queries = selected_project['associated_queries']
        print('associated_queries',associated_queries)
        for each_query in associated_queries:

            query_data_entry = query_collection.find({"_id": ObjectId(each_query)})
            query_data = [i for i in query_data_entry]
            query_attribute_keys = list(query_data[0].keys())
            if ('associated_entries' in query_attribute_keys):
                associated_entries = query_data[0]['associated_entries']
                # print('kk',associated_entries)
                obs_ids = [ObjectId(i) for i in associated_entries]
                assosiated_profiles.extend(obs_ids)
        print('done')



    else:
        print("This project do not have any queries yet")
    # f = open('check.txt','w+')
    # print('all',len(associated_entries))
    # print('unique',len(associated_entries))
    # f.write('all'+str(len(assosiated_profiles))+'\\n')
    # f.write('unique' + str(len(set(assosiated_profiles))))
    # f.close()
    return assosiated_profiles

def filter_completed(id_list):
    completed_list = []
    mycol = refer_collection()
    zeros = []
    ones = []
    other = []
    filtered_list = []
    ignored_links = []
    for id_a in id_list:
        # print(id_a)
        entry = mycol.find({"_id": id_a})
        data = [d for d in entry]
        if(len(data)==0):continue
        if ('simplified_dump_state' in data[0].keys()):
            # print("yes", data[0]['ignore_flag'])
            if (data[0]['simplified_dump_state'] == 'Completed'):
                if ('ignore_flag' in data[0].keys()):
                    if (data[0]['ignore_flag'] == '0'):
                        # filtered_list.append(id_a)
                        zeros.append(id_a)
                    elif (data[0]['ignore_flag'] == '1'):
                        ones.append(id_a)
                    else:
                        other.append(id_a)

                    # print("yes",data[0]['ignore_flag'])
                    # if(data[0]['ignore_flag']=='1'):
                    #     ignored_links.append(data[0]['link'])
                    #     # print('ignored',id_a)
                    #     id_list.remove(id_a)
                    # else:
                    #     print([id_a,data[0]['ignore_flag'],data[0]['link']])

                else:
                    print([id_a, data[0]['link']])
                completed_list.append(id_a)
    return zeros


def check_ignore_flag(id_list):
    mycol = refer_collection()
    zeros =[]
    ones = []
    other = []
    filtered_list = []
    ignored_links = []
    for id_a in id_list:
        entry = mycol.find({"_id": id_a})
        data = [d for d in entry]
        if('ignore_flag' in data[0].keys()):
            if(data[0]['ignore_flag']=='0'):
                # filtered_list.append(id_a)
                zeros.append(id_a)
            elif(data[0]['ignore_flag']=='1'):
                ones.append(id_a)
            else:
                other.append(id_a)

            # print("yes",data[0]['ignore_flag'])
            # if(data[0]['ignore_flag']=='1'):
            #     ignored_links.append(data[0]['link'])
            #     # print('ignored',id_a)
            #     id_list.remove(id_a)
            # else:
            #     print([id_a,data[0]['ignore_flag'],data[0]['link']])

        else:
            print([id_a,data[0]['link']])
    # print(ignored_links)
    print('ig',len(ignored_links))
    print('ones',len(ones))
    print('zeros',len(zeros))
    print('other',len(other))
    # for k in ones:
    #     id_list.remove(k)

    print('filtered',len(id_list))

    return zeros


def project_simplified_dump(project_id):
    entry_ids = get_entries_project(project_id)
    entry_ids = list(set(entry_ids))
    print(entry_ids)
    # results_file = simplified_export(entry_ids,'C:/Project_files/armitage/armitage_admin/catalog/dumps/'+str(project_id)+'_simplified_dump.csv')
    if not os.path.exists('dumps/'):
        os.makedirs('dumps/')
    results_file = simplified_export(entry_ids, 'dumps/' + str(
        project_id) + '_simplified_dump.csv')

    return results_file

def project_simplified_dump_with_sources(project_id):
    entry_ids = get_entries_project(project_id)
    entry_ids = list(set(entry_ids))
    # print(entry_ids)
    # results_file = simplified_export_with_sources(entry_ids,'C:/Project_files/armitage/armitage_admin/catalog/dumps/'+str(project_id)+'_simplified_dump_with_sources.csv')
    if not os.path.exists('dumps/'):
        os.makedirs('dumps/')
    results_file = simplified_export_with_sources(entry_ids,
                                                  'dumps/' + str(
                                                      project_id) + '_simplified_dump_with_sources.csv')

    return results_file


def project_simplified_dump_with_sources_and_confidence(project_id):
    entry_ids = get_entries_project(project_id)
    entry_ids = list(set(entry_ids))
    # print('entry_ids...',entry_ids)
    print('all',len(entry_ids))
    completed_list = filter_completed(entry_ids)
    print('completed',len(completed_list))
    # filtered_list = check_ignore_flag(completed_list)
    filtered_list = completed_list
    # print('filtered',filtered_list)
    # print('len',len(filtered_list))
    # print("before",'C:/Project_files/armitage/armitage_admin/catalog/dumps/'+str(project_id)+'_simplified_dump_with_sources_and_confidence.csv')
    # results_file = simplified_export_with_sources_and_confidence(filtered_list,'C:/Project_files/armitage/armitage_admin/catalog/dumps/'+str(project_id)+'_simplified_dump_with_sources_and_confidence.csv')
    # results_file = csv_exp_s_c(filtered_list,'C:/Project_files/armitage/armitage_admin/catalog/dumps/'+str(project_id)+'_simplified_dump_with_sources_and_confidence.csv')

    if not os.path.exists('dumps/'):
        os.makedirs('dumps/')
    results_file = csv_exp_s_c(filtered_list, 'dumps/' + str(
        project_id) + '_simplified_dump_with_sources_and_confidence.csv')

    # results_file = csv_exp_s_c([ObjectId('602f3ade7ba8308c59e0f310')], 'C:/Project_files/armitage/armitage_admin/catalog/dumps/' + str(
    #     project_id) + '_simplified_dump_with_sources_and_confidence.csv')

    return results_file
# project_simplified_dump(ObjectId('60064e27d1e86884d532fbe8'))

# project_simplified_dump_wit
# get_entries_project()

def export_projects_via_queue():
    print("Project export queue is live")
    mycol = refer_collection()
    connect_str = "DefaultEndpointsProtocol=https;AccountName=armitage;AccountKey=yUoQAb2ZRKKFiQBzMUTLKd1YSNbd0zjkgFaAz9OS9ze+RJW6DWbeeDsPmNfucyXlDEEGmU6WUlv36My2RARLLA==;EndpointSuffix=core.windows.net"
    project_export_client = QueueClient.from_connection_string(connect_str, "project-export-queue")
    while (True):
        time.sleep(10)
        rows = project_export_client.receive_messages()
        for msg in rows:
            time.sleep(30)
            try:
                row = msg.content
                row = ast.literal_eval(row)
                print(row[0],'exporting the project')
                file_out = project_simplified_dump_with_sources_and_confidence(row[0])
                print('out',file_out)
                send_dump(file_path=file_out,file_name=file_out.split('/')[-1])
                # entry_id = ObjectId(row[0])
                # comp_data_entry = mycol.find({"_id": entry_id})
                # data = [i for i in comp_data_entry]
                project_export_client.delete_message(msg)
            except SyntaxError:
                print('fine')
            # except Exception as e:
            #     print("Exception Occured",e)
            #

# export_projects_via_queue()

