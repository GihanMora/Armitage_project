import json
import os

import pandas as pd
from nltk import word_tokenize
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from tqdm import tqdm
#import the modules
from sklearn.cluster import KMeans
import numpy as np
#create the kmeans object withe vectors created previously

from crawl_n_depth.word_embeddings.wordtovec_model import sort_on_relevance

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
        j_list_t = [(path_to_jsons_t+each_path_t) for each_path_t in json_list_t]
        # sorted_j_list_t = sorted_alphanumeric(j_list_t)
        tagged_data=[]
        # name_set = []
        c=0
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
                guided_lda_res= data_o[0]["guided_lda_resutls"]
                guided_lda_tokens = [j for i in guided_lda_res for j in i]
                # print(guided_lda_tokens)
                lda_topics = data_o[0]["lda_resutls"]
                lda_tokens = []
                for eac_re in lda_topics:
                    topic_a = eac_re[1].split('+')
                    for eac_t in topic_a:
                        lda_tokens.append(eac_t.split('*')[1].split('"')[1])

                kpe_results = word_cloud_results = data_o[0]['kpe_resutls']
                kpe_tokens =[term[0] for term in kpe_results]
                word_cloud_tokens = [term[0] for term in word_cloud_results]

                token_set = lda_tokens+word_cloud_bi+guided_lda_tokens+meta_description+text_rank_tokens+kpe_tokens+word_cloud_tokens+title
                # name_set.append(path_f)
                tagged_data.append([path_f,TaggedDocument(words=token_set, tags=[c]),class_tag])
                c=c+1
            except KeyError:
                continue
        return tagged_data
# print('test')
# # test_tagged_data = process_data("F:/Armitage_project/crawl_n_depth//114/",'test')
# # print(test_tagged_data)
# process_out = process_data("F:/Armitage_project/crawl_n_depth/dataset/train/",'train')
train_out = process_data("F:/Armitage_project/crawl_n_depth/extracted_json_files/",'train')
# test_out = process_data("F:/Armitage_project/crawl_n_depth/dataset/test/",'train')
# print(len(process_out))
# tagged_data = [item[1] for item in process_out]
# name_set= [item[0] for item in process_out]
train_tagged_data = [item[1] for item in train_out]
# print(train_tagged_data)
# test_tagged_data = [item[1] for item in test_out]
train_names = [item[0] for item in train_out]
train_class_tags= [item[2] for item in train_out]
train_tagged_data = train_tagged_data

print('datas')
print(len(train_tagged_data),len(train_names))
print('ok')
max_epochs = 100
vec_size = 100
alpha = 0.025

model = Doc2Vec(size=vec_size,
                alpha=alpha,
                min_alpha=0.00025,
                min_count=1,
                dm=1)
# print("tagged",tagged_data[0])
model.build_vocab(train_tagged_data)

for epoch in range(max_epochs):
    print('iteration {0}'.format(epoch))
    model.train(train_tagged_data,
                total_examples=model.corpus_count,
                epochs=model.iter)
    # decrease the learning rate
    model.alpha -= 0.0002
    # fix the learning rate, no decay
    model.min_alpha = model.alpha

# test_data = word_tokenize("Medical Equipment Hospital".lower())
X=[]
for i in range(len(model.docvecs)):
    X.append(model.docvecs[i])
    # print (model.docvecs[i])
# print(len(X),len(model.docvecs))
# print('docvecs',model.docvecs)
# print('X',X)

kmeans = KMeans(n_clusters=10, random_state=0).fit(X)
print(len(kmeans.labels_))
# print('kmeans_lab',kmeans.labels_)
print(len(train_names))
#craete a dictionary to get cluster data
clusters={0:[],1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[]}
for i in range(len(kmeans.labels_)):
    print(i)
    # print(kmeans.labels_[i])
    # print(kmeans.labels_[i],train_names[i])
    clusters[kmeans.labels_[i]].append([train_names[i].split('/')[-1],train_class_tags[i]])
print (clusters)
for each_i in clusters:
    tag_set = []
    for k in clusters[each_i]:
        # print(k)
        tag_set.append(k[1])
    distinct_tags = set(tag_set)
    for each_t in distinct_tags:
        print(each_t,tag_set.count(each_t))
    print('*********************')

# print(tagged_data[0][0])
# predictions = []
# ground_truths = []
# count = 0
# for i,each in enumerate(test_tagged_data):
#     test_data = each[0]
#     v1 = model.infer_vector(test_data)
#
#     sims = model.docvecs.most_similar([v1])
#     predictions.append(sims[0][0])
#     ground_truths.append(each[1])
#     with open(test_names[i]) as json_file:
#         data = json.load(json_file)
#     if not os.path.exists('noisy_data/'):
#         os.makedirs('noisy_data/')
#     if not os.path.exists('correct_data/'):
#         os.makedirs('correct_data/')
#     if(sims[0][0]!=each[1][0]):
#         if (sims[0][1] > 0.40):
#         #     print(count,test_names[i])
#         #     print(sims[0], each[1][0])
#             count=count+1
#
#     #     with open('noisy_data/'+test_names[i].split("/")[-1], 'w') as outfile:
#     #         json.dump(data, outfile)
#     else:
#         if(sims[0][1]>0.30):
#             print(count, test_names[i])
#             print(sims[0], each[1][0])
#             # print()
#             with open('correct_data/'+test_names[i].split("/")[-1], 'w') as outfile:
#                 json.dump(data, outfile)
#
#
#     # print(sims[0],each[1])
#
# r = classification_report(ground_truths,predictions)
# print(r)