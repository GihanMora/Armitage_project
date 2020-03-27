import csv
import pandas as pd
from googlesearch import search
df = pd.read_csv("../data/csvfiles_ABR/Public01.csv", encoding='utf8')
# print(df['NonIndividualNameText'][0])
# post_set = []
black_list = []
with open('comp_urls.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['company', 'url'])
    for each_p in df['NonIndividualNameText']:
        # print(each_p)
        results = [k for k in search(each_p+' -site:facebook.com -site:bloomberg.com -site:asic.hkcorporationsearch.com -site:abnlookup.net -site:aubiz.net -site:auscompanies.com -site:google.com -site:whitepages.com.au -site:abn-lookup.com -site:au.mycompanydetails.com -site:infobel.com -site:truelocal.com.au -site:realestate.com.au -site:localsearch.com.au -site:linkedin.com -site:www.dnb.com -site:wikipedia.org', tld="com", num=5, stop=5, pause=2)]
        if(len(results)):
            print(each_p,results[0])
            writer.writerow([each_p, results[0]])
        else:
            writer.writerow([each_p, 'None'])
    # post_set.append(each_p)
# for each in post_set:
#     for j in search(each, tld="com", num=1, stop=1, pause=2):
#         print(each,j)

#
# query = "SI INTERNATIONAL PTY LTD"
# for k in range(5000):
#     for j in search(query, tld="co.in", num=1,stop=1, pause=2):
#         print(j)


