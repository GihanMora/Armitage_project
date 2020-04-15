from get_n_search_results import getGoogleLinksForSearchText
import csv
import json
import os
import time
def search_a_company(comp_name):
    sr = getGoogleLinksForSearchText(comp_name, 3)
    count = 0
    while (sr == 'captcha'):
        count = count + 1
        print('captch detected and sleeping for n times n:', count)
        time.sleep(1200 * count)
        sr = getGoogleLinksForSearchText(comp_name, 3)

    b_list_file = open('black_list.txt','r')
    black_list = b_list_file.read().splitlines()
    # 'www.dnb.com'
    received_links = [i['link'] for i in sr]

    received_domains = [i.split("/")[2] for i in received_links]
    filtered_sr = []

    print('rd', received_domains)
    for i, each in enumerate(received_domains):
        if each not in black_list:
            filtered_sr.append(sr[i])

    with open('search_results.csv', mode='w',encoding='utf8') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for each_item in filtered_sr:
            results_writer.writerow([each_item['title'], each_item['link'], each_item['description']])
        results_file.close()


def search_a_query(comp_name,number_of_results):
    sr = getGoogleLinksForSearchText(comp_name, number_of_results)
    count = 0
    while (sr == 'captcha'):
        count = count + 1
        print('captch detected and sleeping for n times n:', count)
        time.sleep(1200 * count)
        sr = getGoogleLinksForSearchText(comp_name, 3)



    with open('search_results.csv', mode='w',encoding='utf8') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for each_item in sr:
            results_writer.writerow([each_item['title'], each_item['link'], each_item['description']])
        results_file.close()

search_a_company('caltex australia')
# search_a_query('Education Systems Australia',3)