
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
# id_list = [ObjectId('5ea16524448198da7f949494'),ObjectId('5ea16529448198da7f949495')]
id_list = [ ObjectId('5ea66f138fd4e42eb70808c3'), ObjectId('5ea66f2a8fd4e42eb70808c4'), ObjectId('5ea66f728fd4e42eb70808c6'), ObjectId('5ea66f8b8fd4e42eb70808c7'), ObjectId('5ea6849bb8f02a5e1f6c34e9'), ObjectId('5ea684d8b8f02a5e1f6c34eb'), ObjectId('5ea684edb8f02a5e1f6c34ec'), ObjectId('5ea68b3276a95ce09edcbe09'), ObjectId('5ea68b4976a95ce09edcbe0a'), ObjectId('5ea68b5e76a95ce09edcbe0b'), ObjectId('5ea68b7376a95ce09edcbe0c'), ObjectId('5ea68b9b76a95ce09edcbe0d'), ObjectId('5ea68bb176a95ce09edcbe0e'), ObjectId('5ea690d71ded0362e3f25021'), ObjectId('5ea691191ded0362e3f25022'), ObjectId('5ea691481ded0362e3f25024'), ObjectId('5ea69e062f7730c4b15480f3'), ObjectId('5ea69e1b2f7730c4b15480f4'), ObjectId('5ea69e342f7730c4b15480f5'), ObjectId('5ea6ca1da27a31ef12ce1206'), ObjectId('5ea6ca37a27a31ef12ce1207'), ObjectId('5ea6ca6aa27a31ef12ce1208')]

for each_entry in id_list:#for each search result
    #run_lda_model(id of data entry,number_of_topics)
    run_lda_model(each_entry,10)#run LDA
    # run_mallet_model(id of data entry,number_of_topics)
    # run_mallet_model(each_entry, 10)  # run LDA Mallet, Mallet path should be given for this
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