
import sys

import pymongo
from bson import ObjectId

from crawl_n_depth.Simplified_System.Database.db_connect import refer_collection

sys.path.insert(0, 'F:/Armitage_project/')
from crawl_n_depth.key_phrase_extractors.kpe_model import key_phrase_extract
from crawl_n_depth.LDA_models.lda_model import run_lda_model
from crawl_n_depth.LDA_models.lda_mallet_model import run_mallet_model
from crawl_n_depth.key_phrase_extractors.Rake_model import run_rake_model
from crawl_n_depth.LDA_models.guided_lda import run_guided_lda_model
from crawl_n_depth.key_phrase_extractors.wordnet import run_wordcloud_model
from crawl_n_depth.key_phrase_extractors.textrank import run_textrank_model




#should give set of entried where deep crawling is completed in order to run feature extraction
id_list = [ObjectId('5ea16524448198da7f949494'),ObjectId('5ea16529448198da7f949495')]

for each_entry in id_list:#for each search result
    #run_lda_model(id of data entry,number_of_topics)
    run_lda_model(each_entry,10)#run LDA
    # run_mallet_model(id of data entry,number_of_topics)
    run_mallet_model(each_entry, 10)  # run LDA Mallet, Mallet path should be given for this
    # run_guided_lda_model(id of data entry,number_of_topics)
    run_guided_lda_model(each_entry, 3)# run guided LDA
    # run_rake_model(id of data entry,number_of_keywords)
    run_rake_model(each_entry, 50)# run rake
    # # run_textrank_model(id of data entry,number_of_keywords)
    run_textrank_model(each_entry, 50)# run textrank
    # # key_phrase_extract(id of data entry,number_of_candidates)
    key_phrase_extract(each_entry, 10)  # run Key Phrase extraction
    # # run_wordcloud_model(id of data entry,mode)
    run_wordcloud_model(each_entry,'tri')