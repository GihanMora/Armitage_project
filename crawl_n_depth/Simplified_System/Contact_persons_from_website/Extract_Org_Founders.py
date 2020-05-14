# Author    :Sajani Ranasinghe
# Task      :Extract the founders, co-founders and Important persons of an Organization through the deep crawled pages of the given Organization


import re
import string
import sys
import nltk
import numpy as np
from scipy import spatial
from bson import ObjectId
from collections import OrderedDict
import spacy
nlp = spacy.load("en_core_web_sm")
from spacy.lang.en import English
from openie import StanfordOpenIE
from allennlp.predictors.predictor import Predictor
from fuzzysearch import find_near_matches
from fuzzywuzzy import process
from urllib.parse import urlparse
from itertools import groupby
import subprocess
from stanfordnlp.server import CoreNLPClient
import allennlp_models.ner.crf_tagger
#import pymongo
#from spacy import displacy
#from collections import Counter
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('maxent_ne_chunker')
#nltk.download('words')
#nlp.add_pipe(nlp.create_pipe('sentencizer'))


sys.path.insert(0, 'C:/Users/user/Desktop/LaTrobe/Projects/Proj_Armitage/Armitage_project-pre_version/crawl_n_depth//')
from Simplified_System.Database.db_connect import refer_collection
from Simplified_System.Initial_Crawling.main import search_a_query
from Simplified_System.Initial_Crawling.main import search_a_company
from Simplified_System.Deep_Crawling.main import deep_crawl


# Function to read the file containing the GLOVE embeddings from Stanford
def read_Glove_file():

    # Dictionary to hold the word mappings
    embeddings_dict = {}
    # Read the text file containing the GLOVE embeddings from Stanford
    with open(r'C:/Users/user/Desktop/LaTrobe/Projects/Proj_Armitage/Armitage_project-pre_version/crawl_n_depth/glove.6B/glove.6B.50d.txt', 'r', encoding="utf-8") as f:
        for line in f:
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            embeddings_dict[word] = vector

    return embeddings_dict

# Function to find similar words
def find_closest_embeddings(embedding, embeddings_dict):
    return sorted(embeddings_dict.keys(), key=lambda word: spatial.distance.euclidean(embeddings_dict[word], embedding))

# Function to extract the title, description, header and paragraph text from the given record_id to an extended list
def extract_data(def_entry_id):
    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": def_entry_id})
    data = [i for i in comp_data_entry]
    # extracted_data = data[0]['header_text'] + [data[0]["description"]] + data[0]["paragraph_text"]
    extracted_data = data[0]["paragraph_text"]
    return extracted_data

# Function to enrich the vocabulary using the GLOVE model
def enrich_vocab(embeddings_dict):

    def_list = ['founder', 'commence']
    keywords = []
    temp = []

    # Get the keywords with similar meanings
    for i in range(len(def_list)):
        temp.extend(find_closest_embeddings(embeddings_dict[def_list[i]], embeddings_dict)[0:9])

    # Check if the length of the given keyword is greater than 2
    for i in range(len(temp)):
        if len(temp[i]) > 2:
            keywords.append(temp[i])

    # Remove keyword from the list
    _list_ = ['ceasing', 'postpone', 'proceed', 'underway', 'builder', 'pioneer', 'founding', 'start', 'started', 'entrepreneur']
    for i in range(len(_list_)):
        if _list_[i] in keywords:
            keywords.remove(_list_[i])

    # Extend the keyword list with two more keywords
    keywords.extend(['creator', 'named', 'established', ' dates from ', 'start-up', 'startup', 'cofounder', 'cofounded'])

    # Remove duplicates from the keyword list
    keywords = list(set(keywords))

    return keywords

# Function to get the positions of the existing vocab keywords
def get_position(def_sentences, def_vocab_list):

    words = def_sentences.split()
    position_list = []
    word_list = []

    for i in range(len(def_vocab_list)):
        for pos in range(len(words)):
            if def_vocab_list[i].lower() in words[pos].lower():
                if pos not in position_list:
                    position_list.append(pos)
                    word_list.append(words[pos])

    return position_list, word_list

# Function to get human names
def get_human_names(text):

    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary = False)
    person_list = []
    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        # Not grabbing lone surnames
        if len(person) > 1:
            for part in person:
                name += part + ' '
            if name[:-1] not in person_list:
                person_list.append(name[:-1])
            name = ''
        person = []
    return (person_list)

# Function to extract the sentences where the keywords appear from the enriched vocab
def extract_sentences(def_extracted_data, def_enrich_vocab_list):

    sentences = []
    for k in range(len(def_enrich_vocab_list)):
        for i in range(len(def_extracted_data)):
            if def_enrich_vocab_list[k].lower() in def_extracted_data[i].lower():
                if def_extracted_data[i].lower() not in sentences:
                    sentences.append(def_extracted_data[i])

    # Remove duplicates in the list sentences
    sentences = list(OrderedDict.fromkeys(sentences))

    return sentences

# Function to extract the names of the founders
def extract_founders(def_sentences):

    names = []
    for i in range(len(def_sentences)):
        names.extend(get_human_names(def_sentences[i]))

    # Remove duplicates in the list sentences
    names = list(OrderedDict.fromkeys(names))

    return names

# Function to extract portion of a text for a given keyword radius
def extract_text(def_words, position, def_keyword_radius):

    # Get the bounds of the text to be extracted by specifying the keyword radius
    start_idx = position - def_keyword_radius
    finish_idx = position + (def_keyword_radius + 1)
    if start_idx < 0:
        start_idx = 0
    if finish_idx > len(def_words) + 1:
        finish_idx = len(def_words) + 1

    text = ' '.join(def_words[start_idx:finish_idx])

    return text

# Function to parse sentences
def form_sentences(join_sentences):

    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    doc = nlp(join_sentences)
    sentences = [sent.string.strip() for sent in doc.sents]

    return sentences

# Function to split to sentences by '.'
def split_to_sentences(join_sentences):

    long_sentence = join_sentences.split('.')
    return long_sentence

# Function to extract names of different tags using AllenNLp
def extract_names_allenNLP(join_sentences):

    predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/ner-model-2020.02.10.tar.gz")
    pre = predictor.predict(sentence=join_sentences)

    _persons_ = ['']*len(pre['tags'])
    pre_tag = pre['tags']
    pre_words = pre['words']
    for i in range(len(pre_tag)):
        tag = pre_tag[i]
        if 'PER' in tag:
            _persons_[i] = pre_words[i]

    _persons_ = [list(g) for k, g in groupby(_persons_, key=bool) if k]
    names = []
    for i in range(len(_persons_)):
        names.append(' '.join(_persons_[i]))

    # Remove duplicate names and considering the lone names as well
    temp = []
    for i in range(len(names)):
        if names[i] not in temp:
            temp.append(names[i])
    names = temp
    # Remove duplicate names irrespective of the case
    wordset = set(names)
    names = [item for item in wordset if item.istitle() or item.title() not in wordset]

    return names

# Function to extract organization names using AllenNLP
def extract_org_allenNLP(join_sentences, def_tag):

    predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/ner-model-2020.02.10.tar.gz")
    pre = predictor.predict(sentence=join_sentences)

    _persons_ = [''] * len(pre['tags'])
    pre_tag = pre['tags']
    pre_words = pre['words']
    for i in range(len(pre_tag)):
        tag = pre_tag[i]
        if def_tag in tag:
            _persons_[i] = pre_words[i]

    _persons_ = [list(g) for k, g in groupby(_persons_, key=bool) if k]
    names = []
    for i in range(len(_persons_)):
        names.append(' '.join(_persons_[i]))

    # Remove duplicate names and considering the lone names as well
    temp = []
    for i in range(len(names)):
        if names[i] not in temp:
            temp.append(names[i])
    names = temp
    # Remove duplicate names irrespective of the case
    wordset = set(names)
    names = [item for item in wordset if item.istitle() or item.title() not in wordset]

    return names

# Function to extract founders using OpenIE
def extract_founders_openie(person_names, _list_, enrich_vocab_list, def_org):

    with StanfordOpenIE() as client:

        # Initializing the lists
        subject_list = [[]]*len(_list_)
        relation_list = [[]]*len(_list_)
        object_list = [[]]*len(_list_)

        for i in range(len(_list_)):
            for triple in client.annotate(_list_[i]):
                subject_list[i].append(triple['subject'])
                relation_list[i].append(triple['relation'])
                object_list[i].append(triple['object'])

    obj_sbj_list = []
    for i in range(len(relation_list)):
        for m in range(len(relation_list[i])):
            relation = relation_list[i][m]
            for k in range(len(enrich_vocab_list)):
                if enrich_vocab_list[k].lower() in relation.lower():
                    # Then extract the object and subject to a new list, removing duplicates
                    if [object_list[i][m], subject_list[i][m]] not in obj_sbj_list:
                        obj_sbj_list.append([object_list[i][m], subject_list[i][m]])

    #print('obj_sbj_list:', obj_sbj_list)

    # Remove the names from the person names if the name is not associated with the given organization
    #print('def_org:', def_org)
    #print('len def_org:', len(def_org))
    #print('Person Names Before:', person_names)

    temp_names = []
    # obj_suj_list contains the object and the subject where the relation contains a keyword from enrich vocab
    for i in range(len(obj_sbj_list)):

        # Check if the object or the subject contains the organization
        flag1 = fuzzy_extract(def_org.lower(), obj_sbj_list[i][0].lower(), 60, 3)
        flag2 = fuzzy_extract(def_org.lower(), obj_sbj_list[i][1].lower(), 60, 3)

        #print('obj_sbj_list[i][0]:', obj_sbj_list[i][0])
        #print('obj_sbj_list[i][1]:', obj_sbj_list[i][1])
        #print('flag1:', flag1)
        #print('flag2:', flag2)
        """flag1 = False
        flag2 = False
        if obj_sbj_list[i][0].lower() == def_org.lower():
            flag1 = True
        if obj_sbj_list[i][1].lower() == def_org.lower():
            flag2 = True"""

        if flag1 != False and flag2 != False:
            if obj_sbj_list[i][0] in person_names:
                temp_names.append(obj_sbj_list[i][0])
            if obj_sbj_list[i][1] in person_names:
                temp_names.append(obj_sbj_list[i][1])

    return temp_names

# Fine tune the founder extraction by removing names after the word 'said'
def remove_names_said(filtered_person_names, _list_):

    flag = False
    # Iterating through the sentence list
    for i in range(len(_list_)):
        sentence = _list_[i]
        if 'I ' in sentence:
            flag = True
        if ' said ' in sentence:
            sentence_word_list = sentence.split()
            idx = sentence_word_list.index('said')
            # Get 5 words after the word said
            if idx <= len(sentence_word_list) + 1:
                words = sentence_word_list[idx:idx+5]
            else:
                last_idx = len(sentence_word_list) + 1
                words = sentence_word_list[idx:last_idx]

        if flag == False and words != []:
            # Check if a name occurs in a words list
            for k in range(len(words)):
                for m in range(len(filtered_person_names)):
                    if words[k] in filtered_person_names[m]:
                        filtered_person_names.remove(filtered_person_names[m])

    return filtered_person_names

# Function to fine-tune founder extraction by using OpenIE
def relation_ext_OpenIE(person_names, _list_, enrich_vocab_list, def_org):

    with StanfordOpenIE() as client:

        # Initializing the lists
        subject_list = [[]]*len(_list_)
        relation_list = [[]]*len(_list_)
        object_list = [[]]*len(_list_)

        for i in range(len(_list_)):
            for triple in client.annotate(_list_[i]):
                subject_list[i].append(triple['subject'])
                relation_list[i].append(triple['relation'])
                object_list[i].append(triple['object'])

    obj_sbj_list = []
    for i in range(len(relation_list)):
        for m in range(len(relation_list[i])):
            relation = relation_list[i][m]
            for k in range(len(enrich_vocab_list)):
                if enrich_vocab_list[k].lower() in relation.lower():
                    # Then extract the object and subject to a new list, removing duplicates
                    if [object_list[i][m], subject_list[i][m]] not in obj_sbj_list:
                        obj_sbj_list.append([object_list[i][m], subject_list[i][m]])

    #print('obj_sbj_list:', obj_sbj_list)

    # Remove the names from the person names if the name is not associated with the given organization
    #print('def_org:', def_org)
    #print('len def_org:', len(def_org))
    #print('Person Names Before:', person_names)
    for i in range(len(obj_sbj_list)):
        #print('Person Names Before:', person_names)
        flag1 = fuzzy_extract(def_org.lower(), obj_sbj_list[i][0].lower(), 60, 3)
        flag2 = fuzzy_extract(def_org.lower(), obj_sbj_list[i][1].lower(), 60, 3)
        #print('obj_sbj_list[i][0]:', obj_sbj_list[i][0])
        #print('obj_sbj_list[i][1]:', obj_sbj_list[i][1])
        #print('flag1:', flag1)
        #print('flag2:', flag2)
        """flag1 = False
        flag2 = False
        if obj_sbj_list[i][0].lower() == def_org.lower():
            flag1 = True
        if obj_sbj_list[i][1].lower() == def_org.lower():
            flag2 = True"""

        if flag1 == False and flag2 == False:
            if obj_sbj_list[i][0] in person_names:
                person_names.remove(obj_sbj_list[i][0])
            if obj_sbj_list[i][1] in person_names:
                person_names.remove(obj_sbj_list[i][1])

    return person_names

# Function to fine-tune the founder extract by extracting the names which are a no. of words away from the keyword
def check_keyword_dist(person_names, _list_, enrich_vocab_list, no_of_words_away):

    count_array = []
    main_keyword = []
    position_of_keyword = []
    # Iterating through the sentence list to check how many names appear in each sentence and the main keyword
    for i in range(len(_list_)):
        sentence = _list_[i]
        sentence = sentence.translate(str.maketrans('', '', string.punctuation))
        _list_[i] = sentence
        count = 0
        for k in range(len(person_names)):
            if person_names[k] in sentence:
                count = count + 1
        count_array.append(count)
        for k in range(len(enrich_vocab_list)):
            if enrich_vocab_list[k].lower() in sentence.lower():
                main_keyword.append(enrich_vocab_list[k])
                break

        sentence_list = sentence.lower().split()
        for k in range(len(sentence_list)):
            for m in range(len(enrich_vocab_list)):
                if enrich_vocab_list[m].lower() in sentence_list[k]:
                    position_of_keyword.append(k)
        #position_of_keyword.append(sentence_list.index(main_keyword[i].lower()))

    new_person_names = []
    # Getting the words around a keyword and checking if there are any names
    for i in range(len(_list_)):
        sentence = _list_[i]
        if count_array[i] == 1:
            for k in range(len(person_names)):
                if person_names[k] in sentence:
                    if person_names[k] not in new_person_names:
                        new_person_names.append(person_names[k])

        if count_array[i] > 1:
            # Extract the words around the main keyword
            text = extract_text(sentence.split(), position_of_keyword[i], no_of_words_away)
            # Check if a name appears on the text
            text_words = text.split()
            for k in range(len(text_words)):
                for m in range(len(person_names)):
                    if text_words[k] in person_names[m]: # Might be the issue
                        if text_words[k] not in new_person_names:
                            new_person_names.append(person_names[m])
    # Remove duplicates from the list
    new_person_names = list(set(new_person_names))

    return new_person_names

# Function to detect organizations names when link is provided
def get_main_organization_link(link):

    org = []
    rem = re.findall('\W+|\w+', str(link))
    remove_list = ['.', ',', '-', '_', ':', ';', 'https', 'http', 'www', 'au', 'com', 'wiki', '/', '//', '\*', 'ca', 'co', 'un', 'lk', 'za', 'en', 'web', 'net', 'org', 'wikipedia']
    for i in range(len(rem)):
        if rem[i] not in remove_list:
            if len(rem[i]) > 2:
                org.append(rem[i])
    return org

# Function to detect organizations names when link is provided
def get_main_organization_text(text):

    text = text.lower()
    remove_list = ['.', ',', '-', '_', ':', ';', ' pty', ' ltd', ' inc', ' llc', ' co ', 'org', 'australia', 'limited']
    for i in range(len(remove_list)):
        if remove_list[i] in text:
            text = text.replace(remove_list[i], '')

    # Remove the leading and traling white spaces
    text = text.lstrip()
    text = text.rstrip()

    return text

# Function to perform fuzzy string matching to check if a ~company name exist within the sentence
def fuzzy_extract(qs, ls, threshold, l_dist):

    _flag_ = False
    for word, _ in process.extractBests(qs, (ls,), score_cutoff=threshold):
        # print('word {}'.format(word))
        for match in find_near_matches(qs, word, max_l_dist=l_dist):
            match = word[match.start:match.end]
            # print('match {}'.format(match))
            index = ls.find(match)
            # if index != None and index > 0:
            if index != None:
                _flag_ = True
            # yield (match, index)

    return _flag_

# Function to extract founders using nltk - Not Effective
def extract_founders_nltk(join_sentences, enrich_vocab_list):

    # Get the position of keywords from the vocab in the extracted text
    position_list, word_list = get_position(join_sentences, enrich_vocab_list)

    # Extract the text within 40 keyword radius from a given keyword from the enriched vocab
    words = join_sentences.split()
    text_portions = extract_text(words, position_list, 40)

    # Extract person names
    founders = extract_founders(text_portions)

    return founders

# Function to extract founders using spacy - in sentence level - Not Effective
def extract_founders_spacy_sentence_lvl(join_sentences, enrich_vocab_list):

    # Get all the people names
    doc = nlp(join_sentences)
    person_names = []
    for X in doc.ents:
        if X.label_ == 'PERSON':
            _split_ = X.text.split(' ')
            if len(_split_) > 1:
                person_names.append(X.text)

    sentence_list = form_sentences(join_sentences)
    sents = extract_sentences(sentence_list, enrich_vocab_list)

    # Extract the people from the sentences where the keywords occurred
    _persons_ = []
    for i in range(len(sents)):
        for k in range(len(person_names)):
            if person_names[k] in sents[i]:
                if person_names[k] not in _persons_:
                    _persons_.append(person_names[k])

    return _persons_

# Function to extract founders using spacy - in keyword level - Not Effective
def extract_founders_spacy_keyword_lvl(join_sentences, enrich_vocab_list):

    # Get the position of keywords from the vocab in the extracted text
    position_list, word_list = get_position(join_sentences, enrich_vocab_list)

    # Extract the text within 40 keyword radius from a given keyword from the enriched vocab
    words = join_sentences.split()
    text_portions = extract_text(words, position_list, 40)

    # Get all the people names
    doc = nlp(join_sentences)
    person_names = []
    for X in doc.ents:
        if X.label_ == 'PERSON':
            _split_ = X.text.split(' ')
            if len(_split_) > 1:
                person_names.append(X.text)

    # Extract the people from the sentences where the keywords occurred
    _persons_ = []
    for i in range(len(text_portions)):
        for k in range(len(person_names)):
            if person_names[k] in text_portions[i]:
                if person_names[k] not in _persons_:
                    _persons_.append(person_names[k])

    return _persons_

# Function to extract founders using spacy - in keyword level - Not Effective
def extract_founders_spacy_keyword_lvl_openie(join_sentences, enrich_vocab_list):

    # Get the position of keywords from the vocab in the extracted text
    position_list, word_list = get_position(join_sentences, enrich_vocab_list)

    # Extract the text within 40 keyword radius from a given keyword from the enriched vocab
    words = join_sentences.split()
    text_portions = extract_text(words, position_list, 40)

    # Get all the people names
    doc = nlp(join_sentences)
    person_names = []
    for X in doc.ents:
        if X.label_ == 'PERSON':
            _split_ = X.text.split(' ')
            if len(_split_) > 1:
                person_names.append(X.text)

    print('Initial Person Names:', person_names)
    # Extract the people from the sentences where the keywords occurred
    _persons_ = []
    for i in range(len(text_portions)):
        for k in range(len(person_names)):
            if person_names[k] in text_portions[i]:
                if person_names[k] not in _persons_:
                    _persons_.append(person_names[k])

    subjects = []
    # Use OpenIE to extract entity relationships
    with StanfordOpenIE() as client:

        for i in range(len(text_portions)):
            text = text_portions[i]
            for triple in client.annotate(text):
                # print(triple)
                # Should be the other way round
                for k in range(len(enrich_vocab_list)):
                    if enrich_vocab_list[k] in triple['relation'] or triple['relation'] in enrich_vocab_list:
                        if triple['subject'] not in subjects:
                            subjects.append(triple['subject'])

    print('_persons_:', _persons_)
    print('subjects:', subjects)

    return _persons_

# Function to extract founders using spacy and Allen NLP - keyword level - Not Effective
def extract_founders_spacy_and_allennlp_keyword(join_sentences, enrich_vocab_list, org):

    # Get the position of keywords from the vocab in the extracted text
    position_list, word_list = get_position(join_sentences, enrich_vocab_list)

    # Extract the text within 40 keyword radius from a given keyword from the enriched vocab
    words = join_sentences.split()
    text_portions = extract_text(words, position_list, 40)

    _list_ = []
    # Check if the company is there
    for i in range(len(text_portions)):
        print('text portions:', text_portions[i].lower())
        print('org:', org.lower())
        if org.lower() in text_portions[i].lower():
            _list_.append(text_portions[i])
    print('list with the company:', _list_)

    # Get the person names
    persons = extract_names_allenNLP(' '.join(_list_))
    print('persons:', persons)

    return persons

# Function to extract founders using spacy and Allen NLP - sentence level - Not Effective
def extract_founders_openie_allennlp(join_sentences, enrich_vocab_list, org):

    # Extract the sentences by splitting it by '.'
    sents = split_to_sentences(join_sentences)
    sents = extract_sentences(sents, enrich_vocab_list)
    print('No. of sentences have the keywords from the enrich vocab:', len(sents))

    _list_ = []
    flag = False
    # Check if the company name is there
    for i in range(len(sents)):
        if org.lower() in sents[i].lower():
            _list_.append(sents[i])
            flag = True
    if flag == False:
        # Do fuzzy string matching for company and the organization name
        for i in range(len(sents)):
            _flag_ = fuzzy_extract(org.lower(), sents[i], 50, 7)
            if _flag_ == True:
                _list_.append(sents[i])
    print('Final list where the names are extracted:', _list_)
    print('No. of sentences Allen NLP is used:', len(_list_))

    person_names = []
    if _list_ != []:
        # Get the person names
        person_names = extract_names_allenNLP(' '.join(_list_))

    # Perform OpenIE to extract founders, by checking if there is a keyword appearing on the relation
    temp_person_names = extract_founders_openie(person_names, _list_, enrich_vocab_list, org)
    print('temp_person_names:', temp_person_names)
    # Fine-tune the founder extraction by performing OpenIE on the final list(_list_)
    filtered_person_names = relation_ext_OpenIE(person_names, _list_, enrich_vocab_list, org)

    # Fine-tune the founder extraction by checking if a name is appearing before and after 6 words of a keyword
    filterd_person_names = check_keyword_dist(filtered_person_names, _list_, enrich_vocab_list, 5)
    print('filterd_person_names:', filterd_person_names)

    # Concat the lists together and remove duplicates
    final_names = temp_person_names + filterd_person_names
    final_names = list(set(final_names))

    return final_names, _list_

# Function to extract founders using spacy and Allen NLP - sentence level
def extract_founders_allennlp(join_sentences, enrich_vocab_list, org):

    # Extract the sentences which have keywords from the enrich vocab list and use spacy to parse into sentences - Not Effective
    # sentence_list = form_sentences(join_sentences)
    # sents = extract_sentences(sentence_list, enrich_vocab_list)

    # Extract the sentences by splitting it by '.'
    sents = split_to_sentences(join_sentences)
    sents = extract_sentences(sents, enrich_vocab_list)
    print('No. of sentences have the keywords from the enrich vocab:', len(sents))

    _list_ = []
    flag = False
    # Check if the company name is there
    for i in range(len(sents)):
        if org.lower() in sents[i].lower():
            _list_.append(sents[i])
            flag = True
    if flag == False:
        # Do fuzzy string matching for company and the organization name
        for i in range(len(sents)):
            _flag_ = fuzzy_extract(org.lower(), sents[i], 50, 7)
            if _flag_ == True:
                _list_.append(sents[i])
    print('Final list where the names are extracted:', _list_)
    print('No. of sentences Allen NLP is used:', len(_list_))

    person_names = []
    if _list_ != []:
        # Get the person names
        person_names = extract_names_allenNLP(' '.join(_list_))

    # Fine-tune the founder extraction by performing OpenIE on the final list(_list_)
    filtered_person_names = relation_ext_OpenIE(person_names, _list_, enrich_vocab_list, org)
    # Fine-tune the founder extraction by checking if a name is appearing before and after 12 words of a keyword
    filterd_person_names = check_keyword_dist(filtered_person_names, _list_, enrich_vocab_list, 12)
    #filtered_person_names = remove_names_said(filtered_person_names, _list_)
    #print('final filtered_person_names:', filtered_person_names)

    return person_names, _list_, filterd_person_names





def main():

    ####################################################################################################################
    mycol = refer_collection()
    _id_ = None

    _input_ = input('Input whether a link(L) or text(T): ')
    if _input_ == 'L':
        # Enter link to be deep crawled and to extract founders
        link = 'www.sentral.com.au' # There exist founders in the deep crawled sites and the program can identify them successfully
        #link = 'https://www.codelikeagirl.com/about/our-story/' # There exist founders in the deep crawled sites and the program can identify them successfully
        _id_ = search_a_company(link, mycol)

    if _input_ == 'T':
        # Enter organization or the company name to be deep crawled and to extract founders
        text = 'SENTRAL PTY LTD' # There exist founders in the deep crawled sites and the program can identify them successfully
        #text = 'Jac and Jack pty ltd' # There exist founders in the deep crawled sites and the program can identify them successfully
        _id_ = search_a_query(text, 1, mycol)

    # Calling the deep crawling function just to extract the data from the initial website only
    deep_crawl([ObjectId(_id_)], 3, 20)
    print('*** FINISHED DEEP CRAWLING *** \n')

    # Read the text file containing the GLOVE embeddings from Stanford
    embeddings_dict = read_Glove_file()
    # Enrich the vocabulary with similar meaning to founder
    enrich_vocab_list = enrich_vocab(embeddings_dict)
    print('enrich_vocab_list: ', enrich_vocab_list)
    # Extract the data related to the title, description, header and paragraph text in form of an extended list
    extracted_data = extract_data(_id_)
    print('extracted_data:', extracted_data)
    # Joining the sentences
    join_sentences = ' '.join(extracted_data)

    if _input_ == 'L':
        # Get the main company name to be searched when a link is given
        _netloc_ = urlparse(link).netloc
        if _netloc_ != '':
            if 'wiki' not in _netloc_:
                org = get_main_organization_link(_netloc_)[0]
            else:
                _netloc_ = ''
        if _netloc_ is '':
            org = get_main_organization_link(link)[0]
        print('Main Organization after parsing the url:', org)

    elif _input_ == 'T':
        # Some pre-processing to get the company only
        org = get_main_organization_text(text)
        print('Main Organization after pre-processing text:', org)
    ####################################################################################################################

    ####################################################################################################################
    # Extract founders using spacy - in sentence level - Not Effective
    #founders = extract_founders_spacy_sentence_lvl(join_sentences, enrich_vocab_list)
    #print('No. of Founders or Important Persons:', len(founders))
    #print('Founders or Important Persons associated with the organization:', founders)
    ####################################################################################################################

    ####################################################################################################################
    # Extract founders using spacy - in keyword level - Not Effective
    #founders = extract_founders_spacy_keyword_lvl(join_sentences, enrich_vocab_list)
    #print('No. of Founders or Important Persons (using Spacy keyword level):', len(founders))
    #print('Founders or Important Persons associated with the organization:', founders)
    ####################################################################################################################

    ####################################################################################################################
    # Extract founders using nltk - Not Effective
    #founders = extract_founders_nltk(join_sentences, enrich_vocab_list)
    #print('No. of Founders or Important Persons:', len(founders))
    #print('Founders or Important Persons associated with the organization:', founders)
    ####################################################################################################################

    ####################################################################################################################
    # Extract founders using spacy - in keyword level using OpenIE - Not Effective
    #founders = extract_founders_spacy_keyword_lvl_openie(join_sentences, enrich_vocab_list)
    #print('No. of Founders or Important Persons (using Spacy & OpenIE):', len(founders))
    #print('Founders or Important Persons associated with the organization:', str(founders))
    ####################################################################################################################

    ####################################################################################################################
    # Extract founders using Spacy, AllenNLP - Not Effective
    #founders = extract_founders_spacy_and_allennlp_keyword(join_sentences, enrich_vocab_list, org)
    #print('No. of Founders or Important Persons (using Spacy & Allen NLP):', len(founders))
    #print('Founders or Important Persons associated with the organization:', str(founders))
    ####################################################################################################################

    ####################################################################################################################
    # Extract founders using AllenNLP and OpenIE to further fine-tune it
    founders, _list_, filterd_person_names = extract_founders_allennlp(join_sentences, enrich_vocab_list, org)
    print('No. of Founders or Important Persons (Allen NLP):', len(founders))
    print('Founders or Important Persons associated with the organization:', str(founders))
    print('Founders or Important Persons associated with the organization after filtering:', str(filterd_person_names))
    print()
    ####################################################################################################################



if __name__ == "__main__":
    main()
