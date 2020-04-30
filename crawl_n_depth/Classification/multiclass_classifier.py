import json
import os
import pandas as pd
from bson import ObjectId
from nltk import word_tokenize
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from tqdm import tqdm
# from crawl_n_depth.word_embeddings.wordtovec_model import sort_on_relevance

from Simplified_System.Database.db_connect import refer_collection

tqdm.pandas(desc="progress-bar")
from gensim.models import Doc2Vec, doc2vec
from sklearn import utils
import gensim
from gensim.models.doc2vec import TaggedDocument
import re

def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)

def process_data(path_to_jsons_t,mode):
        json_list_t = os.listdir(path_to_jsons_t)
        sorted_json_list_t = sorted_alphanumeric(json_list_t)
        print(sorted_json_list_t)
        j_list_t = [(path_to_jsons_t+each_path_t) for each_path_t in json_list_t]
        tagged_data=[]
        for i, each_json_t in enumerate(sorted_json_list_t):  # for each search result
            path_f = path_to_jsons_t + each_json_t
            with open(path_f) as json_file:
                data_o = json.load(json_file)
            try:
                if(mode=='test'):
                    class_tag = data_o[0]['link']

                if(mode == 'train'):
                    class_tag = data_o[0]['industry']
                word_cloud_results = data_o[0]['wordcloud_resutls']
                text_rank_results = data_o[0]["textrank_resutls"]
                title = data_o[0]["title"].split(" ")
                meta_description = data_o[0]["description"].split(" ")
                text_rank_sen = [term[2].split(" ") for term in text_rank_results]
                text_rank_tokens = [j for i in text_rank_sen for j in i]
                word_cloud_bi = data_o[0]["wordcloud_resultsbi"]
                # print(text_rank_tokens)
                # text_rank_results = data_o[0]['textrank_results']
                # print(text_rank_results)
                guided_lda_res = data_o[0]["guided_lda_resutls"]
                guided_lda_tokens = [j for i in guided_lda_res for j in i]
                # print(guided_lda_tokens)
                lda_topics = data_o[0]["lda_resutls"]
                lda_tokens = []
                for eac_re in lda_topics:
                    topic_a = eac_re[1].split('+')
                    for eac_t in topic_a:
                        lda_tokens.append(eac_t.split('*')[1].split('"')[1])

                kpe_results = word_cloud_results = data_o[0]['kpe_resutls']
                kpe_tokens = [term[0] for term in kpe_results]
                word_cloud_tokens = [term[0] for term in word_cloud_results]

                token_set = lda_tokens + word_cloud_bi + guided_lda_tokens + meta_description + text_rank_tokens + kpe_tokens + word_cloud_tokens + title  # combining all features
                # name_set.append(path_f)
                tagged_data.append([path_f,TaggedDocument(words=token_set, tags=[class_tag])])



            except KeyError:
                print(path_f)
                print(KeyError)
                continue
        return tagged_data


def process_data_m(id_list, mode):
    tagged_data = []
    mycol = refer_collection()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data_o = [i for i in comp_data_entry]
        # print(data_o)
        try:
            if (mode == 'test'):
                class_tag = data_o[0]['comp_name']
            if (mode == 'train'):
                class_tag = data_o[0]['industry']

            word_cloud_results = data_o[0]['wordcloud_results_tri']
            word_cloud_tokens = [term[0] for term in word_cloud_results]
            # print(word_cloud_tokens)

            text_rank_tokens = data_o[0]["textrank_results"]
            # print(text_rank_tokens)

            title = data_o[0]["title"].split(" ")

            meta_description = data_o[0]["description"].split(" ")

            guided_lda_res = data_o[0]["guided_lda_results"]
            guided_lda_tokens = [j for i in guided_lda_res for j in i]
            # print(guided_lda_tokens)

            lda_topics = data_o[0]["lda_results"]
            lda_tokens = []
            for eac_re in lda_topics:
                lda_tokens=lda_tokens+lda_topics[eac_re]
            # print(lda_tokens)

            kpe_tokens = word_cloud_results = data_o[0]['kpe_results']
            # print(kpe_tokens)

            token_set = lda_tokens + word_cloud_tokens+ text_rank_tokens + title + meta_description + guided_lda_tokens + kpe_tokens    # combining all features
            # name_set.append(path_f)
            tagged_data.append([data_o[0]["_id"], TaggedDocument(words=token_set, tags=[class_tag])])



        except KeyError:
            print("prediction is skipped as features no present, entry id ",entry_id)
            # print(KeyError)
            continue
    return tagged_data

# predict_out = process_data_m([ObjectId('5ea5c4eecd9a0d942213d1ad')],'test')


def train_and_evaluate_model():
    print("Preparing training data..")
    #setting training data
    train_out = process_data("train_data/",'train')
    train_tagged_data = [item[1] for item in train_out]
    train_names = [item[0] for item in train_out]

    print("Preparing testing data")
    #setting testing data
    test_out = process_data("test_data/",'train')
    test_tagged_data = [item[1] for item in test_out]
    test_names = [item[0] for item in test_out]

    train_tagged_data = train_tagged_data+test_tagged_data

    print("Building Doc2Vec model..")
    max_epochs = 10
    vec_size = 100
    alpha = 0.025

    model = Doc2Vec(size=vec_size,
                    alpha=alpha,
                    min_alpha=0.00025,
                    min_count=1,
                    dm=1)
    # print("tagged",tagged_data[0])
    model.build_vocab(train_tagged_data)
    print("Building vectors..")
    for epoch in range(max_epochs):
        print('iteration {0}'.format(epoch))
        model.train(train_tagged_data,
                    total_examples=model.corpus_count,
                    epochs=model.iter)
        # decrease the learning rate
        model.alpha -= 0.0002
        # fix the learning rate, no decay
        model.min_alpha = model.alpha
    #saving the model for reuse
    model.save('classification.model')
    predictions = []
    ground_truths = []
    count = 0
    print("Predecting labels for unseen test data")
    # predict_tagged_data
    for i,each in enumerate(test_tagged_data):
        test_data = each[0]
        v1 = model.infer_vector(test_data)
        sims = model.docvecs.most_similar([v1])
        predictions.append(sims[0][0])
        ground_truths.append(each[1])
        with open(test_names[i]) as json_file:
            data = json.load(json_file)
        # if not os.path.exists('noisy_data/'):
        #     os.makedirs('noisy_data/')
        # if not os.path.exists('correct_data/'):
        #     os.makedirs('correct_data/')
        # if(sims[0][0]!=each[1][0]):
        if (each[1][0] in [sims[0][0],sims[1][0],sims[2][0]]):
            # if (sims[0][1] > 0.40):
                print(count,test_names[i])
                print(sims[0:3], [each[1][0]])
                count=count+1

        #     with open('noisy_data/'+test_names[i].split("/")[-1], 'w') as outfile:
        #         json.dump(data, outfile)
        # else:
        #     if(sims[0][1]>0.30):
        #         # print(count, test_names[i])
        #         # print(sims[0], each[1][0])
        #         print()
        #         # with open('correct_data/'+test_names[i].split("/")[-1], 'w') as outfile:
        #         #     json.dump(data, outfile)


        # print(sims[0],each[1])
    print("ground truths",ground_truths)
    print("predictions",predictions)
    r = classification_report(ground_truths,predictions)
    print(r)