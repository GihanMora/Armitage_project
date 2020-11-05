import csv
import sys
from os.path import dirname as up
three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)
from Simplified_System.Database.db_connect import refer_collection,refer_query_col,simplified_export,simplified_export_via_queue,add_to_simplified_export_queue


f = open('edu.txt','r')
missed_list = [link.strip() for link in f.readlines()]
print(missed_list)
# for row in missed_list:
#     q = row+' --comp'
#     add_to_initial_crawling_queue([q])
#     print(q)
# with open('export_raw_data.csv', mode='w', encoding='utf8', newline='') as results_file:
#     results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#     results_writer.writerow(attrib)
#     results_writer.writerow(vals)
# results_file.close()
def get_missed_to_csv(prof_list):
    with open('EDU_deep_keywords.csv', mode='w', encoding='utf8', newline='') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(['link','title','description','rake_results','textrank_results','kpe_results','wordcloud_results','IsPrivateEquity'])
        for k in prof_list:
            search_t = k+' Australia'
            mycol = refer_collection()
            entry = mycol.find({"search_text": search_t})
            data = [d for d in entry]
            iseq = False
            eq_t = ['Investor','Invested','Private Equity','Acquired','Allocated capital']
            # print(data)a
            try:
                all_text = (',').join(data[0]['paragraph_text'])+(',').join(data[0]['header_text'])
                for k in eq_t:
                    if k in all_text:
                        iseq = True
                        break
                row = [data[0]['link'],data[0]['title'],data[0]['description'],data[0]['rake_results'][:10],
                   data[0]['textrank_results'][:10],data[0]['kpe_results'][:10],

                       [k[0] for k in data[0]['wordcloud_results_tri'][:10]],
                       iseq

                       ]
            except Exception as e:
                print(k)
                p = k.split('//')[1].replace('www.','')
                c_name = p.split('.com')[0]

                entry = mycol.find({"comp_name": c_name})
                data = [d for d in entry]
                try:
                    all_text = (',').join(data[0]['paragraph_text']) + (',').join(data[0]['header_text'])
                    for k in eq_t:
                        if k in all_text:
                            iseq = True
                            break
                    row = [data[0]['link'], data[0]['title'], data[0]['description'], data[0]['rake_results'][:10],
                           data[0]['textrank_results'][:10], data[0]['kpe_results'][:10],
                          [k[0] for k in data[0]['wordcloud_results_tri'][:10]],
                           iseq

                           ]
                except Exception as e:
                    print(k,"******")
                    continue
                # q = k + ' --comp'
                # add_to_initial_crawling_queue([q])
            results_writer.writerow(row)
    results_file.close()


# get_missed_to_csv(missed_list)