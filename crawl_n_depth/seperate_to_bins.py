import json
import os
import re
def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)
#reading stored jsons to be given to LDA and Key phrase extraction
json_paths = [os.path.abspath(x) for x in os.listdir("dataset/train/")]
path_to_jsons = "F:/Armitage_project/crawl_n_depth/dataset/train/"#specify the path for json files
json_list = os.listdir(path_to_jsons)
sorted_json_list = sorted_alphanumeric(json_list)
j_list = [(path_to_jsons+each_path) for each_path in json_list]

sorted_j_list = sorted_alphanumeric(j_list)


for i,each_json in enumerate(sorted_json_list):#for each search result
    path_f = path_to_jsons+each_json
    with open(path_f) as json_file:
        data_o = json.load(json_file)
        print(data_o[0]['industry'])
        if not os.path.exists('dataset/bins/'+data_o[0]['industry']):
            os.makedirs('dataset/bins/'+data_o[0]['industry'])

        with open('dataset/bins//'+data_o[0]['industry']+'//'+each_json, 'w') as outfile:
            json.dump(data_o, outfile)
