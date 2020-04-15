import csv
import json
import os


def build_jsons_given_csv(csv_path,json_destination):
    if not os.path.exists(json_destination):
        os.makedirs(json_destination)
    with open(csv_path, "r", encoding='utf-8') as f:
        reader = csv.reader(f, delimiter="\t")
        for i,line in enumerate(reader):#going for n depth for the each google search result
            if(line==[]):continue
            row_line = line[0].split(",")
            print(row_line)
            data_dict = {
                 'title':row_line[0],
                 'link':row_line[1],
                 'description':row_line[2]
                 }
            data = []  # preparing data to dump
            data.append(data_dict)
            print(data)
            e_name = row_line[1].split("/")[2]
            print(e_name)
            j_name = '\\'+str(i)+'_'+ e_name+'.json'
            with open(json_destination + j_name, 'w+') as outfile:
                json.dump(data, outfile)

build_jsons_given_csv("F:\Armitage_project\crawl_n_depth\Simplified_System\Initial_Crawling\search_results.csv",'json_files')