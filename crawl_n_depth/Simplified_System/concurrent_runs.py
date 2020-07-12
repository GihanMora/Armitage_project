import sys
from multiprocessing import Process
from os.path import dirname as up
two_up = up(up(__file__))
sys.path.insert(0, two_up)


from Classification.predict_class import predict_class_tags_via_queue
from Simplified_System.Deep_Crawling.main import run_crawlers_via_queue_chain
from Simplified_System.Feature_Extraction.main import extract_features_via_queue_chain


def loop_a():
    while 1:
        print("a")

def loop_b():
    while 1:
        print("b")

if __name__ == '__main__':
    print('fine')
    p1 = Process(target=run_crawlers_via_queue_chain)
    p1.start()
    p2 = Process(target=extract_features_via_queue_chain)
    p2.start()
    p3 = Process(target=predict_class_tags_via_queue)
    p3.start()
    #         p.start()
    # Process(target=loop_a).start()
    # Process(target=loop_b).start()