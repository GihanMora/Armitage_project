import csv
import time
import sys

from selenium.common.exceptions import WebDriverException

from os.path import dirname as up
three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)

from key_phrase_extractors.wordnet import get_wc_results

# get_wc_results(['RiskTeq covers all aspects of planning and managing risk  safety and compliance. This paperless  easy-to-use solution leaves a complete audit trail  and connects everyone involved in a particular project  especially between those in the field and those in the office._RiskTeq covers all aspects of planning and managing risk  safety and compliance. This paperless  easy-to-use solution leaves a complete audit trail  and connects everyone involved in a particular project  especially between those in the field and those in the office._Aged Care & Disability Services Build a quality and compliance focus into everyday activities. Put staff and residents first by effectively managing incidents  feedback and continuous improvement opportunities. Find Out More Education & Research Bringing a people focus into your safety and risk planning is key to delivering good outcomes. Riskteq allows people doing the work to'],'bi')

with open('all_results.csv',encoding="utf8") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    with open('output_csv.csv', mode='w', encoding='utf8',
              newline='') as results_file:  # store search results in to a csv file
        for i,row in enumerate(csv_reader):
            results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if(i==0):
                results_writer.writerow(row+['bi_word_tokens','tri_word_tokens'])
            else:
                rich_description = [row[4].replace('\n',' ').strip()]



                bi_tokens = get_wc_results(rich_description,'bi')
                tri_tokens = get_wc_results(rich_description, 'tri')
                print(type(bi_tokens))
                print(tri_tokens)
                print(row + [bi_tokens[:10], tri_tokens[:10]])
                results_writer.writerow(row + [bi_tokens[:10], tri_tokens[:10]])
            # print(row[4])
    results_file.close()
csv_file.close()