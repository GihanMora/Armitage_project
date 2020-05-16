#fix sys path if you want to run it seperately
import sys
from bson import ObjectId
sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
from crawl_n_depth.spiders.n_crawler import run_crawlers_m

#This executes the deep crawling for the initial search results collected
#run_crawlers_m(list of objectt ids,crawling depth,crawling limit)
#Example
# run_crawlers_m([ObjectId('5ea5c4eecd9a0d942213d1ad'),ObjectId('5ea5c4f4cd9a0d942213d1ae'),ObjectId('5ea5c4f9cd9a0d942213d1af'),ObjectId('5ea5c505cd9a0d942213d1b0'),ObjectId('5ea5c50bcd9a0d942213d1b1')],3,100)
# run_crawlers_m([ObjectId('5ea5d9ce1b34f00db5396ba7'),ObjectId('5ea5d9d41b34f00db5396ba8')],3,100)
# run_crawlers_m([ObjectId('5ea655fb80029dbdf0e1e94d'),ObjectId('5ea655f580029dbdf0e1e94c'),ObjectId('5ea655ec80029dbdf0e1e94b'),ObjectId('5ea655e680029dbdf0e1e94a')],3,100)
# run_crawlers_m([ObjectId('5ea6626c70430722e806a858'), ObjectId('5ea6629970430722e806a85a'), ObjectId('5ea662ae70430722e806a85b')],3,100)
# run_crawlers_m([ObjectId('5ea66f138fd4e42eb70808c3'), ObjectId('5ea66f2a8fd4e42eb70808c4'), ObjectId('5ea66f728fd4e42eb70808c6'), ObjectId('5ea66f8b8fd4e42eb70808c7')]
# ,3,100)
# run_crawlers_m([ObjectId('5ea6849bb8f02a5e1f6c34e9'),ObjectId('5ea684d8b8f02a5e1f6c34eb'),ObjectId('5ea684edb8f02a5e1f6c34ec')],3,100)
# run_crawlers_m([ObjectId('5ea68b3276a95ce09edcbe09'), ObjectId('5ea68b4976a95ce09edcbe0a'), ObjectId('5ea68b5e76a95ce09edcbe0b'), ObjectId('5ea68b7376a95ce09edcbe0c'), ObjectId('5ea68b9b76a95ce09edcbe0d'), ObjectId('5ea68bb176a95ce09edcbe0e')]
# ,3,100)

# run_crawlers_m([ObjectId('5ea690d71ded0362e3f25021'), ObjectId('5ea691191ded0362e3f25022'), ObjectId('5ea691481ded0362e3f25024')],3,100)
# run_crawlers_m([ObjectId('5ea69e062f7730c4b15480f3'), ObjectId('5ea69e1b2f7730c4b15480f4'), ObjectId('5ea69e342f7730c4b15480f5')],3,100)


# run_crawlers_m([ObjectId('5ea6ca1da27a31ef12ce1206'), ObjectId('5ea6ca37a27a31ef12ce1207'), ObjectId('5ea6ca6aa27a31ef12ce1208')],3,100)

def deep_crawl(id_list,depth,link_limit):

    run_crawlers_m(id_list,depth,link_limit)
# run_crawlers_m([ObjectId('5eaa4865b5e8e09eef472217')],3,100)
run_crawlers_m([ObjectId('5eb6783b3dd775bea489b02d')],3,70)