import os
import re
import sys
sys.path.insert(0, 'F:/Armitage_project/')

from crawl_n_depth.key_phrase_extractor.kpe_model import key_phrase_extract
from crawl_n_depth.LDA_model.lda_model import run_lda_model
from crawl_n_depth.LDA_model.lda_mallet_model import run_mallet_model

from crawl_n_depth.key_phrase_extractor.Rake_model import run_rake_model
from crawl_n_depth.LDA_model.guided_lda import run_guided_lda_model
from crawl_n_depth.LDA_model.wordnet import run_wordcloud_model
from crawl_n_depth.key_phrase_extractor.textrank import run_textrank_model

def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)

json_paths = ['F:\Armitage_project\crawl_n_depth\Simplified_system\Json_files\\'+x for x in os.listdir("F:\Armitage_project\crawl_n_depth\Simplified_system\Json_files")]
print(json_paths)
sorted_j_list = sorted_alphanumeric(json_paths)


for each_json in sorted_j_list:#for each search result
    #run_lda_model(path to the json object,number_of_topics)
    run_lda_model(each_json,10)#run LDA
    # run_mallet_model(path to the json object,number_of_topics)
    run_mallet_model(each_json, 10)  # run LDA Mallet
    # run_guided_lda_model(path to the json object,number_of_topics)
    run_guided_lda_model(each_json, 3)# run guided LDA
    # run_rake_model(path to the json object,number_of_keywords)
    run_rake_model(each_json, 50)# run rake
    # run_textrank_model(path to the json object,number_of_keywords)
    run_textrank_model(each_json, 50)# run textrank
    # key_phrase_extract(path to the json object,number_of_candidates)
    key_phrase_extract(each_json, 10)  # run Key Phrase extraction
    # run_wordcloud_model(path to the json object,mode)
    run_wordcloud_model(each_json,'tri')