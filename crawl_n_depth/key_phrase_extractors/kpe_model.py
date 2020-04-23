import json

import pymongo
import spacy
from nltk.corpus import stopwords
from pke.unsupervised import TopicRank,YAKE

from crawl_n_depth.Simplified_System.Database.db_connect import refer_collection

nlp = spacy.load('en_core_web_sm')
# nlp.max_length = 1500000

def key_phrase_extract(entry_id,number_of_candidates):#this will extract paragraph and header text from given json file and extract the topics from that
    extractor = TopicRank()

    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    print("key_phrase extraction started", str(data[0]['_id']), data[0]['link'])
    h_data = data[0]["header_text"]  # do topic extraction on paragraph and header text

    data_hp = " ".join(h_data)
    with open('temp_text.txt', 'w', encoding='utf-8') as f:#write the extracted header and paragraph text to .txt as this lib_guidedlda only accepts .txt files
        f.write(data_hp)
        f.close()

    extractor.load_document(input='temp_text.txt', language="en", max_length=10000000,#load text file
                            normalization='stemming')
    #get stop words list
    stoplist = stopwords.words('english')

    # select the keyphrase candidates, for TopicRank the longest sequences of
    # nouns and adjectives
    extractor.candidate_selection(pos={'NOUN', 'PROPN', 'ADJ'},stoplist=stoplist)

    # weight the candidates using a random walk. The threshold parameter sets the
    # minimum similarity for clustering, and the method parameter defines the
    # linkage method
    try:
        extractor.candidate_weighting(threshold=0.74,
                                      method='average')
    except ValueError:#handling exceptions if corpus is empty
        print("Observations set is empty or not valid")
        mycol.update_one({'_id': entry_id},
                         {'$set': {'kpe_results': []}})
        return "Observations set is empty or not valid"


    # print the n-highest (10) scored candidates
    kpe_results = []
    for (keyphrase, score) in extractor.get_n_best(n=number_of_candidates, stemming=True):
        kpe_results.append([keyphrase, score])
    print("key phrase extraction completed")
    # print(kpe_results)
    kpe_words = [i[0] for i in kpe_results]
    # print(kpe_words)
    print(kpe_words)
    mycol.update_one({'_id': entry_id},
                     {'$set': {'kpe_results': kpe_words}})
    print("Successfully extended the data entry with kpe results", entry_id)

#To run this scrpit individually use following line and run the script
# key_phrase_extract(path to the json object,number_of_candidates)
