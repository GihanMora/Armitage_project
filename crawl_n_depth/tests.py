import json

path_f = "F://Armitage_project//crawl_n_depth//extracted_json_files//1885_Interpath_Services_data.json"
with open(path_f) as json_file:
    data_o = json.load(json_file)




data_dict = data_o
data_dict[0]['paragraph_text'] = data_o[0]['paragraph_text'][:3000]

with open(path_f, 'w') as outfile:
    json.dump(data_dict, outfile)  # dumping data and save