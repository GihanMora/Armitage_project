# Python program to generate word vectors using Word2Vec

# importing all necessary modules
import csv
import json
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import warnings

warnings.filterwarnings(action='ignore')

import gensim
from gensim.models import Word2Vec
stop_words = set(stopwords.words('english'))

def sort_on_relevance(path_f,industry,model):
    print(path_f)
    with open(path_f) as json_file:
        data_o = json.load(json_file)
    #  Reads ‘alice.txt’ file
    # sample = open("C:\\Users\\Admin\\Desktop\\alice.txt", "r")
    # s = sample.read()
    s = (" ").join(data_o[0]['paragraph_text']+data_o[0]['header_text'])
    if(len(s)==0):
        return []
    if path_f=="F://Armitage_project//crawl_n_depth//extracted_json_files//1727_Smith_Bros_Group_data.json":
        return []
    # print(len(s))
    # Replaces escape character with space
    f = s.replace("\n", " ")
    # print(len(f))
    data = []
    # print(sent_tokenize(f[:710000]))

    # iterate through each sentence in the file
    for i in sent_tokenize(f):
        temp = []
        # print("i",i)
        # tokenize the sentence into words
        for j in word_tokenize(i):
            if((j.lower() not in stop_words) and (j.lower()).isalpha()):
                temp.append(j.lower())

        data.append(temp)

    try:
        word_cloud_results = [w[0] for w in data_o[0]['wordcloud_resutls']]
        # print('wc_res',data_o[0]['wordcloud_resutls'])
        # print(word_cloud_results)
        # Create CBOW model
        if(model=='CBOW'):
            model1 = gensim.models.Word2Vec(data, min_count=1,size=100, window=5)
            print("similarities CBOW")
            filtered_results_cbow = {}
            for each in word_cloud_results:
                try:
                    similarity = model1.wv.n_similarity(industry.lower().split(), each.lower().split())
                    filtered_results_cbow[each] = similarity
                except KeyError:
                    filtered_results_cbow[each] = 0
                    # print("not exist")
            filtered_results_cbow = sorted(filtered_results_cbow, key=filtered_results_cbow.get, reverse=True)
            return filtered_results_cbow[:80]
    # for each in word_cloud_results:
    #     print(each,model1.wv.n_similarity("medical equipment healthcare".lower().split(),each.lower().split()))
    # Print results
    # print("Cosine similarity between 'family' " +
    #       "and 'entertainment' - CBOW : ",
    #       model1.similarity('family', 'entertainment'))
    # print(model1.most_similar(positive=['medical', 'equipment'], topn=10))


        # Create Skip Gram model
        if(model == 'SKIP'):
            model2 = gensim.models.Word2Vec(data, min_count=1, size=100,
                                            window=5, sg=1)

            filtered_results_skip = {}
            for each in word_cloud_results:
                try:
                    similarity = model2.wv.n_similarity(industry.lower().split(), each.lower().split())
                    # print(each, model2.wv.n_similarity("medical equipment healthcare".lower().split(),each.lower().split()))
                    filtered_results_skip[each] = similarity
                except KeyError:
                    filtered_results_skip[each] = 0
                    # print("not exist")
            filtered_results_skip = sorted(filtered_results_skip, key=filtered_results_skip.get, reverse=True)
            return filtered_results_skip[:80]
    except KeyError:
        return []
# Print results
# print("Cosine similarity between 'alice' " +
#       "and 'wonderland' - Skip Gram : ",
#       model2.similarity('alice', 'wonderland'))

# print("Cosine similarity between 'family' " +
#       "and 'entertainment' - skip gram : ",
#       model2.similarity('family', 'entertainment'))

    # print("cbow",filtered_results_cbow)
    # print("skip",filtered_results_skip)
    # skip_results = model2.most_similar(positive=industry.split(" "),topn=100)
    # cbow_results = model1.most_similar(positive=industry.split(" "),topn=100)
    # print("cbow",cbow_results)
    # print("skip",skip_results)


# path_f = "F://Armitage_project//crawl_n_depth//extracted_json_files//1727_Smith_Bros_Group_data.json"
# path_f = "F://Armitage_project//crawl_n_depth//extracted_json_files//544_Aged_Care_Channel_data.json"
# sort_on_relevance(path_f, "plant hire search site construction","CBOW")
# with open('improve_res.csv', 'w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     writer.writerow(['Wordcloud original results', 'Sorted by relavence to industry using CBOW model', 'Sorted by relavence to industry using SKIP-GRAM model', 'Get top 100 similar tokens for industry using CBOW', 'Get top 100 similar tokens for industry using SKIP-GRAM'])
#
#     for each_res in range(len(word_cloud_results)):
#         writer.writerow([word_cloud_results[each_res],filtered_results_cbow[each_res],filtered_results_skip[each_res],cbow_results[each_res][0],skip_results[each_res][0]])