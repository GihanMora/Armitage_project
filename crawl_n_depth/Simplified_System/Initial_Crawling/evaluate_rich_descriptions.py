import csv
import sys
import pandas as pd

from os.path import dirname as up

three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)
from key_phrase_extractors.wordnet import get_wc_results

file = 'C:/Project_files/armitage/armitage_worker/Armitage_project/crawl_n_depth/Simplified_System/Initial_Crawling/for_listing_websites_NDIS.csv'

res_file = pd.read_csv(file)
columns = res_file.columns
print(list(columns))

with open('for_listing_websites_NDIS_with_keywords.csv', mode='w', encoding='utf8',
          newline='') as results_file:  # store search results in to a csv file
    results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    attributes_a = ['search_text', 'title', 'link', 'description', 'rich_description','keywords_bi','keywords_tri']
    results_writer.writerow(attributes_a)
    for _,row in res_file.iterrows():
        descriptions = str(row['description'])+' '+str(row['rich_description'])

        print('dddd',descriptions)
        bi_keywords = get_wc_results([descriptions],'bi')
        tri_keywords = get_wc_results([descriptions], 'tri')
        row_final =list(row)+[[bi_keywords],[tri_keywords]]
        print(row_final)
        # break
        results_writer.writerow(row_final)
        # break


    results_file.close()
        # print(row['description'])



