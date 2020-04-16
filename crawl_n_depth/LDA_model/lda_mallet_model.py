import json
# Gensim
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
# spacy for lemmatization
import spacy
import os

os.environ.update({'MALLET_HOME': r'C:/new_mallet/mallet-2.0.8/'})

# Enable logging for gensim
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)
# NLTK Stop words
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])


def sent_to_words(sentences):#split sentences to words and remove punctuations
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations



def remove_stopwords(texts):#remove stopwords to do more effective extraction
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def make_bigrams(texts,bigram_mod):
    return [bigram_mod[doc] for doc in texts]

def make_trigrams(texts,bigram_mod,trigram_mod):
    return [trigram_mod[bigram_mod[doc]] for doc in texts]
def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):#lemmatize words to get core word
    """https://spacy.io/api/annotation"""
    nlp = spacy.load('en', disable=['parser', 'ner'])
    nlp.max_length = 150000000
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out


def run_mallet_model(path_to_json,number_of_topics):#this will extract paragraph and header text from given json file and extract the topics from that
    print("lda model started", path_to_json)
    with open(path_to_json) as json_file:
        data = json.load(json_file)
        for p in data:
            h_p_data = p["paragraph_text"] + p["header_text"]#do topic extraction on paragraph and header text

    print('Grabbing paragraph and header text from json file...')
    # print(h_p_data)
    data_words = list(sent_to_words(h_p_data))
    # print("data_words",data_words)
    print('remove_punctuations...')
    # Remove Stop Words
    data_words_nostops = remove_stopwords(data_words)

    # Do lemmatization keeping only noun, adj, vb, adv
    data_lemmatized = lemmatization(data_words_nostops, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV'])
    # print('data_lemmatized...')

    # Create Dictionary
    id2word = corpora.Dictionary(data_lemmatized)
    # print('id2word',id2word)
    # Create Corpus
    texts = data_lemmatized

    # Term Document Frequency
    corpus = [id2word.doc2bow(text) for text in texts]
    # print('corpus',corpus)
    # View
    print('corpus is created')#(word,frequency of occuring)
    topics = []
    mallet_list = []
    try:
        print("Mallet model is running")
        mallet_path = 'C:/new_mallet/mallet-2.0.8/bin/mallet'  # update this path
        ldamallet = gensim.models.wrappers.LdaMallet(mallet_path, corpus=corpus, num_topics=number_of_topics, id2word=id2word)
        print('mallet', ldamallet.show_topics(formatted=False))
        mallet_list = {'Topic_' + str(i): [word for word, prob in ldamallet.show_topic(i, topn=10)] for i in
                       range(0, ldamallet.num_topics)}

        print("mallet", mallet_list)

    except ValueError:#handling exceptions if corpus is empty
        print("corpus is empty or not valid")

    print(mallet_list)

    # data[0]['lda_resutls'] = words_list#dump the extracted topics back to the json file
    data[0]['lda_mallet_resutls'] = mallet_list
    with open(path_to_json, 'w') as outfile:
        json.dump(data, outfile)


#To run this scrpit individually use following line and run the script
# topics = run_lda_model(path to the json object,number_of_topics)
# print(topics)
# path_f = "F://Armitage_project//crawl_n_depth//evaluation//samples_in_different_industries//29_www.iseekplant.com.au_data.json"
# run_lda_model(path_f,3)