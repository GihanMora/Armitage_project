
import re
import os
import sys
sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
from crawl_n_depth.spiders.n_crawler import run_crawlers

def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)

json_paths = ['F:\Armitage_project\crawl_n_depth\Simplified_system\Deep_crawling\json_files\\'+x for x in os.listdir("F:\Armitage_project\crawl_n_depth\Simplified_system\Deep_crawling\json_files")]
print(json_paths)
sorted_j_list = sorted_alphanumeric(json_paths)

run_crawlers(sorted_j_list,5,5)