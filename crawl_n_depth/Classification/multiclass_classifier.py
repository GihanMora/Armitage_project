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


# json_paths = [os.path.abspath(x) for x in os.listdir("../Classification/correct_data/")]
# path_to_jsons = "F:/Armitage_project/crawl_n_depth/Classification/correct_data/"#specify the path for json files
# json_list = os.listdir(path_to_jsons)
# sorted_json_list = sorted_alphanumeric(json_list)
# j_list = [(path_to_jsons+each_path) for each_path in json_list]
#
# sorted_j_list = sorted_alphanumeric(j_list)
# print(sorted_j_list)


def process_data(path_to_jsons_t,mode):
        # path_to_jsons_t = "F:/Armitage_project/crawl_n_depth//114/"#specify the path for json files

        json_list_t = os.listdir(path_to_jsons_t)
        sorted_json_list_t = sorted_alphanumeric(json_list_t)
        print(sorted_json_list_t)
        j_list_t = [(path_to_jsons_t+each_path_t) for each_path_t in json_list_t]
        # sorted_j_list_t = sorted_alphanumeric(j_list_t)
        tagged_data=[]
        name_set = []
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
                # print('menna '+mode+path_f, word_cloud_results)
                text_rank_results = data_o[0]["textrank_resutls"]
                title = data_o[0]["title"].split(" ")
                meta_description = data_o[0]["description"].split(" ")
                text_rank_sen = [term[2].split(" ") for term in text_rank_results]
                text_rank_tokens = [j for i in text_rank_sen for j in i]
                # word_cloud_bi = data_o[0]["wordcloud_resultsbi"]
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
                print('wordcloud',word_cloud_tokens)
                # sorted_wordcloud_results = sort_on_relevance(path_f, class_tag,"CBOW")
                # if(len(sorted_wordcloud_results)==0):
                #     sorted_wordcloud_results=word_cloud_tokens
                # print(word_cloud_tokens)
                # print(class_tag)
                # word_cloud_lists.append(word_cloud_tokens+text_rank_tokens)
                # industry_list.append(class_tag)
                # token_set = word_cloud_tokens+text_rank_tokens+title+meta_description+kpe_results
                # header_text = (',').join(data_o[0]["header_text"])
                # h_t_lists = header_text.split(" ")
                # token_set = lda_tokens+guided_lda_tokens+meta_description+word_cloud_bi
                token_set = lda_tokens+guided_lda_tokens+meta_description+text_rank_tokens+kpe_tokens+word_cloud_tokens+title
                # name_set.append(path_f)
                tagged_data.append([path_f,TaggedDocument(words=token_set, tags=[class_tag])])



            except KeyError:
                print(path_f)
                print(KeyError)
                continue
        # print(tagged_data)
        # print(name_set)
        return tagged_data
# print('test')
# # test_tagged_data = process_data("F:/Armitage_project/crawl_n_depth//114/",'test')
# # print(test_tagged_data)
# process_out = process_data("F:/Armitage_project/crawl_n_depth/dataset/train/",'train')
# train_out = process_data("F:/Armitage_project/crawl_n_depth/dataset/train/",'train')
# test_out = process_data("F:/Armitage_project/crawl_n_depth/dataset/test/",'train')
to_predict_out = process_data("F:/Armitage_project/crawl_n_depth//114//",'test')
# print(len(process_out))
# tagged_data = [item[1] for item in process_out]
# name_set= [item[0] for item in process_out]
train_out,test_out = [],[]
train_tagged_data = [item[1] for item in train_out]
# test_tagged_data = [item[1] for item in test_out]
predict_tagged_data = [item[1] for item in to_predict_out]

print(predict_tagged_data)
predict_names = [item[0] for item in to_predict_out]
test_names = [item[0] for item in test_out]
# print(name_set)
# print(len(name_set))
# print(tagged_data)
# print(len(tagged_data))
# agri_data = process_data("F:/Armitage_project/crawl_n_depth/extracted_json_files/",'train')
# print('train')
# train_tagged_data = process_data("F:/Armitage_project/crawl_n_depth/extracted_json_files/",'train')
# test_tagged_data = tagged_data[1200:1600]
# test_names = name_set[1200:1600]
# train_tagged_data = tagged_data[:1200]+tagged_data[1600:]
# train_names = name_set[400:]
# wrds = ['Acquaculture','Prawn','Agriculture','production','supplies','Animal','Farming','Agricultural','Agrosystem','Nutrition','farmer','Shrimp','farm','Dairy','milk','Greenhouse','environmental','Horticulture','production','blueberries','strawberries','yoghurt','food','vinegar']
# train_tagged_data.append(TaggedDocument(words=wrds, tags=['Agriculture']))
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
count = 0
predict_tagged_data
for i,each in enumerate(predict_tagged_data):
    test_data = each[0]
    v1 = model.infer_vector(test_data)

    sims = model.docvecs.most_similar([v1])
    predictions.append(sims[0][0])
    ground_truths.append(each[1])
    with open(test_names[i]) as json_file:
        data = json.load(json_file)
    if not os.path.exists('noisy_data/'):
        os.makedirs('noisy_data/')
    if not os.path.exists('correct_data/'):
        os.makedirs('correct_data/')
    # if(sims[0][0]!=each[1][0]):
    if (each[1][0] in [sims[0][0],sims[1][0],sims[2][0]]):
        # if (sims[0][1] > 0.40):
            print(count,predict_names[i])
            print(sims[0:3], each[1][0])
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
print(ground_truths)
print(predictions)
r = classification_report(ground_truths,predictions)
print(r)