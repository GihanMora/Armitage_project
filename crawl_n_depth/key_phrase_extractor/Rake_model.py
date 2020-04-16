import spacy

import gensim
import json

from gensim.utils import simple_preprocess
from rake_nltk import Rake, Metric
def run_rake_model(path_to_json,rake_limit):
    from nltk.corpus import stopwords
    stop_words = stopwords.words('english')
    stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

    with open(path_to_json) as json_file:
        data = json.load(json_file)
        for p in data:
            h_p_data = p["header_text"]+p["paragraph_text"]
    combined_text = " ".join(h_p_data)

    # text = ["RAKE short for Rapid Automatic Keyword Extraction algorithm, " \
    #        "is a domain independent keyword extraction algorithm which tries " \
    #        "to determine key phrases in a body of text by analyzing the frequency " \
    #        "of word appearance and its co-occurance with other words in the text."]

    r = Rake(max_length=3,min_length=1,ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO)
    # print('lemmatized',data_lemmatized)
    # total_data = []
    # for each in data_lemmatized:
    #     total_data+=each
    # print(total_data)
    # cleaned_text = " ".join(total_data)
    # print('cleaned',cleaned_text)
    # print('combined',text)
    r.extract_keywords_from_text(combined_text)
     # To get keyword phrases ranked highest to lowest.
    # res = r.get_ranked_phrases_with_scores()
    res_words = r.get_ranked_phrases()
    print(res_words[:rake_limit])
    data[0]['rake_resutls'] = res_words[:rake_limit]  # dump the extracted topics back to the json file

    with open(path_to_json, 'w') as outfile:
        json.dump(data, outfile)

# run_rake_model("F://Armitage_project/crawl_n_depth/extracted_json_files/www.axcelerate.com.au_0_data.json",50)