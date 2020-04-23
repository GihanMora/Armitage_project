
import sys
from bson import ObjectId
sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
from crawl_n_depth.spiders.n_crawler import run_crawlers_m

#This executes the deep crawling for the initial search results collected
#run_crawlers_m(list of objectt ids,crawling depth,crawling limit)
#Example
run_crawlers_m([ObjectId('5ea16524448198da7f949494'),ObjectId('5ea16529448198da7f949495')],3,10)
