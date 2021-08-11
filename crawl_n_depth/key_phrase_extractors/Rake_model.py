import pymongo
import spacy
import gensim
import json

from gensim.utils import simple_preprocess
from rake_nltk import Rake, Metric

from Simplified_System.Database.db_connect import refer_collection


def run_rake_model(entry_id,rake_limit):
    from nltk.corpus import stopwords
    stop_words = stopwords.words('english')
    stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    print("rake model started", str(data[0]['_id']), data[0]['link'])
    try:
        h_p_data = data[0]["paragraph_text"] + data[0]["header_text"]  # do topic extraction on paragraph and header text

        combined_text = " ".join(h_p_data)

        r = Rake(max_length=3,min_length=1,ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO)
        r.extract_keywords_from_text(combined_text)
        res_words = r.get_ranked_phrases()
        if(len(res_words)):
            print(res_words[:rake_limit])
            mycol.update_one({'_id': entry_id},
                             {'$set': {'rake_results': res_words[:rake_limit] }})
            print("Successfully extended the data entry with rake results", entry_id)
        else:
            mycol.update_one({'_id': entry_id},
                             {'$set': {'rake_results': []}})
            print("vocabulary is empty")

    except Exception:
        mycol.update_one({'_id': entry_id},
                         {'$set': {'rake_results': []}})
        print("vocabulary is empty")


# run_rake_model("F://Armitage_project_v1/crawl_n_depth/extracted_json_files/www.axcelerate.com.au_0_data.json",50)