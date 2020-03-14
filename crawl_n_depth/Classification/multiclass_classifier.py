import json
import os

import pandas as pd
from nltk import word_tokenize
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from tqdm import tqdm

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
# def label_sentences(corpus, label_type):
#     """
#     Gensim's Doc2Vec implementation requires each document/paragraph to have a label associated with it.
#     We do this by using the TaggedDocument method. The format will be "TRAIN_i" or "TEST_i" where "i" is
#     a dummy index of the post.
#     """
#     labeled = []
#     for i, v in enumerate(corpus):
#         label = label_type + '_' + str(i)
#         labeled.append(doc2vec.TaggedDocument(v.split(), [label]))
#     return labeled


json_paths = [os.path.abspath(x) for x in os.listdir("../extracted_json_files/")]
path_to_jsons = "F:/Armitage_project/crawl_n_depth/extracted_json_files/"#specify the path for json files
json_list = os.listdir(path_to_jsons)
sorted_json_list = sorted_alphanumeric(json_list)
j_list = [(path_to_jsons+each_path) for each_path in json_list]

sorted_j_list = sorted_alphanumeric(j_list)
print(sorted_j_list)


def process_data(path_to_jsons_t,mode):
        # path_to_jsons_t = "F:/Armitage_project/crawl_n_depth//114/"#specify the path for json files
        json_list_t = os.listdir(path_to_jsons_t)
        sorted_json_list_t = sorted_alphanumeric(json_list_t)
        j_list_t = [(path_to_jsons_t+each_path_t) for each_path_t in json_list_t]
        # sorted_j_list_t = sorted_alphanumeric(j_list_t)
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
                # print(text_rank_tokens)
                # text_rank_results = data_o[0]['textrank_results']
                # print(text_rank_results)
                kpe_results = word_cloud_results = data_o[0]['kpe_resutls']
                kpe_tokens =[term[0] for term in kpe_results]
                word_cloud_tokens = [term[0] for term in word_cloud_results]
                # sorted_wordcloud_results = sort_on_relevance(path_f, class_tag,"CBOW")
                # if(len(sorted_wordcloud_results)==0):
                #     sorted_wordcloud_results=word_cloud_tokens
                # print(word_cloud_tokens)
                # print(class_tag)
                # word_cloud_lists.append(word_cloud_tokens+text_rank_tokens)
                # industry_list.append(class_tag)
                # token_set = word_cloud_tokens+text_rank_tokens+title+meta_description+kpe_results
                token_set = word_cloud_tokens+title+meta_description


                tagged_data.append(TaggedDocument(words=token_set, tags=[class_tag]))


            except KeyError:
                continue
        return tagged_data
# print('test')
# # test_tagged_data = process_data("F:/Armitage_project/crawl_n_depth//114/",'test')
# # print(test_tagged_data)
tagged_data = process_data("F:/Armitage_project/crawl_n_depth/extracted_json_files/",'train')
# print('train')
# train_tagged_data = process_data("F:/Armitage_project/crawl_n_depth/extracted_json_files/",'train')
test_tagged_data = tagged_data[1500:]
train_tagged_data = tagged_data[:1500]
# print(train_tagged_data)
# # path_f = "F://Armitage_project//crawl_n_depth//evaluation//samples_in_different_industries//29_www.iseekplant.com.au_data.json"
# tagged_data = []
# # word_cloud_lists=[]
# # industry_list = []
# for i, each_json in enumerate(sorted_json_list):  # for each search result
#     path_f = path_to_jsons + each_json
#     with open(path_f) as json_file:
#         data_o = json.load(json_file)
#     try:
#         class_tag = data_o[0]['industry']
#         word_cloud_results = data_o[0]['wordcloud_resutls']
#         text_rank_results = data_o[0]["textrank_resutls"]
#         title = data_o[0]["title"].split(" ")
#         meta_description = data_o[0]["description"].split(" ")
#         text_rank_sen = [term[2].split(" ") for term in text_rank_results]
#         text_rank_tokens = [j for i in text_rank_sen for j in i]
#         # print(text_rank_tokens)
#         # text_rank_results = data_o[0]['textrank_results']
#         # print(text_rank_results)
#         word_cloud_tokens = [term[0] for term in word_cloud_results]
#         # sorted_wordcloud_results = sort_on_relevance(path_f, class_tag,"CBOW")
#         # if(len(sorted_wordcloud_results)==0):
#         #     sorted_wordcloud_results=word_cloud_tokens
#         # print(word_cloud_tokens)
#         # print(class_tag)
#         # word_cloud_lists.append(word_cloud_tokens+text_rank_tokens)
#         # industry_list.append(class_tag)
#         token_set = word_cloud_tokens+text_rank_tokens+title+meta_description
#
#
#         tagged_data.append(TaggedDocument(words=token_set, tags=[class_tag]))
#
#     except KeyError:
#         continue

# print(tagged_data)
# data = {'wordcloud_results': word_cloud_lists,'industry':industry_list}
# df = pd.DataFrame(data)
# # print(df.industry)
# # print(df.wordcloud_results)
# X_train, X_test, y_train, y_test = train_test_split(df.wordcloud_results, df.industry, random_state=0, test_size=0.3)
# # X_train = label_sentences(X_train, 'Train')
# # X_test = label_sentences(X_test, 'Test')
# all_data = X_train + X_test
# print(all_data[:2])

# model_dbow = Doc2Vec(dm=0, vector_size=300, negative=5, min_count=1, alpha=0.065, min_alpha=0.065)
# model_dbow.build_vocab(tagged_data)

max_epochs = 100
vec_size = 25
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

# print(tagged_data[0][0])
predictions = []
ground_truths = []
for each in test_tagged_data:
    test_data = each[0]
    v1 = model.infer_vector(test_data)

    sims = model.docvecs.most_similar([v1])
    predictions.append(sims[0][0])
    ground_truths.append(each[1])
    # print(sims[0],each[1])

r = classification_report(ground_truths,predictions)
print(r)