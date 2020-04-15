import csv
import json
import os


def build_jsons_given_csv(csv_path,json_destination):
    if not os.path.exists(json_destination):
        os.makedirs(json_destination)
    with open(csv_path, "r", encoding='utf-8') as f:
        reader = csv.reader(f, delimiter="\t")
        for i,line in enumerate(reader):#going for n depth for the each google search result
            row_line = line[0].split(",")
            print(row_line)
            if (i == 0): continue
            print(row_line)
            data_dict = {
                'ABN': row_line[0],
                 'EntityTypeInd':row_line[1],
                 'EntityTypeText':row_line[2],
                 'NonIndividualNameText':row_line[3],
                 'GivenName':row_line[4],
                 'FamilyName':row_line[5],
                 'State':row_line[6],
                 'Postcode':row_line[7],
                 'ASICNumber':row_line[8],
                 'OtherEntity':row_line[9],
                 'title':row_line[10],
                 'link':row_line[11],
                 'description':row_line[12]
                 }
            data = []  # preparing data to dump
            data.append(data_dict)
            print(data)
            e_name = row_line[3].replace(" ","_").replace('"',"").replace("/","_")
            print(e_name)
            j_name = '\\'+str(i)+'_'+row_line[0]+'_'+row_line[1]+'_'+ e_name+'.json'
            with open(json_destination + j_name, 'w+') as outfile:
                json.dump(data, outfile)

build_jsons_given_csv("F:\Armitage_project\crawl_n_depth\private_qualty_comp_urls.csv",'quality_json_files')