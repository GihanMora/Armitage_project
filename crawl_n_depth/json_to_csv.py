import csv
import json
import json
import os
import re
def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)
#reading stored jsons to be given to LDA and Key phrase extraction
json_paths = [os.path.abspath(x) for x in os.listdir("extracted_json_files/samples/")]
path_to_jsons = "F:/Armitage_project/crawl_n_depth/extracted_json_files/samples/"#specify the path for json files
json_list = os.listdir(path_to_jsons)
sorted_json_list = sorted_alphanumeric(json_list)
j_list = [(path_to_jsons+each_path) for each_path in json_list]

sorted_j_list = sorted_alphanumeric(j_list)
print(sorted_j_list)
with open('to_analyze.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)


    writer.writerow(['company', 'introduction', 'end_market', 'industry', 'link', 'title', 'link_corrected',
               'description', 'lda_resutls', 'kpe_resutls', 'rake_resutls',
               'guided_lda_resutls', 'textrank_resutls', 'textrank_summery__resutls', 'wordcloud_resutls'])
    for i,each_json in enumerate(sorted_json_list):#for each search result
        path_f = path_to_jsons+each_json
        with open(path_f) as json_file:
            data_o = json.load(json_file)

        print(path_f)
        # data_dict[0]['paragraph_text'] = data_o[0]['paragraph_text'][:3000]
        results_list = [str(i) for i in [data_o[0]['company'], data_o[0]['introduction'], data_o[0]['end_market'], data_o[0]['industry'], data_o[0]['link'],
                         data_o[0]['title'], data_o[0]['link_corrected'],
                         data_o[0]['description'], data_o[0]['lda_resutls'], data_o[0]['kpe_resutls'], data_o[0]['rake_resutls'],
                         data_o[0]['guided_lda_resutls'], data_o[0]['textrank_resutls'], data_o[0]['textrank_summery__resutls'],
                         data_o[0]['wordcloud_resutls']]]
        writer.writerow(results_list)
    # writer.writerow([2, "Tim Berners-Lee", "World Wide Web"])
    # writer.writerow([3, "Guido van Rossum", "Python Programming"])