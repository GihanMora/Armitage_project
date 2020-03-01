import csv
import json

reader = csv.DictReader(open('F://Armitage_data/companylist_2197.csv'))
for i,row in enumerate(reader):
    to_dump = []
    search_text = ""
    if(len(row['Website'])==0):
        search_text = row['Company']+" australia/new zealand company"
    else:
        search_text = row['Website']

    data_dict ={
        'company' :row['Company'],
        'introduction' :row['Description'],
        'end_market':row['End market'],
        'industry':row['Industry'],
        'link': row['Website'],
        'search_text':search_text
    }
    to_dump.append(data_dict)
    c_name = row['Company'].replace(" ","_").replace('/',"").replace('(',"").replace(')',"").replace('"',"")
    json_name =  str(i)+ "_"+c_name+"_data.json"  # give json file name as domain + iteration
    print(json_name)
    print("s_t",search_text)
    with open('extracted_json_files/' + json_name, 'w') as outfile:
       json.dump(to_dump, outfile)  # dumping data and save