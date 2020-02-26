from get_n_search_results import getGoogleLinksForSearchText
from time import sleep
f = open('evaluation/websites.txt','r')
sites = [item[:-1] for item in f.readlines()]
print(sites)


searchResults = []
f = open("links_file.txt",'w+')
for each_l in sites[15:20]:
    sr = getGoogleLinksForSearchText(each_l,1)
    print(sr[0]['link'])
    sleep(5)
    f.write(sr[0]['link'])
    searchResults.append(sr[0]['link'])
f.close()