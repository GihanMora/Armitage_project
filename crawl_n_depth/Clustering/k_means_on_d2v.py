import json
import os

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

def sorted_alphanumeric(data):#ensure jsons are processed in alphanumeric order
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)

def process_data(path_to_jsons_t,mode):#process the data such that fits for the model, some files that does not have some features might be filtered
    '''

    :param path_to_jsons_t: Path where data is stored. Jsons consisted with the features extracted.
    :param mode: Can be train or test, where train data has class label(industry) and test data does not.
    :return: processed data in format of [path_f,TaggedDocument(words=token_set, tags=[c]),class_tag]
    '''
    json_list_t = os.listdir(path_to_jsons_t)
    sorted_json_list_t = sorted_alphanumeric(json_list_t)
    print(sorted_json_list_t)
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
                class_tag = data_o[0]['link']#to recognize the file in the cluster
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

            token_set = lda_tokens+word_cloud_bi+guided_lda_tokens+meta_description+text_rank_tokens+kpe_tokens+word_cloud_tokens+title#combining all features
            # name_set.append(path_f)
            tagged_data.append([path_f,TaggedDocument(words=token_set, tags=[c]),class_tag])
            c=c+1
        except KeyError:
            print('error occured and excluding from clustering file:',each_json_t)
            continue
    return tagged_data

print("Processing the data")
#for data with industry tag
#getting the processed data
train_out = process_data("labelled_jsons/",'train')#processed output of training data
train_tagged_data = [item[1] for item in train_out]#features with class label
train_names = [item[0] for item in train_out]#json file names set of processed data
train_class_tags= [item[2] for item in train_out]#the industry tags set of processed data



print("Processing finished, Number of files:",len(train_names))

max_epochs = 100
vec_size = 100
alpha = 0.025

model = Doc2Vec(size=vec_size,#building the Doc2vec model
                alpha=alpha,
                min_alpha=0.00025,
                min_count=1,
                dm=1)
model.build_vocab(train_tagged_data)#feeding tagged data

print("Building document vectors")
for epoch in range(max_epochs):#Building vectors for documents
    print('iteration {0}'.format(epoch))
    model.train(train_tagged_data,
                total_examples=model.corpus_count,
                epochs=model.iter)
    # decrease the learning rate
    model.alpha -= 0.0002
    # fix the learning rate, no decay
    model.min_alpha = model.alpha


X=[]
for i in range(len(model.docvecs)):#taking generated document vectors
    X.append(model.docvecs[i])

print("Building clustering model")
number_of_clusters = 5
kmeans = KMeans(n_clusters=number_of_clusters, random_state=0).fit(X)#kmeans model initialization
print("Number of predictions:",len(kmeans.labels_))
print("Number of files:",len(train_names))


clusters = {}#craete a dictionary to get cluster data
for c in range(number_of_clusters):clusters[c]=[]
for i in range(len(kmeans.labels_)):#seperated the predicted data to demonstrate purpose
    clusters[kmeans.labels_[i]].append([train_names[i].split('/')[-1],train_class_tags[i]])

print("Display clustered results")
for each_i in clusters:
    tag_set = []
    for k in clusters[each_i]:
        # print(k)
        tag_set.append(k[1])
    distinct_tags = set(tag_set)
    for each_t in distinct_tags:
        print(each_t,tag_set.count(each_t))
    print('*********************')

#showing clustered data in the format of

# *********************(cluster 1)
# industry_type number_of_items
# industry_type number_of_items
# industry_type number_of_items
# *********************(cluster 2)
# industry_type number_of_items
# industry_type number_of_items
# industry_type number_of_items
# *********************(cluster 3)
# industry_type number_of_items
# industry_type number_of_items
# industry_type number_of_items
# *********************















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