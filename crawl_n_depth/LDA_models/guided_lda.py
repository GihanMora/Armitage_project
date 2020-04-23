import json
# Gensim
import gensim
import gensim.corpora as corpora
import pymongo
from gensim.utils import simple_preprocess
# spacy for lemmatization
import spacy
from lda import guidedlda
# Enable logging for gensim
import logging

from crawl_n_depth.Simplified_System.Database.db_connect import refer_collection

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)
import numpy as np
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)
# NLTK Stop words
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])
from sklearn.feature_extraction.text import CountVectorizer

def sent_to_words(sentences):#split sentences to words and remove punctuations
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

def remove_stopwords(texts):#remove stopwords to do more effective extraction
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):#lemmatize words to get core word
    """https://spacy.io/api/annotation"""
    nlp = spacy.load('en', disable=['parser', 'ner'])
    nlp.max_length = 150000000
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out


def run_guided_lda_model(entry_id,number_of_topics):#this will extract paragraph and header text from given json file and extract the topics from that
    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    print("guided lda model started", str(data[0]['_id']), data[0]['link'])
    h_p_data = data[0]["paragraph_text"] + data[0]["header_text"]  # do topic extraction on paragraph and header text

    combined_text = " ".join(h_p_data)
    doc_list=[combined_text]

    token_vectorizer = CountVectorizer(doc_list,stop_words=stop_words)
    try:
        X= token_vectorizer.fit_transform(doc_list)
        tf_feature_names = token_vectorizer.get_feature_names()
        word2id = dict((v, idx) for idx, v in enumerate(tf_feature_names))
    except ValueError:
        print("Vocabulary is empty")
        mycol.update_one({'_id': entry_id},
                         {'$set': {'guided_lda_results': []}})
        return "No enough Data/Vocabulary is empty"

    seed_topic_list =  [['about', 'vision', 'mission','approach','team','clients'],
                        ['course', 'service', 'work','task'],
                        ['address', 'australia','contact','email','location','call','social']]
    number_of_topics=number_of_topics

    model = guidedlda.GuidedLDA(n_topics=number_of_topics, n_iter=100, random_state=7, refresh=20)
    seed_topics = {}

    for t_id, st in enumerate(seed_topic_list):
        for word in st:
            if(word in word2id.keys()):
                seed_topics[word2id[word]] = t_id
            else:
                try:
                    word2id[word]=str(int(list(word2id.keys())[-1])+1)
                    seed_topics[word2id[word]] = t_id
                except ValueError:
                    pass

    model.fit(X, seed_topics=seed_topics, seed_confidence=0.35)

    n_top_words = 10
    topic_word = model.topic_word_
    topics_set = []
    for i, topic_dist in enumerate(topic_word):
        topic_words = np.array(tf_feature_names)[np.argsort(topic_dist)][:-(n_top_words + 1):-1]
        words = [w for w in topic_words]
        topics_set.append(words)
        # print('Topic {}: {}'.format(i, ' '.join(topic_words)))
    print('topics are extracting')
    print(topics_set)
    mycol.update_one({'_id': entry_id},
                     {'$set': {'guided_lda_results': topics_set}})
    print("Successfully extended the data entry with guided lda results", entry_id)


#To run this scrpit individually use following line and run the script
# topics = run_lda_model(id to data entry,number_of_topics)
# print(topics)
