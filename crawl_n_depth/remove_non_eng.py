import json

import nltk
# nltk.download('words')
words = set(nltk.corpus.words.words())
path_f = "F://Armitage_project//crawl_n_depth//evaluation//samples_in_different_industries//89_Oz_Family_Entertainment_Centres_data.json"
print(path_f)
with open(path_f) as json_file:
    data_o = json.load(json_file)
for sent in data_o[0]['paragraph_text']:
    print(sent)
    print(" ".join(w for w in nltk.wordpunct_tokenize(sent) if w.lower() in words or  w.isalpha()))