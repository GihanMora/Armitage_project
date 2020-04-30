from operator import itemgetter

import pymongo
import spacy

import gensim
import json
import os

from gensim.utils import simple_preprocess
from nltk import BigramCollocationFinder, BigramAssocMeasures, TrigramCollocationFinder, TrigramAssocMeasures
from wordcloud import WordCloud
from wordcloud import STOPWORDS

from Simplified_System.Database.db_connect import refer_collection

stop_words = list(STOPWORDS)+["one","going","go","things","will","know","really","said","say","see","talk","think","time","help","thing","want","day","work"]
# print(stop_words)
def sent_to_words(sentences):#split sentences to words and remove punctuations

    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations

def remove_stopwords(texts):#remove stopwords to do more effective extraction
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]

def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):#lemmatize words to get core word

    nlp = spacy.load('en', disable=['parser', 'ner'])
    nlp.max_length = 150000000
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
    return texts_out
def run_wordcloud_model(entry_id,mode):  # this will extract paragraph and header text from given json file and extract the topics from that

    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    print("wordcloud model started", str(data[0]['_id']), data[0]['link'])
    try:
        h_p_data = data[0]["paragraph_text"] + data[0]["header_text"]  # do topic extraction on paragraph and header text

        wordcloud = WordCloud(background_color="white", max_words=100, contour_width=3, contour_color='steelblue')
        # Generate a word cloud
        data_words = list(sent_to_words(h_p_data))
        # data_words_nostops = remove_stopwords(data_words)
        data_lemmatized = lemmatization(data_words, allowed_postags=['NOUN', 'ADJ'])
        # data_lemmatized = lemmatization(data_words_nostops, allowed_postags=['NOUN', 'ADJ'])
        # print(data_lemmatized)
        all_tokens = [j for i in data_lemmatized for j in i]
        # print('all', all_tokens)
        all_tokens = [value for value in all_tokens if
                      (value != 'other' and value != 'day' and value != 'thing' and value != 'last')]


        if mode == 'single':
            combined_text = " ".join(all_tokens)
        else:
            if mode=='bi':
                finder = BigramCollocationFinder.from_words(all_tokens)
                bigram_measures = BigramAssocMeasures()
                scored = finder.score_ngrams(bigram_measures.raw_freq)
            if mode =='tri':
                # print(combined_text)
                # setup and score the bigrams using the raw frequency.
                finder = TrigramCollocationFinder.from_words(all_tokens)
                trigram_measures = TrigramAssocMeasures()
                scored = finder.score_ngrams(trigram_measures.raw_freq)

            # print(scored)

            # By default finder.score_ngrams is sorted, however don't rely on this default behavior.
            # Sort highest to lowest based on the score.
            scoredList = sorted(scored, key=itemgetter(1), reverse=True)
            # print('sclist',scoredList)
            # word_dict is the dictionary we'll use for the word cloud.
            # Load dictionary with the FOR loop below.
            # The dictionary will look like this with the bigram and the score from above.
            # word_dict = {'bigram A': 0.000697411,
            #             'bigram B': 0.000524882}

            word_dict = {}
            listLen = len(scoredList)
            # Get the bigram and make a contiguous string for the dictionary key.
            # Set the key to the scored value.
            for i in range(listLen-1):
                word_dict['_'.join(scoredList[i][0])] = scoredList[i][1]
            # print('dic',word_dict)

        if mode=='single':
            wordcloud.generate(combined_text)
        else:
            wordcloud.generate_from_frequencies(word_dict)
    except Exception:
        print("cannot make word cloud for empty text")
        mycol.update_one({'_id': entry_id},
                         {'$set': {'wordcloud_results_'+mode: []}})
        print("vocabulary is empty")
        return "Vocabulary is empty"

    # Visualize the word cloud
    wordcloud.to_image()
    wordcloud_words = []

    word_cloud_results = []
    for each_res in wordcloud.words_:

        word_cloud_results.append([each_res,wordcloud.words_[each_res]])
        wordcloud_words.append(each_res)
    # print('words', wordcloud_words)
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis("off")
    # plt.savefig(name_j[:-4]+"png")
    # plt.show()
    print(word_cloud_results)
    # return wordcloud_words

    mycol.update_one({'_id': entry_id},
                     {'$set': {'wordcloud_results_'+mode: word_cloud_results}})
    print("Successfully extended the data entry with wordcloud results", entry_id)

# run_wordcloud_model("F://Armitage_project//crawl_n_depth//extracted_json_files//3_www.hydroterra.com.au_data.json")