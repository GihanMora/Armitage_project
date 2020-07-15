# Author        :Sajani Ranasinghe
# Task          :Extract the founders, co-founders and important persons of an organization through the deep crawled pages
# Pre-conditions:The script uses RocketReach, NeverBounce APIs and AllenNLP, Glove Stanford embeddings
# pip install torch===1.5.0 torchvision===0.6.0 -f https://download.pytorch.org/whl/torch_stable.html
# Libraries
import re
import sys
import spacy # version 2.2.4
import string
import requests
import rocketreach # version 2.1.0
import numpy as np # version 1.18.4
import neverbounce_sdk # version 4.2.8
from scipy import spatial # version 1.4.1
from bson import ObjectId
from fuzzywuzzy import fuzz
from collections import OrderedDict
nlp = spacy.load("en_core_web_sm")
from allennlp.predictors.predictor import Predictor # version 1.0.0rc3
from itertools import groupby
from fuzzywuzzy import process
from urllib.parse import urlparse
from fuzzysearch import find_near_matches
import subprocess
from spacy.lang.en import English
from openie import StanfordOpenIE
import allennlp_models.ner.crf_tagger #version 1.0.0rc3
from stanfordnlp.server import CoreNLPClient # version 0.2.0
#import pymongo
#from spacy import displacy
#from collections import Counter
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('maxent_ne_chunker')
#nltk.download('words')
#nlp.add_pipe(nlp.create_pipe('sentencizer'))

from os.path import dirname as up
three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)

# from scrape_linkedin import ProfileScraper, HEADLESS_OPTIONS
from Simplified_System.Database.db_connect import refer_collection
# from Simplified_System.linkedin_data_crawler.linkedin_crawling import scrape_person
from Simplified_System.Initial_Crawling.get_n_search_results import getGoogleLinksForSearchText


# Function to read the file containing the GLOVE embeddings from Stanford
def read_Glove_file():

    # Dictionary to hold the word mappings
    embeddings_dict = {}
    # Read the text file containing the GLOVE embeddings from Stanford
    with open( three_up+'//Simplified_System//Contact_persons_from_website//glove.6B.50d.txt', 'r', encoding="utf-8") as f:
        for line in f:
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            embeddings_dict[word] = vector

    return embeddings_dict

# Function to find similar words
def find_closest_embeddings(embedding, embeddings_dict):
    return sorted(embeddings_dict.keys(), key=lambda word: spatial.distance.euclidean(embeddings_dict[word], embedding))

# Function to extract the description, header and paragraph text from the crawled data for a given record_id to an extended list
def extract_data(def_entry_id):

    mycol = refer_collection()
    comp_data_entry = mycol.find({'_id': ObjectId(def_entry_id)})
    data = [i for i in comp_data_entry]
    print('data:', data)
    # extracted_data = data[0]['header_text'] + [data[0]["description"]] + data[0]["paragraph_text"]
    try:
        extracted_data = data[0]['header_text'] + data[0]["paragraph_text"]
    except KeyError:
        extracted_data = None

    return extracted_data

# Function to get the required text from the given entry id and return the type
def get_company(def_entry_id, key):

    type = None
    flag = False
    check_link_list = ['www.', '.com', 'https', 'http']
    mycol = refer_collection()
    comp_data_entry = mycol.find({'_id': ObjectId(def_entry_id)})
    data = [i for i in comp_data_entry]
    comp_name = data[0][key]

    for i in range(len(check_link_list)):
        if check_link_list[i] in comp_name:
            flag = True
            type = 'link'
            break
    if flag == False:
        type = 'text'

    return comp_name, type

# Function to get the organization name
def get_org(company, type):

    if type == 'link':
        # Get the main company name to be searched when a link is given
        _netloc_ = urlparse(company).netloc
        if _netloc_ != '':
            if 'wiki' not in _netloc_:
                org = get_main_organization_link(_netloc_)[0]
            else:
                _netloc_ = ''
        if _netloc_ is '':
            org = get_main_organization_link(company)[0]

    elif type == 'text':
        # Some pre-processing to get the company only
        org = get_main_organization_text(company)

    return org

# Function to get the person names from dnb key value pair of the stored json
def get_persons_dnb(def_entry_id):

    mycol = refer_collection()
    comp_data_entry = mycol.find({'_id': ObjectId(def_entry_id)})
    data = [i for i in comp_data_entry]
    try:
        person_names = data[0]['dnb_cp_info']
        if len(person_names) > 1:
            person_names = person_names[-1]
        else:
            person_names = None
    except KeyError:
        return None

    return person_names

# Function to check if the directors/people listed in dnb have any association to the company through LinkedIn
def cross_check_person_linkedin(def_names, comp_name, status):

    title_link_list = []
    for i in range(len(def_names)):

        # Defining the search text on google
        if status == 'nested':
            name = def_names[i][0]
            search_text = name.lower() + ' ' + comp_name + ' linkedin'
        elif status == 'not nested':
            name = def_names[i]
            search_text = name.lower() + ' ' + comp_name + ' linkedin'

        # Searching google with the search text and extracting the titles and the links
        sr = getGoogleLinksForSearchText(search_text, 3, 'normal')
        filtered_li = []
        for p in sr:
            if 'linkedin.com' in p['link']:
                if '/in/' in p['link']:
                    if [p['title'], p['link']] not in title_link_list:
                        if [p['title'], p['link']] not in filtered_li:
                            filtered_li.append([p['title'], p['link']])

            title_link_list.extend(filtered_li)

    # Remove duplicates from the nested list
    fset = set(frozenset(x) for x in title_link_list)
    title_link_list = [list(x) for x in fset]

    names_in_profiles = []
    profile_urls = []
    # Extract the names and profile urls from the extracted profiles
    for i in range(len(title_link_list)):
        if 'linkedin.com' in title_link_list[i][1]:
            temp = title_link_list[i][0].split(' - ')
            names_in_profiles.append(temp[0])
            profile_urls.append(title_link_list[i][1])
        else:
            temp = title_link_list[i][1].split(' - ')
            names_in_profiles.append(temp[0])
            profile_urls.append(title_link_list[i][0])

    scraped_profiles = []
    # Scraping the linkedin profiles
    for i in range(len(profile_urls)):
        try:
            # profile_dict = scrape_person(profile_urls[i])
            profile_dict = {}
        except Exception:
            print('Exception Occurred')
            continue
        scraped_profiles.append(profile_dict)

    # Check if the person is associated with the company, if so extract them
    persons_associated = check_person_association_comp(scraped_profiles, comp_name, profile_urls)
    # Check if the persons associated is in the upper hierarchy of the company
    persons_relevant = check_if_important_person(persons_associated, ['co founder','co-founder','co-founded','co founded','co found','co-found','managing director','director',' ceo ', 'CEO', 'ceo',' coo ','founder','found','founding','executive director','chief executive officer','chief executive','chief operating officer', 'owner', 'chairman', 'chairperson'])

    return persons_relevant

# Function to check if the persons associated is in the upper hierarchy of the company
def check_if_important_person(person_list, important_person_list):

    final_person_list = []
    for i in range(len(person_list)):
        person_des = person_list[i]['job_title'].lower()
        for k in range(len(important_person_list)):
            if important_person_list[k] in person_des:
                if person_list[i] not in final_person_list:
                    final_person_list.append(person_list[i])

    return final_person_list

# Function to check if the person scraped from linkedin profile is associated with the company
def check_person_association_comp(scraped_linkedin_list, org, profile_urls):

    nested_list = []
    # Make a nested list [[scraped_linkedin_list, profile_urls]]
    for i in range(len(scraped_linkedin_list)):
        nested_list.append([scraped_linkedin_list[i], profile_urls[i]])

    title_list = []
    # Iterating through the scraped linkedin profiles
    for i in range(len(nested_list)):
        profile = nested_list[i][0]
        linkedin_url = nested_list[i][1]
        name = profile['personal_info']['name']
        jobs = profile['experiences']['jobs']

        for k in range(len(jobs)):
            job = jobs[k]
            # Fuzzy string match to check if the companies are the same
            par_ratio = fuzz.partial_ratio(job['company'].lower(), org.lower())
            ratio = fuzz.ratio(job['company'].lower(), org.lower())
            avg_ratio = (par_ratio + ratio)/2

            if avg_ratio >= 60:
                title_list.append({'name':name, 'job_title':job['title'], 'company':job['company'], 'linkedin_url':linkedin_url})

    return title_list

# Function to get email address of persons cross-checked with linkedIn using RocketReach
def get_email_address(names):

    rr = rocketreach.Gateway(rocketreach.GatewayConfig('756a0k4ed02a10eb8954855c811c8c5e82fe6a'))
    print(names)
    for i in range(len(names)):
        print(names[i])
        linkedin_url = names[i]['linkedin_url']

        # Find a valid email for a given person
        email_list = []
        result = rr.person.lookup(linkedin_url=linkedin_url)

        try:
            # Get only the valid email addresses using RocketReach API
            email_dict = result.person.emails
            for k in range(len(email_dict)):
                if email_dict[k]['smtp_valid'] == 'valid':
                    email_list.append(email_dict[k]['email'])

            if email_list == []:
                names[i].update({'email':None})
            elif email_list != []:
                names[i].update({'email':email_list})

        except AttributeError:
            names[i].update({'email': None})
            continue

    return names

# Function to write the important persons as a dictionary to MongoDB
def write_to_mongodb(names, entry_id):

    if names != []:
        mycol = refer_collection()
        mycol.update_one({'_id': ObjectId(entry_id)},
                         {'$set': {'important_person_company':names}})

    elif names == []:
        mycol = refer_collection()
        mycol.update_one({'_id': ObjectId(entry_id)},
                         {'$set': {'important_person_company': 'No important persons found'}})

    # mycol = refer_cleaned_collection()
    # comp_data_entry = mycol.find({"_id": entry_id})
    # data = [i for i in comp_data_entry]
    # print('Updated final mongodb record:', data)

# Function to generate all possible combinations of emails for a given person and verify them
def generate_validate_email(name, domain):

    # Remove punctuation from the name string
    name = name.translate(str.maketrans('', '', string.punctuation))
    name = name.lower().split()
    # Remove keyword from the list
    _list_ = ['dr', 'mr', 'mrs', 'miss', ' Co']
    for i in range(len(_list_)):
        if _list_[i] in name:
            name.remove(_list_[i])
    # Check if the length of the given keyword is greater than 2, to remove unnecessary keywords
    name_list = []
    for i in range(len(name)):
        if len(name[i]) > 2:
            name_list.append(name[i])

    print('org inside:', domain)
    domain_main = ['@'+domain]

    print('name_list:', name_list)
    # Split the name to a list
    if len(name_list) == 1:
        name = name_list[0]
        combinations = [name+'@'+domain, name[0]+'@'+domain]
    else:
        # Get the first name and the last name
        first_name = name_list[0]
        last_name = name_list[-1]

        # Define the different combinations/permutations of email possibilities
        combinations_main = [first_name+last_name,first_name+'.'+last_name,first_name+'_'+last_name,first_name[0]+'.'+last_name,first_name[0]+last_name,first_name,last_name,last_name+first_name,last_name+'.'+first_name,last_name+'_'+first_name]
        combinations = []
        for i in range(len(domain_main)):
            for k in range(len(combinations_main)):
                combinations.append(combinations_main[k] + domain_main[i])
                print(combinations_main[k] + domain_main[i])

    # Verify the combinations using NeverBounce API
    api_key = 'private_37bacd9d4f2ab6c8224cf5cecf825bb0'
    client = neverbounce_sdk.client(api_key=api_key, timeout=30)
    email_list = []

    # Iterating through the combination list
    for i in range(len(combinations)):
        try:
            resp = client.single_check(combinations[i])
            print('resp_result:', resp['result'])
            if resp['result'] == 'valid':
                print(combinations[i])
                email_list.append(combinations[i])
            else:
                try:
                    filename = open('unverified_emails.txt', "+a")
                    filename.write(combinations[i] + '\n')
                    filename.close()
                except UnicodeEncodeError:
                    print('UnicodeEncodeError')
                    continue

        except requests.exceptions.Timeout:
            print('Timeout Occurred')
            continue


    if email_list == []:
        email_list = None

    return email_list

# Function to verify emails where the emails value is None
def predict_emails(entry_id):

    # Get the data for important_person_company for the given entry id
    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": ObjectId(entry_id)})
    data = [i for i in comp_data_entry]
    important_person_company = data[0]['important_person_company']

    comp_name, type = get_company(entry_id, 'search_text')
    if type == 'link':
        org = get_org(comp_name, type)
    elif type == 'text':
        if len(data[0]['search_text']) <= 15:
            comp_name, type = get_company(entry_id, 'search_text')
            org = get_org(comp_name, type)
        elif len(data[0]['search_text']) > 15:
            comp_name, type = get_company(entry_id, 'comp_name')
            org = get_org(comp_name, type)

    if important_person_company != 'No important persons found':

        print(important_person_company)
        # Iterating through the list of persons
        for i in range(len(important_person_company)):
            email = important_person_company[i]['email']

            if email == None:
                # Generate all possible combinations of emails and verify
                email_list = generate_validate_email(important_person_company[i]['name'], org)
                important_person_company[i]['email'] = email_list

            elif email != None:
                continue

        # Write back to the MongoDB record, the updated emails
        write_to_mongodb(important_person_company, entry_id)

# Function to extract sentences where the contact people from dnb exist
# And check if the keywords appear in the selected sentences and return the contact persons
def check_person_dnb_website(def_people_dnb_list, join_sentences, enrich_vocab_list):

    # Extract the sentences by splitting it by '.'
    sents = split_to_sentences(join_sentences)
    sents = extract_sentences(sents, enrich_vocab_list)

    sents_list = []
    for i in range(len(sents)):
        for k in range(len(def_people_dnb_list)):
            flag = fuzzy_extract(def_people_dnb_list[k][0].lower(), sents[i], 50, 6)
            if flag == True:
                sents_list.append(def_people_dnb_list[k][0])

    # Remove duplicates from the list
    sents_list = list(set(sents_list))
    if sents_list != []:
        return sents_list
    else:
        return None

# Function to enrich the vocabulary using the GLOVE model
def enrich_vocab(embeddings_dict):

    def_list = ['founder']
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
    _list_ = ['ceasing', 'postpone', 'proceed', 'underway', 'builder', 'pioneer', 'founding', 'start', 'started', 'entrepreneur', 'recommence']
    for i in range(len(_list_)):
        if _list_[i] in keywords:
            keywords.remove(_list_[i])

    # Extend the keyword list with two more keywords | Might have to include 'owner', 'owned', 'director'
    keywords.extend(['established', ' dates from ', 'start-up', 'startup', 'cofounder', 'cofounded', 'investor'])

    # Remove duplicates from the keyword list
    keywords = list(set(keywords))

    return keywords

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

# Function to split to sentences by '.'
def split_to_sentences(join_sentences):
    long_sentence = join_sentences.split('.')
    return long_sentence

# Function to extract names of different tags using AllenNLp
def extract_names_allenNLP(join_sentences):

    # predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/ner-model-2020.02.10.tar.gz")
    predictor = Predictor.from_path(three_up+"\\Simplified_System\\Contact_persons_from_website\\ner-model-2020.02.10.tar.gz")
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
    predictor = Predictor.from_path(
        three_up+"\\Simplified_System\\Contact_persons_from_website\\ner-model-2020.02.10.tar.gz")

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

# Function to extract organizations names when link is provided
def get_main_organization_link(link):

    org = []
    rem = re.findall('\W+|\w+', str(link))
    remove_list = ['.', ',', '-', '_', ':', ';', 'https', 'http', 'www', 'au', 'com', 'wiki', '/', '//', '\*', 'ca', 'co', 'un', 'lk', 'za', 'en', 'web', 'net', 'org', 'wikipedia']
    for i in range(len(rem)):
        if rem[i] not in remove_list:
            if len(rem[i]) > 2:
                org.append(rem[i])
    return org

# Function to extract organizations names when text is provided
def get_main_organization_text(text):

    text = text.lower()
    if '.' in text:
        text_list = text.split('.')
        remove_list = ['au', 'com', 'nz', 'ac', 'uk', 'net', 'gov', 'govt']
        for k in range(len(remove_list)):
            if remove_list[k] in text_list:
                text_list.remove(remove_list[k])
        text = ''.join(text_list)

    elif '.' not in text:
        remove_list = ['.', ',', '-', '_', ':', ';', ' pty', ' ltd', ' inc', ' llc', ' co ', 'org', 'australia', 'limited']
        for i in range(len(remove_list)):
            if remove_list[i] in text:
                text = text.replace(remove_list[i], '')

    # Remove the leading and trailing white spaces
    text = text.lstrip()
    text = text.rstrip()

    return text

# Function to perform fuzzy string matching to check if a ~company name exist within the sentence
def fuzzy_extract(qs, ls, threshold, l_dist):

    _flag_ = False
    for word, _ in process.extractBests(qs, (ls,), score_cutoff=threshold):
        for match in find_near_matches(qs, word, max_l_dist=l_dist):
            match = word[match.start:match.end]
            index = ls.find(match)
            # if index != None and index > 0:
            if index != None:
                _flag_ = True

    return _flag_

# Function to extract founders using Allen NLP in sentence level
def extract_founders_allennlp(join_sentences, enrich_vocab_list, org):

    # Remove duplicates from the enrich vocab list
    enrich_vocab_list = list(set(enrich_vocab_list))

    # Extract the sentences by splitting it by '.'
    sents = split_to_sentences(join_sentences)
    sents = extract_sentences(sents, enrich_vocab_list)
    print('Sentences having the enrich vocab:', sents)

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

    # Remove duplicates from the _list_
    _list_ = list(set(_list_))
    print('No. of sentences Allen NLP is used:', len(_list_))

    if _list_ != []:
        # Get the person names
        person_names = extract_names_allenNLP(' '.join(_list_))
        print('Person names using Allen NLP:', person_names)
        # Fine-tune the founder extraction by performing OpenIE on the final list(_list_)
        # filtered_person_names = relation_ext_OpenIE(person_names, _list_, enrich_vocab_list, org)

    elif _list_ == []:
        person_names = []

    return person_names, _list_

# Function to extract the important persons role/position
def extract_person_postion(list_sentences, enrich_vocab_list, person_names):

    lst = []
    for i in range(len(person_names)):
        for k in range(len(list_sentences)):
            if person_names[i] in list_sentences[k]:
                for j in range(len(enrich_vocab_list)):
                    if enrich_vocab_list[j] in list_sentences[k].lower():
                        res = any(person_names[i] in sublist for sublist in lst)
                        if res == False:
                            lst.append([person_names[i], enrich_vocab_list[j]])

    return lst

# Function to perform extended founder search using LinkedIn cross checking
def main_founder_search(id_list):

    # Read the text file containing the GLOVE embeddings from Stanford and enrich the vocabulary with similar meaning to founder
    embeddings_dict = read_Glove_file()
    enrich_vocab_list = enrich_vocab(embeddings_dict)

    for entry_id in id_list:

        # Get the company name
        comp_name, type = get_company(entry_id, 'comp_name')
        print('Entry Id:', entry_id)
        print('Stored company name:', comp_name)

        persons_dnb = get_persons_dnb(entry_id)
        flag = False
        if persons_dnb == []:
            flag = True
        if persons_dnb == None:
            flag = True
        print('Persons found in D&B:', persons_dnb)

        # Get organization name
        org = get_org(comp_name, type)
        print('Organization: ' + str(org))

        # Extract the data related to the description, header and paragraph text in form of an extended list and joining the extracted data
        extracted_data = extract_data(entry_id)
        if extracted_data == None:
            write_to_mongodb([], entry_id)
            print('*** No extracted data ***')

        if extracted_data != None:
            join_sentences = ' '.join(extracted_data)
            chairperson_flag = True
            # Check for chairman or chairpersons of a company
            chairperson, _list_ = extract_founders_allennlp(join_sentences, ['chairman', 'chairperson'], org)
            print('Chairman or Chairperson:', chairperson)

            # Cross check the chairman list with LinkedIn
            if chairperson != []:
                print('Cross-checking Chairman or Chairperson with linkedin profiles')
                names = cross_check_person_linkedin(chairperson, org, 'not nested')
                if names != []:
                    # Update the output names by appending email addresses using RocketReach
                    # names= get_email_address(names)
                    write_to_mongodb(names, entry_id)
                    print('Chairman/Important persons associated with company after LinkedIn cross-checking:', names)
                    print('Updated MongoDB')
                if names == []:
                    chairperson_flag = False
            if chairperson == []:
                chairperson_flag = False

            # If there exist no chairman or chairpersons
            if chairperson_flag == False:
                print('No mentioning of Chairman or Chairpersons in the website')

                # If there exist people in the dnb
                if flag == False:
                    # Check if the persons listed in dnb has any association with the mentioned organization
                    print('Cross-checking with linkedin profiles to check the persons mentioned in the D&B are associated with the company')
                    names = cross_check_person_linkedin(persons_dnb, org, 'nested')

                    if names == []:
                        # Extract founders/co-founders/directors/managing director/CEO from the crawled text AllenNLP
                        founders, _list_ = extract_founders_allennlp(join_sentences,enrich_vocab_list + ['co founder','co-founder','co-founded', 'co founded','co found','co-found','managing director','director',' ceo ','coo ','founder', 'found','founding','executive director','chief executive officer','chief executive','chief operating officer',' owner '], org)
                        print('Founders or Important Persons of the organization in the website:', str(founders))

                        if founders != []:
                            # Cross-check with LinkedIn
                            print('Cross-checking founders/co-founders/managing directors etc. with LinkedIn profiles')
                            names = cross_check_person_linkedin(founders, org, 'not nested')

                            if names != []:
                                # Update the output names by appending email addresses using RocketReach
                                # names = get_email_address(names)
                                write_to_mongodb(names, entry_id)
                                print('Important persons associated with company after LinkedIn cross-checking:', names)
                                print('Updated MongoDB')

                            if names == []:
                                write_to_mongodb(names, entry_id)
                                print('No important persons found')
                                print('Updated MongoDB')

                        if founders == []:
                            write_to_mongodb(founders, entry_id)
                            print('No important persons found')
                            print('Updated MongoDB')

                    if names != []:
                        # Update the output names by appending email addresses using RocketReach
                        # names = get_email_address(names)
                        write_to_mongodb(names, entry_id)
                        print('Chairman/Important persons associated with company after LinkedIn cross-checking:', names)
                        print('Updated MongoDB')


                elif flag == True:
                    # Extract founders/co-founders/directors/managing director/CEO from the crawled text AllenNLP
                    founders, _list_ = extract_founders_allennlp(join_sentences,enrich_vocab_list + ['co founder', 'co-founder','co-founded', 'co founded','co found', 'co-found','managing director', 'director',' ceo ', ' coo ', 'founder', 'found','founding', 'executive director','chief executive officer','chief executive','chief operating officer', ' owner '], org)
                    print('Founders or Important Persons of the organization in the website:', str(founders))

                    # Cross-check with LinkedIn
                    if founders != []:
                        print('Cross-checking founders/co-founders/managing directors etc. with LinkedIn profiles')
                        names = cross_check_person_linkedin(founders, org, 'not nested')

                        if names != []:
                            # Update the output names by appending email addresses using RocketReach
                            # names = get_email_address(names)
                            write_to_mongodb(names, entry_id)
                            print('Chairman/Important persons associated with company after linkedin cross-checking:', names)
                            print('Updated MongoDB')

                        if names == []:
                            write_to_mongodb(names, entry_id)
                            print('No important persons found')
                            print('Updated MongoDB')

                    if founders == []:
                        write_to_mongodb(founders, entry_id)
                        print('No important persons found')
                        print('Updated MongoDB')

            # Uncomment if not needed to predict the emails of the contact persons
            # Predict the emails for contact persons using NeverBounce, i.e the emails which couldn't be predicted through RocketReach
            # print('Predicting emails using NeverBounce')
            # predict_emails(entry_id)
            print('*** DONE ***')
            print()

# Function to perform extended founder search WITHOUT using LinkedIn cross checking
def main_founder_search_v2(id_list):

    """
    :param id_list  : entry_id list
    :return         : None
                    : The updated MongoDB records with the attribute important_person_company
                    : eg: important_person_company: [[important person name, role]]
    """

    # Read the text file containing the GLOVE embeddings from Stanford and enrich the vocabulary with similar meaning to founder
    embeddings_dict = read_Glove_file()
    enrich_vocab_list = enrich_vocab(embeddings_dict)
    print("Extracting contacts from website")
    for entry_id in id_list:
        try:
            # Get the company name
            entry_id = str(entry_id)
            comp_name, type = get_company(entry_id, 'comp_name')
            print('Entry Id:', entry_id)
            print('Stored company name:', comp_name)

            # Get organization name
            org = get_org(comp_name, type)
            print('Organization: ' + str(org))

            # Extract the data related to the description, header and paragraph text in form of an extended list and joining the extracted data
            extracted_data = extract_data(entry_id)
            if extracted_data == None:
                write_to_mongodb([], entry_id)
                print('*** No extracted data ***')

            if extracted_data != None:
                join_sentences = ' '.join(extracted_data)
                chairperson_flag = True

                # Check for chairman or chairpersons of a company exist in crawled text
                chairperson, _list_ = extract_founders_allennlp(join_sentences, ['chairman', 'chairperson'], org)
                chairperson = extract_person_postion(_list_, ['chairman', 'chairperson'], chairperson)
                print('Chairman or Chairperson:', chairperson)

                if chairperson != []:
                    write_to_mongodb(chairperson, entry_id)
                    print('Updated MongoDB')

                if chairperson == []:
                    chairperson_flag = False

                # If there exist no chairman or chairpersons
                if chairperson_flag == False:
                    print('No mentioning of Chairman or Chairpersons in the website')

                    # Extract founders/co-founders/directors/managing director/CEO from the crawled text AllenNLP
                    founders, _list_ = extract_founders_allennlp(join_sentences,enrich_vocab_list + ['co founder','co-founder','co-founded','co founders','co-founders','co founded','co found','co-found','managing director','director',' ceo ','coo ','founder', 'found','founding','executive director','chief executive officer','chief executive','chief operating officer',' owner '], org)
                    founders = extract_person_postion(_list_, ['co founder','co-founder','co found','co-found','managing director','director',' ceo ','coo ','founder','founders', 'executive director','chief executive officer','chief executive','chief operating officer',' owner '], founders)
                    print('Founders or Important Persons of the organization in the website:', str(founders))

                    write_to_mongodb(founders, entry_id)
                    print('Updated MongoDB')

                print('*** DONE ***')
        except SyntaxError as e:
            print("syntax",e)
        # except Exception as e:
        #     print("Exception Occured while extracting contacts from website",e)





# def main():


    # The founders/important persons of an organization can be found by running the main_founder_search(entry_id_list),
    # eg: main_founder_search(['5eb703a2a86cec7b42163618', '5eb703b9a86cec7b42163619'])
    # or
    # The main_founder_search(entry_id_list) can be embedded in the main pipeline
    # eg: main_founder_search(['5eb63aff81de1c4846fd91ab'])

    # The following entry ids are updated with the important_person_company key value pair, in the refer_cleaned_collection()
    # updated_entry_id_list = ['5eb703a2a86cec7b42163618','5eb703b9a86cec7b42163619','5eb6a058cd265d6ef2ee766f','5eb66dabf3d5b58ef16a4c74','5eb7c4fd9a65a3d7609e4fd1','5eb7f2e0a97054c1c28ae403','5eb71606b7411bc8fe5ec287','5eb68e2fab2ce0451e2b4056','5eb762a5646627514dad781a','5eb67a4c109ddab70aec7b2d','5eb652de55de509b4a9efaf4','5eb76342646627514dad781f','5eb71564b7411bc8fe5ec282','5eb66bb449a0728d932475bc','5eb6a21fe632eaf0b1d593db','5eb65f2cde8cab37cd68dffd','5eb6820dcc1fecfea5009f48','5eb762fd646627514dad781c','5eb7d6a0f75273c9af329f7a','5eb6bbbee2f17c3f3238cec8','5eb689814e048265dd507dbc','5eb650acab06d680d6990351','5eb639ee2c60aae411d1ae8b','5eb8081955584ed5ddbe68f3','5eb7026aa86cec7b4216360a','5eb6734f61272a1489607d7c','5eb64a8e96bdd2bbbb3287e5','5eb672382cf60f5b673dc845','5eb8080355584ed5ddbe68f2','5eb6a930b440ebf60d42d6c2','5eb697cac579ca076779cb0f','5eb7c5bb9a65a3d7609e4fd4','5eb7c5d19a65a3d7609e4fd5','5eb7f3a7a97054c1c28ae40a','5eb64bc810a22fecd4eca987','5eb661a6796445df9bfd756d','5eb698a46de98c90f95a497d','5eb7f323a97054c1c28ae405','5eb70280a86cec7b4216360b','5eb7d6e4f75273c9af329f7d','5eb7f34ea97054c1c28ae407','5eb699a671806057e76f0141','5eb65433af5bcc3efe32c504','5eb727682d11eabb9aa47f83','5eb6567909d0de1b6b708cf8','5eb64f4ea0549166c51ca057','5eb6bdb1e7b6cc4614eb0edb','5eb6afc4e15b344d1a3aafa0','5eb695e1ffe996bbe09292fe','5eb6ab260aef4a583d77118f','5eb7273c2d11eabb9aa47f81','5eb7f364a97054c1c28ae408','5eb7f415a97054c1c28ae40f','5eb63539be65b70e5af0c7a9','5eb8085b55584ed5ddbe68f6','5eb7038ca86cec7b42163617','5eb70333a86cec7b42163613','5eb8084555584ed5ddbe68f5','5eb67bc12373d9a910e8750f','5eb646ce3b4442b4da91c057','5eb66a9b90f9dd06f1107866','5eb66ce4535d821544a14dee','5eb690bd8d99ac316303ffb6','5eb6944565d7b2466379f198','5eb7157ab7411bc8fe5ec283','5eb7639d646627514dad7822','5eb657e754ee9cbe1a7388c8','5eb651bc5fa088c453991725','5eb6556c29c37695bc97bec4','5eb68d458e708541f4671189','5eb7d6fbf75273c9af329f7e','5eb7f441a97054c1c28ae411','5eb634492802acb8c48e02aa','5eb70305a86cec7b42163611','5eb68405b8f3f1e1b3084a52','5eb67952c38498d75c86627f','5eb7d6b7f75273c9af329f7b','5eb6853a626f824ef428e315','5eb7f3d3a97054c1c28ae40c','5eb7d5d6f75273c9af329f72','5eb6631b245b7e033d0f92ed','5eb6b9158f232307ce0bdc13','5eb676209d0d155a1c6530f3','5eb6378b772150870b5c8d27','5eb76261646627514dad7817','5eb6af2a6012ca09c1728130','5eb762e6646627514dad781b','5eb76385646627514dad7821','5eb808f055584ed5ddbe68f9','5eb6688cf9acda3a876322e4','5eb68b52298db2bd4cebdd0e','5eb690038f7f6e26b6253fd5','5eb7d61bf75273c9af329f75','5eb62e2a134cc6fb9536e93d','5eb7d631f75273c9af329f76','5eb69a7d5587c492135fd56c','5eb6b71e5cd9b7b54c7d9961','5eb6311c86662885174692de','5eb808a355584ed5ddbe68f7','5eb682ecd810c81378eb806d','5eb7154eb7411bc8fe5ec281','5eb6479687b6932b9e6de098','5eb7f3e9a97054c1c28ae40d','5eb71591b7411bc8fe5ec284','5eb7d604f75273c9af329f74','5eb6783b3dd775bea489b02d','5eb6a8462d272649f7b4df95','5eb680d98c70c48229cd26b6','5eb7f338a97054c1c28ae406','5eb807ec55584ed5ddbe68f1','5eb6363894bd0b097f9c2734','5eb6ac1bfff106a6f58c42e7','5eb7161db7411bc8fe5ec288','5eb714ebb7411bc8fe5ec27d','5eb65942b46918d079adebe9','5eb640560732058562a400b3','5eb7628f646627514dad7819','5eb69c52d1ecab806f2beead','5eb67d3dd9818bcd44884d39','5eb694f59c10ae1d407b7c2a','5eb64e13158973dfa9982019','5eb6918fa2e66438837c2d83','5eb8091c55584ed5ddbe68fb','5eb68edce0b5b75b05fba1e6','5eb670c2382a70cea3c90149','5eb7d6cef75273c9af329f7c','5eb68c65501e64174bede873','5eb6b38eeb5e21b75a0d7cdb','5eb6b45f4dab807be8d7a28a','5eb69b6fc6cad85bd913e12a','5eb6bca1b68e7672cd0ef210','5eb67e66b7921dcf1c2e6805','5eb702d9a86cec7b4216360f','5eb7c4bb9a65a3d7609e4fcf','5eb69cefc81bdf1aac4bf6a1','5eb630147afe26eca4ba7bfa','5eb7277f2d11eabb9aa47f84','5eb66401b0e60a643fae0467','5eb6603b6e69c6f2e1092cf8','5eb675384beae11731a0ce35','5eb7031ca86cec7b42163612','5eb6a72dfc5d1c47d4ca9cd1','5eb7d689f75273c9af329f79','5eb7f2f8a97054c1c28ae404','5eb7f461a97054c1c28ae412','5eb7d5eef75273c9af329f73','5eb6925a31a5f94e1207b916','5eb7f37aa97054c1c28ae409','5eb76205646627514dad7813','5eb7c5149a65a3d7609e4fd2','5eb70376a86cec7b42163616','5eb7624b646627514dad7816','5eb70254a86cec7b42163609','5eb7c5e89a65a3d7609e4fd6','5eb727522d11eabb9aa47f82','5eb64cfc8c94747a21f39855','5eb702c2a86cec7b4216360e','5eb63c1e9c69232f6ed6edd8','5eb65d83728ad01002b3a5f6','5eb68a771a268ae85ef97960','5eb6ad1662db4e6c180a378b','5eb7621e646627514dad7814','5eb6bfc707fd60d7d77844de','5eb6b53fd8471918b43146b7','5eb7636f646627514dad7820','5eb6777b140e783b3524f4d9','5eb8093255584ed5ddbe68fc','5eb6746b3f8078c646a32068','5eb6ae390bdb0b194f41f9b3','5eb66682dc99a524418da337','5eb7f3bda97054c1c28ae40b','5eb76278646627514dad7818','5eb7f3ffa97054c1c28ae40e','5eb702efa86cec7b42163610','5eb6bad32c05d6f34cf32652','5eb7d72bf75273c9af329f7f','5eb7d652f75273c9af329f77','5eb715a7b7411bc8fe5ec285','5eb6a12f7ef80a97c531cc67','5eb63e1ee805d1cff3d80a25','5eb6beca47492aa1e0553de4','5eb70296a86cec7b4216360c','5eb7023ba86cec7b42163608','5eb688a782ee2ac4699515f2','5eb726fb2d11eabb9aa47f7f','5eb71538b7411bc8fe5ec280','5eb6b19b1c6e630676c62445','5eb648bf6bc924ef46ab60da','5eb67fa821374c1c36ea76bb','5eb69e087e9ea4385e20beed','5eb6b61fabf00d5fdb2d05a3','5eb71518b7411bc8fe5ec27f','5eb7f42aa97054c1c28ae410','5eb71501b7411bc8fe5ec27e','5eb6aa15b5b4db2c7393254c','5eb63ee743b668cb27ef8137','5eb715bdb7411bc8fe5ec286','5eb63aff81de1c4846fd91ab','5eb65b645417d406270e7e63','5eb65a927cb5b3a1ff4ae362','5eb70349a86cec7b42163614','5eb808d955584ed5ddbe68f8','5eb7d669f75273c9af329f78','5eb6b9dbb8b6b03010c4dcc6','5eb7c55d9a65a3d7609e4fd3','5eb6a63fc0820e4534126e94','5eb667a554cc6bc47dbfea44','5eb7d742f75273c9af329f80','5eb66e99e95b7d86f2518828','5eb63d1b9d2ec0b892c42dd5','5eb8082f55584ed5ddbe68f4','5eb66fa738555190120005d2','5eb6331597c8f5512179c4f1','5eb696f6ef36438bec383b7e','5eb714d5b7411bc8fe5ec27c','5eb69f48a04ce33b509b4895','5eb702aca86cec7b4216360d','5eb6651284c93e9e1b685024','5eb669883e6dc49bd6f1540f','5eb631f1fac479799dedd1f8','5eb6b2a5a9211572420260e9','5eb8090655584ed5ddbe68fa','5eb70360a86cec7b42163615','5eb714beb7411bc8fe5ec27b']


    # main_founder_search() function is updated to main_founder_search_v2()
    # Where the founders/important persons of an organization is extracted from crawled text without cross checking through LinkedIn
    # main_founder_search_v2(['5eb63aff81de1c4846fd91ab'])



# if __name__ == "__main__":
#     main()

all_ids_fixed = [ObjectId('5eb62e2a134cc6fb9536e93d'), ObjectId('5eb630147afe26eca4ba7bfa'), ObjectId('5eb6311c86662885174692de'), ObjectId('5eb631f1fac479799dedd1f8'), ObjectId('5eb6331597c8f5512179c4f1'), ObjectId('5eb634492802acb8c48e02aa'), ObjectId('5eb63539be65b70e5af0c7a9'), ObjectId('5eb6363894bd0b097f9c2734'), ObjectId('5eb6378b772150870b5c8d27'), ObjectId('5eb639ee2c60aae411d1ae8b'), ObjectId('5eb63aff81de1c4846fd91ab'), ObjectId('5eb63c1e9c69232f6ed6edd8'), ObjectId('5eb63d1b9d2ec0b892c42dd5'), ObjectId('5eb63e1ee805d1cff3d80a25'), ObjectId('5eb63ee743b668cb27ef8137'), ObjectId('5eb640560732058562a400b3'), ObjectId('5eb646ce3b4442b4da91c057'), ObjectId('5eb6479687b6932b9e6de098'), ObjectId('5eb648bf6bc924ef46ab60da'), ObjectId('5eb64a8e96bdd2bbbb3287e5'), ObjectId('5eb64bc810a22fecd4eca987'), ObjectId('5eb64cfc8c94747a21f39855'), ObjectId('5eb64e13158973dfa9982019'), ObjectId('5eb64f4ea0549166c51ca057'), ObjectId('5eb650acab06d680d6990351'), ObjectId('5eb651bc5fa088c453991725'), ObjectId('5eb652de55de509b4a9efaf4'), ObjectId('5eb65433af5bcc3efe32c504'), ObjectId('5eb6556c29c37695bc97bec4'), ObjectId('5eb6567909d0de1b6b708cf8'), ObjectId('5eb657e754ee9cbe1a7388c8'), ObjectId('5eb65942b46918d079adebe9'), ObjectId('5eb65a927cb5b3a1ff4ae362'), ObjectId('5eb65b645417d406270e7e63'), ObjectId('5eb65d83728ad01002b3a5f6'), ObjectId('5eb65f2cde8cab37cd68dffd'), ObjectId('5eb6603b6e69c6f2e1092cf8'), ObjectId('5eb661a6796445df9bfd756d'), ObjectId('5eb6631b245b7e033d0f92ed'), ObjectId('5eb66401b0e60a643fae0467'), ObjectId('5eb6651284c93e9e1b685024'), ObjectId('5eb66682dc99a524418da337'), ObjectId('5eb667a554cc6bc47dbfea44'), ObjectId('5eb6688cf9acda3a876322e4'), ObjectId('5eb669883e6dc49bd6f1540f'), ObjectId('5eb66a9b90f9dd06f1107866'), ObjectId('5eb66bb449a0728d932475bc'), ObjectId('5eb66ce4535d821544a14dee'), ObjectId('5eb66dabf3d5b58ef16a4c74'), ObjectId('5eb66e99e95b7d86f2518828'), ObjectId('5eb66fa738555190120005d2'), ObjectId('5eb670c2382a70cea3c90149'), ObjectId('5eb672382cf60f5b673dc845'), ObjectId('5eb6734f61272a1489607d7c'), ObjectId('5eb6746b3f8078c646a32068'), ObjectId('5eb675384beae11731a0ce35'), ObjectId('5eb676209d0d155a1c6530f3'), ObjectId('5eb6777b140e783b3524f4d9'), ObjectId('5eb6783b3dd775bea489b02d'), ObjectId('5eb67952c38498d75c86627f'), ObjectId('5eb67a4c109ddab70aec7b2d'), ObjectId('5eb67bc12373d9a910e8750f'), ObjectId('5eb67d3dd9818bcd44884d39'), ObjectId('5eb67e66b7921dcf1c2e6805'), ObjectId('5eb67fa821374c1c36ea76bb'), ObjectId('5eb680d98c70c48229cd26b6'), ObjectId('5eb6820dcc1fecfea5009f48'), ObjectId('5eb682ecd810c81378eb806d'), ObjectId('5eb68405b8f3f1e1b3084a52'), ObjectId('5eb6853a626f824ef428e315'), ObjectId('5eb688a782ee2ac4699515f2'), ObjectId('5eb689814e048265dd507dbc'), ObjectId('5eb68a771a268ae85ef97960'), ObjectId('5eb68b52298db2bd4cebdd0e'), ObjectId('5eb68c65501e64174bede873'), ObjectId('5eb68d458e708541f4671189'), ObjectId('5eb68e2fab2ce0451e2b4056'), ObjectId('5eb68edce0b5b75b05fba1e6'), ObjectId('5eb690038f7f6e26b6253fd5'), ObjectId('5eb690bd8d99ac316303ffb6'), ObjectId('5eb6918fa2e66438837c2d83'), ObjectId('5eb6925a31a5f94e1207b916'), ObjectId('5eb6944565d7b2466379f198'), ObjectId('5eb694f59c10ae1d407b7c2a'), ObjectId('5eb695e1ffe996bbe09292fe'), ObjectId('5eb696f6ef36438bec383b7e'), ObjectId('5eb697cac579ca076779cb0f'), ObjectId('5eb698a46de98c90f95a497d'), ObjectId('5eb699a671806057e76f0141'), ObjectId('5eb69a7d5587c492135fd56c'), ObjectId('5eb69b6fc6cad85bd913e12a'), ObjectId('5eb69c52d1ecab806f2beead'), ObjectId('5eb69cefc81bdf1aac4bf6a1'), ObjectId('5eb69e087e9ea4385e20beed'), ObjectId('5eb69f48a04ce33b509b4895'), ObjectId('5eb6a058cd265d6ef2ee766f'), ObjectId('5eb6a12f7ef80a97c531cc67'), ObjectId('5eb6a21fe632eaf0b1d593db'), ObjectId('5eb6a63fc0820e4534126e94'), ObjectId('5eb6a72dfc5d1c47d4ca9cd1'), ObjectId('5eb6a8462d272649f7b4df95'), ObjectId('5eb6a930b440ebf60d42d6c2'), ObjectId('5eb6aa15b5b4db2c7393254c'), ObjectId('5eb6ab260aef4a583d77118f'), ObjectId('5eb6ac1bfff106a6f58c42e7'), ObjectId('5eb6ad1662db4e6c180a378b'), ObjectId('5eb6ae390bdb0b194f41f9b3'), ObjectId('5eb6af2a6012ca09c1728130'), ObjectId('5eb6afc4e15b344d1a3aafa0'), ObjectId('5eb6b19b1c6e630676c62445'), ObjectId('5eb6b2a5a9211572420260e9'), ObjectId('5eb6b38eeb5e21b75a0d7cdb'), ObjectId('5eb6b45f4dab807be8d7a28a'), ObjectId('5eb6b53fd8471918b43146b7'), ObjectId('5eb6b61fabf00d5fdb2d05a3'), ObjectId('5eb6b71e5cd9b7b54c7d9961'), ObjectId('5eb6b9158f232307ce0bdc13'), ObjectId('5eb6b9dbb8b6b03010c4dcc6'), ObjectId('5eb6bad32c05d6f34cf32652'), ObjectId('5eb6bbbee2f17c3f3238cec8'), ObjectId('5eb6bca1b68e7672cd0ef210'), ObjectId('5eb6bdb1e7b6cc4614eb0edb'), ObjectId('5eb6beca47492aa1e0553de4'), ObjectId('5eb6bfc707fd60d7d77844de'), ObjectId('5eb6644657dfd2c0b8ad6f9c'), ObjectId('5eb66630e46c2996611e7cc5'), ObjectId('5eb6670c8f3766d3901e7cc5'), ObjectId('5eb667a2f46d5b17e51e7cc5'), ObjectId('5eb66860dab176b3721e7cc5'), ObjectId('5eb6694f13214ceb901e7cc5'), ObjectId('5eb66a1c57d33385281e7cc5'), ObjectId('5eb66b0449715b12861e7cc5'), ObjectId('5eb66bf5c1cd3d67511e7cc5'), ObjectId('5eb66c7efae3969f0e1e7cc5'), ObjectId('5eb66d66b19f4175d41e7cc5'), ObjectId('5eb66e13afcaca79e81e7cc5'), ObjectId('5eb66f73241434c0231e7cc5'), ObjectId('5eb670975ce27f20651e7cc5'), ObjectId('5eb671403fb856baf01e7cc5'), ObjectId('5eb67202016c9eb49e1e7cc5'), ObjectId('5eb672855afc1f3bff1e7cc5'), ObjectId('5eb6732dc2f2cb21251e7cc5'), ObjectId('5eb674640480c494e21e7cc5'), ObjectId('5eb6753ed2085581291e7cc5'), ObjectId('5eb675ac19586b800c1e7cc5'), ObjectId('5eb6763b038d799aef1e7cc5'), ObjectId('5eb6776343946ae8fd1e7cc5'), ObjectId('5eb677f187e92c00051e7cc5'), ObjectId('5eb678eca5ef5a63181e7cc5'), ObjectId('5eb67989fc5079ac861e7cc5'), ObjectId('5eb67aa9307135b7481e7cc5'), ObjectId('5eb67c33c565dca3e61e7cc5'), ObjectId('5eb67d0c36a91550ff1e7cc5'), ObjectId('5eb67ddb4336d384b01e7cc5'), ObjectId('5eb67e90ae420cabcb1e7cc5'), ObjectId('5eb67f5ca8076cfd0a1e7cc5'), ObjectId('5eb68003bb68bcb7741e7cc5'), ObjectId('5eb6810f033af4b22b1e7cc5'), ObjectId('5eb681edb0a260b22a1e7cc5'), ObjectId('5eb682821dc3ebab081e7cc5'), ObjectId('5eb68355a25586c25d1e7cc5'), ObjectId('5eb6846e050a0737611e7cc5'), ObjectId('5eb6856e4c8a5b802f1e7cc5'), ObjectId('5eb6864268930af1f51e7cc5'), ObjectId('5eb686de941ea6f14b1e7cc5'), ObjectId('5eb688c6e8ba899a231e7cc5'), ObjectId('5eb689bf25abe779da1e7cc5'), ObjectId('5eb68afe1af2ab98d31e7cc5'), ObjectId('5eb68bf65c40e7d0d71e7cc5'), ObjectId('5eb68f5da4fd71f5821e7cc5'), ObjectId('5eb690478934691bf01e7cc5'), ObjectId('5eb6913eabf312822a1e7cc5'), ObjectId('5eb691e4f27c5211d21e7cc5'), ObjectId('5eb692b5bb6685adac1e7cc5'), ObjectId('5eb693d2d045d59f3b1e7cc5'), ObjectId('5eb6950c33fb947c391e7cc5'), ObjectId('5eb695e258473bd2511e7cc5'), ObjectId('5eb6968b400af16b271e7cc5'), ObjectId('5eb69733109de20b7e1e7cc5'), ObjectId('5eb697d1fb1caa3d7c1e7cc5'), ObjectId('5eb6988dc9615b33321e7cc5'), ObjectId('5eb69968d9785183931e7cc5'), ObjectId('5eb69a96a657bfc8991e7cc5'), ObjectId('5eb69c9f160e789d7e1e7cc5'), ObjectId('5eb69d5dd8d4ba89261e7cc5'), ObjectId('5eb69e1a46e5e5f33b1e7cc5'), ObjectId('5eb69f2843ef874fb81e7cc5'), ObjectId('5eb6a18ae6c27a5e961e7cc5'), ObjectId('5eb6a230795dc98ebd1e7cc5'), ObjectId('5eb6a2ee6c39588d0c1e7cc5'), ObjectId('5eb6a3d924946bdefc1e7cc5'), ObjectId('5eb6a504d1511c119a1e7cc5'), ObjectId('5eb6a5c37baf5cbfaa1e7cc5'), ObjectId('5eb6a670bc98e2e1471e7cc5'), ObjectId('5eb6a7b02266f527831e7cc5'), ObjectId('5eb6a895c2e3166bcc1e7cc5'), ObjectId('5eb6a9f32ea14a40531e7cc5'), ObjectId('5eb6aa92ee8178abc81e7cc5'), ObjectId('5eb6ab66c0c668b01d1e7cc5'), ObjectId('5eb6b0e61efe4c8c1f1e7cc5'), ObjectId('5eb6b168313d3030621e7cc5'), ObjectId('5eb6b201a201f790431e7cc5'), ObjectId('5eb6b361ce454282431e7cc5'), ObjectId('5eb6b3e04b08fc11b61e7cc5'), ObjectId('5eb6b49ef2b0c3149b1e7cc5'), ObjectId('5eb6b59f9ea7d290471e7cc5'), ObjectId('5eb6b675d1df7e04541e7cc5'), ObjectId('5eb6b75ef05682bd561e7cc5'), ObjectId('5eb6b8a9b0bfa077aa1e7cc5'), ObjectId('5eb6b928dd96b98b8b1e7cc5'), ObjectId('5eb6ba00d479014c311e7cc5'), ObjectId('5eb6bafd19a91c6bc11e7cc5'), ObjectId('5eb6bbe2c4e683d6001e7cc5'), ObjectId('5eb6bd08754af87d741e7cc5'), ObjectId('5eb6bd6f88582ed22e1e7cc5'), ObjectId('5eb6be6b9a04c870951e7cc5'), ObjectId('5eb6bf9531912db86d1e7cc5'), ObjectId('5eb6c13482dff544b31e7cc5'), ObjectId('5eb6c2265a296856911e7cc5'), ObjectId('5eb6c4f7fc8c7e73f71e7cc5'), ObjectId('5eb6c70a75e27bc9f01e7cc5'), ObjectId('5eb6c8e8f1c972d9d11e7cc5'), ObjectId('5eb6c9a73c6af847871e7cc5'), ObjectId('5eb6cad795a02f54c11e7cc5'), ObjectId('5eb6cbbb8e1ea19f721e7cc5'), ObjectId('5eb6cd0b76b872aac31e7cc5'), ObjectId('5eb6cf8d2afda4b75b1e7cc5'), ObjectId('5eb6d0b930966bc45d1e7cc5'), ObjectId('5eb6d180d6c5e588bc1e7cc5'), ObjectId('5eb6d2f157712c0e6b1e7cc5'), ObjectId('5eb6d3e51fd67335b41e7cc5'), ObjectId('5eb6d4b11fa223ec991e7cc5'), ObjectId('5eb6d573eeef09f4631e7cc5'), ObjectId('5eb6d5ed1ea282b3c71e7cc5'), ObjectId('5eb6d80ebb52c48b521e7cc5'), ObjectId('5eb6d92a12a10caf0b1e7cc5'), ObjectId('5eb6d9b2ad56eddd801e7cc5'), ObjectId('5eb6da581aea51c4141e7cc5'), ObjectId('5eb6db02d64b5ffaf01e7cc5'), ObjectId('5eb6dbee173c3e60211e7cc5'), ObjectId('5eb6dd0a8975e79a311e7cc5'), ObjectId('5eb6ddce3b3856712c1e7cc5'), ObjectId('5eb6de8bef8013ae3a1e7cc5'), ObjectId('5eb6dfa18548b41f1e1e7cc5'), ObjectId('5eb6e025a38f0a5bd51e7cc5'), ObjectId('5eb6e1bdc3b80c65f01e7cc5'), ObjectId('5eb6e2e985f544c0f31e7cc5'), ObjectId('5eb6e46fe2a11439211e7cc5'), ObjectId('5eb6e4e68944fb51261e7cc5'), ObjectId('5eb6e5f72810e4528c1e7cc5'), ObjectId('5eb6e71e229726a60d1e7cc5'), ObjectId('5eb6e833e6819157ab1e7cc5'), ObjectId('5eb6e92a73b223baa71e7cc5'), ObjectId('5eb6eb8eddadc0791a1e7cc5'), ObjectId('5eb6ecdfb8eac020ef1e7cc5'), ObjectId('5eb6ef069fd3d2700e1e7cc5'), ObjectId('5eb6f05e6cccb4ec201e7cc5'), ObjectId('5eb6f1abab044238231e7cc5'), ObjectId('5eb6f2785c17eeee301e7cc5'), ObjectId('5eb6f33f610110f7811e7cc5'), ObjectId('5eb6f5f338500f639d1e7cc5'), ObjectId('5eb6f75c547b2dc8a81e7cc5'), ObjectId('5eb6f86fa74f3f01391e7cc5'), ObjectId('5eb6faac13ef4ea5f11e7cc5'), ObjectId('5eb6fdc8c9af34d4321e7cc5'), ObjectId('5eb7015b64a4225c3e1e7cc5'), ObjectId('5eb701c9fd7dd6f0f81e7cc5'), ObjectId('5eb70303b9bd62c2d81e7cc5'), ObjectId('5eb707e40b3d32a9441e7cc5'), ObjectId('5eb70a317191684f471e7cc5'), ObjectId('5eb70b32d76dd257a81e7cc5'), ObjectId('5eb70c4eec6b83a56c1e7cc5'), ObjectId('5eb70d32fe79fe7ae11e7cc5'), ObjectId('5eb70dfc9b8c5669f61e7cc5'), ObjectId('5eb70e8d034df06da41e7cc5'), ObjectId('5eb70fe65ae110a83f1e7cc5'), ObjectId('5eb7108f8c31b21e521e7cc5'), ObjectId('5eb711cbd9698d895c1e7cc5'), ObjectId('5eb712ea41a21fd6dc1e7cc5'), ObjectId('5eb714466deb9085851e7cc5'), ObjectId('5eb714c5156d39e56e1e7cc5'), ObjectId('5eb7167ff888e8df4c1e7cc5'), ObjectId('5eb7172ad0c81b0d771e7cc5'), ObjectId('5eb718151826d970d21e7cc5'), ObjectId('5eb71938ccab1717f01e7cc5'), ObjectId('5eb71a2f30b005afe41e7cc5'), ObjectId('5eb71ad877b13eddbe1e7cc5'), ObjectId('5eb71ce921e8f2861f1e7cc5'), ObjectId('5eb71dca81f016c91a1e7cc5'), ObjectId('5eb71f0a7683d7d4101e7cc5'), ObjectId('5eb7203f4f2f7c0af81e7cc5'), ObjectId('5eb7213113ccf498df1e7cc5'), ObjectId('5eb7220bcc166c7e981e7cc5'), ObjectId('5eb72366ce65662b761e7cc5'), ObjectId('5eb7244a3dd3a2d7cc1e7cc5'), ObjectId('5eb72642b228878d531e7cc5'), ObjectId('5eb727cdaecb81e9bf1e7cc5'), ObjectId('5eb728f7fc797b3e091e7cc5'), ObjectId('5eb72aac0a755be3db1e7cc5'), ObjectId('5eb72bb61eabe2ed531e7cc5'), ObjectId('5eb72cf9e1fce67eae1e7cc5'), ObjectId('5eb730746bb3b692581e7cc5'), ObjectId('5eb730f0b6bdb8bbfc1e7cc5'), ObjectId('5eb731a0a3a39894761e7cc5'), ObjectId('5eb732a744e4da73881e7cc5'), ObjectId('5eb733f0abb68d26771e7cc5'), ObjectId('5eb734c35daa087a711e7cc5'), ObjectId('5eb735c8092b0431131e7cc5'), ObjectId('5eb73fde13df6f7b301e7cc5'), ObjectId('5eb7412226ae5213cf1e7cc5'), ObjectId('5eb7438bfa589ddb521e7cc5'), ObjectId('5eb74470a02a1a69941e7cc5'), ObjectId('5eb746a1e8e7f7509f1e7cc5'), ObjectId('5eb748526f5ea73b621e7cc5'), ObjectId('5eb74998ba43f388011e7cc5'), ObjectId('5eb74b1ffa73ce5db21e7cc5'), ObjectId('5eb74c79daf84fbe7c1e7cc5'), ObjectId('5eb74daa8e571dfa141e7cc5'), ObjectId('5eb7896b081724025f640206'), ObjectId('5eb7897f081724025f640207'), ObjectId('5eb78992081724025f640208'), ObjectId('5eb789a4081724025f640209'), ObjectId('5eb789b6081724025f64020a'), ObjectId('5eb789c9081724025f64020b'), ObjectId('5eb789dc081724025f64020c'), ObjectId('5eb789ee081724025f64020d'), ObjectId('5eb78a01081724025f64020e'), ObjectId('5eb78a13081724025f64020f'), ObjectId('5eb78a25081724025f640210'), ObjectId('5eb78a38081724025f640211'), ObjectId('5eb78a4a081724025f640212'), ObjectId('5eb78a5d081724025f640213'), ObjectId('5eb78a6f081724025f640214'), ObjectId('5eb78a82081724025f640215'), ObjectId('5eb78a95081724025f640216'), ObjectId('5eb78aa7081724025f640217'), ObjectId('5eb78aba081724025f640218'), ObjectId('5eb7aadc52f1054848f5583f'), ObjectId('5eb7ab0452f1054848f55840'), ObjectId('5eb7ab3552f1054848f55841'), ObjectId('5eb7ab4752f1054848f55842'), ObjectId('5eb7ab5a52f1054848f55843'), ObjectId('5eb7ab6d52f1054848f55844'), ObjectId('5eb7ab8052f1054848f55845'), ObjectId('5eb7ab9252f1054848f55846'), ObjectId('5eb7abc752f1054848f55847'), ObjectId('5eb7abda52f1054848f55848'), ObjectId('5eb7abec52f1054848f55849'), ObjectId('5eb7bf7b11ad0e77a8454c20'), ObjectId('5eb7bf9a11ad0e77a8454c21'), ObjectId('5eb7bfac11ad0e77a8454c22'), ObjectId('5eb7bfe611ad0e77a8454c23'), ObjectId('5eb7c00211ad0e77a8454c24'), ObjectId('5eb7c01411ad0e77a8454c25'), ObjectId('5eb7c02811ad0e77a8454c26'), ObjectId('5eb7c03b11ad0e77a8454c27'), ObjectId('5eb7c04d11ad0e77a8454c28'), ObjectId('5eb7c05f11ad0e77a8454c29'), ObjectId('5eb7c07c11ad0e77a8454c2a'), ObjectId('5eb7c08e11ad0e77a8454c2b'), ObjectId('5eb7c0a011ad0e77a8454c2c'), ObjectId('5eb81d4d312f24e51eaa1661'), ObjectId('5eb81d6b312f24e51eaa1662'), ObjectId('5eb81d7d312f24e51eaa1663'), ObjectId('5eb81da1312f24e51eaa1664'), ObjectId('5eb81db3312f24e51eaa1665'), ObjectId('5eb81dc6312f24e51eaa1666'), ObjectId('5eb81dd8312f24e51eaa1667'), ObjectId('5eb81dea312f24e51eaa1668'), ObjectId('5eb81dfd312f24e51eaa1669'), ObjectId('5eb81e2a312f24e51eaa166a'), ObjectId('5eb81e3d312f24e51eaa166b'), ObjectId('5eb81e4f312f24e51eaa166c'), ObjectId('5eb83bb0c20632fd5f21f86d'), ObjectId('5eb83c8a6623055fd421f86d'), ObjectId('5eb83dd63612e8063d21f86d'), ObjectId('5eb83e9d7f0be3c68d21f86d'), ObjectId('5eb83f62e799b9666421f86d'), ObjectId('5eb8417497a7e1b24921f86d'), ObjectId('5eb842cdd24ad47da321f86d'), ObjectId('5eb84387d74544658d21f86d'), ObjectId('5eb844b48bd34e3bcb21f86d'), ObjectId('5eb8452dab8cc3965d21f86d'), ObjectId('5eb845f3acb80ec7c321f86d'), ObjectId('5eb846d473cb9c981121f86d'), ObjectId('5eb847ff38670c0bf521f86d'), ObjectId('5eb848f164dc91c82021f86d'), ObjectId('5eb84a27e7e7c4410d21f86d'), ObjectId('5eb84b2e74c886c55621f86d'), ObjectId('5eb84bdab796088dd121f86d'), ObjectId('5eb84df11ad39fb85b21f86d'), ObjectId('5eb84eadd4bb82049521f86d'), ObjectId('5eb84fe508717ac7dd21f86d'), ObjectId('5eb8517e89396f769e21f86d'), ObjectId('5eb85245d92e9c836b21f86d'), ObjectId('5eb853490aaf61fffc21f86d'), ObjectId('5eb8545dbd6648186b21f86d'), ObjectId('5eb855aa4a7a482fac21f86d'), ObjectId('5eb856dcb34632d71421f86d'), ObjectId('5eb858ab89ca8a714f21f86d'), ObjectId('5eb85a05917001c29321f86d'), ObjectId('5eb85afdfdc73635ab21f86d'), ObjectId('5eb85c4ac83e2ed19721f86d'), ObjectId('5eb85d15da02c4e01821f86d'), ObjectId('5eb85dab7bfffd11c521f86d'), ObjectId('5eb85e43aa8c7e619421f86d'), ObjectId('5eb85f63862fafb0e021f86d'), ObjectId('5eb86122ce929d30d721f86d'), ObjectId('5eb8623bdac3bd4e7f21f86d'), ObjectId('5eb86330ca955600ac21f86d'), ObjectId('5eb863dbb3620c184721f86d'), ObjectId('5eb86507eaccbefb4d21f86d'), ObjectId('5eb866198421e3010421f86d'), ObjectId('5eb8672d51cf71b03d21f86d'), ObjectId('5eb8685ab30e6a462321f86d'), ObjectId('5eb868ec94d882c47c21f86d'), ObjectId('5eb86a31de8016954a21f86d'), ObjectId('5eb86b55f632667f7e21f86d'), ObjectId('5eb86c08d1a5f8db5f21f86d'), ObjectId('5eb86cc182031d652821f86d'), ObjectId('5eb86d4e9609a169d021f86d'), ObjectId('5eb86dfe3b429177a721f86d'), ObjectId('5eb86e7cac9651095921f86d'), ObjectId('5eb86f7613cbb54fe721f86d'), ObjectId('5eb870500793149fa821f86d'), ObjectId('5eb871bfb7374d40cf21f86d'), ObjectId('5eb873c205f65c055421f86d'), ObjectId('5eb8754af638182f4521f86d'), ObjectId('5eb8760ff7dcca255d21f86d'), ObjectId('5eb87727974768f30821f86d'), ObjectId('5eb8780e8d8c35ca9c21f86d'), ObjectId('5eb87917ea8377045721f86d'), ObjectId('5eb879f2b83e5d3a8e21f86d'), ObjectId('5eb87a9ca4a19ac29321f86d'), ObjectId('5eb87ba1dc1e218e7421f86d'), ObjectId('5eb87c945b332f05d121f86d'), ObjectId('5eb87dbc2074be568b21f86d'), ObjectId('5eb87eca54f8828b4e21f86d'), ObjectId('5eb87fb20c0112b7ad21f86d'), ObjectId('5eb880b1614e84a77a21f86d'), ObjectId('5eb881e8f31ce00d4a21f86d'), ObjectId('5eb8831ab323150e1621f86d'), ObjectId('5eb88412761d7e71c921f86d'), ObjectId('5eb884e6d62901c44821f86d'), ObjectId('5eb885858ec581dcd221f86d'), ObjectId('5eb886a2151d63eaee21f86d'), ObjectId('5eb88723f57be6e74e21f86d'), ObjectId('5eb88819f0ffd1483a21f86d'), ObjectId('5eb888dcfd39cc64d921f86d'), ObjectId('5eb889f4ff01ae732f21f86d'), ObjectId('5eb88ad5479569d7e321f86d'), ObjectId('5eb88bbf9c23677f5c21f86d'), ObjectId('5eb88d68f362f40c3421f86d'), ObjectId('5eb88e682df9b5110721f86d'), ObjectId('5eb88f98a60f86f3ef21f86d'), ObjectId('5eb890aa418697e9e421f86d'), ObjectId('5eb8921599a8e5b1f621f86d'), ObjectId('5eb8933c424b54e75121f86d'), ObjectId('5eb8943b6f1514ca3321f86d'), ObjectId('5eb89535aabccb4aab21f86d'), ObjectId('5eb896c896f67bcbc321f86d'), ObjectId('5eb8978f89169ba53d21f86d'), ObjectId('5eb898be51220c01de21f86d'), ObjectId('5eb89a57e84723b8ec21f86d'), ObjectId('5eb89c1e05692d835d21f86d'), ObjectId('5eb89d659149fe900a21f86d'), ObjectId('5eb89df91960c5e9ec21f86d'), ObjectId('5eb89ecd8bf8c16ccf21f86d'), ObjectId('5eb89febd32a61b6c321f86d'), ObjectId('5eb8a1447e730f301521f86d'), ObjectId('5eb8a239464da6884521f86d'), ObjectId('5eb8a30c88d5b4a59121f86d'), ObjectId('5eb8a3f0482eb3feca21f86d'), ObjectId('5eb8a4a6ae599bdfa921f86d'), ObjectId('5eb8a5d1d36fe9f4e121f86d'), ObjectId('5eb8a709099797362b21f86d'), ObjectId('5eb8a83745cee6157a21f86d'), ObjectId('5eb8a955ddc60d84d721f86d'), ObjectId('5eb8aa2e549e722cf921f86d'), ObjectId('5eb8ab15843916c1ec21f86d'), ObjectId('5eb8ab897019bd41e021f86d'), ObjectId('5eb8acf5ec58bd651021f86d'), ObjectId('5eb8adf340037d708b21f86d'), ObjectId('5eb8aed47b8ce2708b21f86d'), ObjectId('5eb8b0273477405e3921f86d'), ObjectId('5eb8b16eeb46817aa921f86d'), ObjectId('5eb8b262c08e90f27321f86d'), ObjectId('5eb8b2c39a33df091821f86d'), ObjectId('5eb8b3cd429175d72321f86d'), ObjectId('5eb8b4c5d1c21dd7ce21f86d'), ObjectId('5eb8b5d7c385759b1421f86d'), ObjectId('5eb8b75137347cbaa321f86d'), ObjectId('5eb8b84c47dde0acac21f86d'), ObjectId('5eb8b912b06f3bcb0421f86d'), ObjectId('5eb8b9855c080d2f1121f86d'), ObjectId('5eb8ba493dc9c4974f21f86d'), ObjectId('5eb8bb252743a7288021f86d'), ObjectId('5eb8bcdf968edc55ea21f86d'), ObjectId('5eb8bd998572a191e321f86d'), ObjectId('5eb8bea3f03d66565d21f86d'), ObjectId('5eb8bfba829032dce021f86d'), ObjectId('5eb8c14565f929811d21f86d'), ObjectId('5eb8c1d5fe1ba67fcd21f86d'), ObjectId('5eb8c2b414da7621f021f86d'), ObjectId('5eb8c3875259f3781f21f86d'), ObjectId('5eb8c491832b7b76fa21f86d'), ObjectId('5eb8c5fcb8a1c0352b21f86d'), ObjectId('5eb8c6dcb28e55297a21f86d'), ObjectId('5eb8c7e1d74c10705521f86d'), ObjectId('5eb8c9b046a9eb0b8621f86d'), ObjectId('5eb8ca4045be5799f521f86d'), ObjectId('5eb8cb349dcab3b90c21f86d'), ObjectId('5eb8cc5df291ba000021f86d'), ObjectId('5eb8ccfeb6f8890b1521f86d'), ObjectId('5eb8cee6ce909d778c21f86d'), ObjectId('5eb8d0d95c7b35b7c421f86d'), ObjectId('5eb8d1d3c01e5308b521f86d'), ObjectId('5eb8d3459b83f4fa6121f86d'), ObjectId('5eb8d4fdabcf9fb65c21f86d'), ObjectId('5eb8d5cb9be0efb86721f86d'), ObjectId('5eb8d681e47422a52421f86d'), ObjectId('5eb8d6fa86dbdd4f6221f86d'), ObjectId('5eb8d806a0f83f495121f86d'), ObjectId('5eb8d9a9e7a770a3ad21f86d'), ObjectId('5eb8dab1a54485a67d21f86d'), ObjectId('5eb8dbd9e608e62aa921f86d'), ObjectId('5eb8dd2eb8359de9fb21f86d'), ObjectId('5eb8de14e961249cf821f86d'), ObjectId('5eb8df468065ee492521f86d'), ObjectId('5eb8e093f2829184d021f86d'), ObjectId('5eb8e1c5e383a8096121f86d'), ObjectId('5eb8e23d68e392761821f86d'), ObjectId('5eb8e35659da95b81421f86d'), ObjectId('5eb8e4508f2df69ea521f86d'), ObjectId('5eb8e5bd8973815f4521f86d'), ObjectId('5eb8e7228500cd563621f86d'), ObjectId('5eb8e813d9d2c9f40121f86d'), ObjectId('5eb8e90528a65c503a21f86d'), ObjectId('5eb8ea3dade030acbc21f86d'), ObjectId('5eb8eb8f7e96c2e52021f86d'), ObjectId('5eb8ec3968930ce0dc21f86d'), ObjectId('5eb8eec96236e1001721f86d'), ObjectId('5eb8ef7b29e2302f9421f86d'), ObjectId('5eb8f03f60558f7f2821f86d'), ObjectId('5eb8f0f37637ebf2f421f86d'), ObjectId('5eb8f199e3d0f6397321f86d'), ObjectId('5eb8f298726ce61bc621f86d'), ObjectId('5eb8f3298d159182be21f86d'), ObjectId('5eb8f4027596476b4e21f86d'), ObjectId('5eb8f4c8b81159e2d121f86d'), ObjectId('5eb8f590fdb965d43a21f86d'), ObjectId('5eb8f6b6214f14826b21f86d'), ObjectId('5eb8f7d0b6e2fbd56f21f86d'), ObjectId('5eb8f8f640293aa81821f86d'), ObjectId('5eb8f9a0e6440a6b8a21f86d'), ObjectId('5eb8fa6df0d07e01bb21f86d'), ObjectId('5eb8fb6637371fbadd21f86d'), ObjectId('5eb8fc2111aa8649a021f86d'), ObjectId('5eb8fd315118a2341121f86d'), ObjectId('5eb8fddd76e458d1f521f86d'), ObjectId('5eb8fe80ab6df587b721f86d'), ObjectId('5eb8ff3c18d32b70bd21f86d'), ObjectId('5eb8ffde228b9dcd4721f86d'), ObjectId('5eb900d48f9aa5e01421f86d'), ObjectId('5eb9016e0b29a3ec7b21f86d'), ObjectId('5eb90231d7710ea89e21f86d'), ObjectId('5eb9030223ce0eaa0e21f86d'), ObjectId('5eb903bd297b7ab6ea21f86d'), ObjectId('5eb90466b8ff202ce721f86d'), ObjectId('5eb9051bd7cc3fdd4a21f86d'), ObjectId('5eb906268b04d8180921f86d'), ObjectId('5eb906b4ac1b87756821f86d'), ObjectId('5eb907adb885b0595e21f86d'), ObjectId('5eb908650c9ba6d0c721f86d'), ObjectId('5eb9098a548b88f22f21f86d'), ObjectId('5eb90aa037a21af96a21f86d'), ObjectId('5eb90b6ff57c66a55021f86d'), ObjectId('5eb90c97d95f0dfd8321f86d'), ObjectId('5eb90d26c24efc344421f86d'), ObjectId('5eb90defe65269ec2921f86d'), ObjectId('5eb90edc081077a28221f86d'), ObjectId('5eb90ff42891822aa721f86d'), ObjectId('5eb910de6bc058e77521f86d'), ObjectId('5eb9121e6b00d398d321f86d'), ObjectId('5eb912f7cf42d0dd1321f86d'), ObjectId('5eb913be1fed838a5421f86d'), ObjectId('5eb914608106a0349521f86d'), ObjectId('5eb915c6fee756399921f86d'), ObjectId('5eb9165c2023b5b0a221f86d'), ObjectId('5eb9172a5f87037fd821f86d'), ObjectId('5eb91804d3c4eabcb021f86d'), ObjectId('5eb918f8be95d058e821f86d'), ObjectId('5eb919d57a1990cecb21f86d'), ObjectId('5eb91ae4754abd427521f86d'), ObjectId('5eb91b88f67f334bd121f86d'), ObjectId('5eb91c5c9952bbf5a121f86d'), ObjectId('5eb91d09164fbbbaac21f86d'), ObjectId('5eb91da3788ecf0ce521f86d'), ObjectId('5eb91e8fa56f9483ce21f86d'), ObjectId('5eb91f39ed94b2224a21f86d'), ObjectId('5eb91ff051c237641c21f86d'), ObjectId('5eb920f94efa4817c021f86d'), ObjectId('5eb921bdedc138291621f86d'), ObjectId('5eb922aecb23d6990521f86d'), ObjectId('5eb923e3a13ac27f3a21f86d'), ObjectId('5eb9248a5ed09e3eea21f86d'), ObjectId('5eb92552b5646f410c21f86d'), ObjectId('5eb9263c768da2781321f86d'), ObjectId('5eb927549b6f7b419d21f86d'), ObjectId('5eb9282909dc67e37421f86d'), ObjectId('5eb929221bbcf7be6f21f86d'), ObjectId('5eb92a461d8435dcd921f86d'), ObjectId('5eb92afa636ef5238c21f86d'), ObjectId('5eb92ba8400dbda15921f86d'), ObjectId('5eb92c710bba61585121f86d'), ObjectId('5eb92d1830daa2538321f86d'), ObjectId('5eb92db361dff8952121f86d'), ObjectId('5eb92e3a89f495fffb21f86d'), ObjectId('5eb92f14ab9ce4f52721f86d'), ObjectId('5eb92fbf0c67b29a9d21f86d'), ObjectId('5eb9312dd15399709d21f86d'), ObjectId('5eb9323b820a6f535621f86d'), ObjectId('5eb93372d46993fbd721f86d'), ObjectId('5eb93429f1f936171a21f86d'), ObjectId('5eb93528186ec1081a21f86d'), ObjectId('5eb93751a44b8aefc721f86d'), ObjectId('5eb9381f8c2abb0f7a21f86d'), ObjectId('5eb938c55389d4db7521f86d'), ObjectId('5eb93967d1022da19a21f86d'), ObjectId('5eb93a35286bebbd3721f86d'), ObjectId('5eb93ad6ca0222976421f86d'), ObjectId('5eb93ba69a5bb9122221f86d'), ObjectId('5eb93ca853c2585cd021f86d'), ObjectId('5eb93d70f717e1186221f86d'), ObjectId('5eb93e5a0f155b463f21f86d'), ObjectId('5eb93f261b3133e13e21f86d'), ObjectId('5eb93fc62c92f2fd7a21f86d'), ObjectId('5eb9406f046057c71821f86d'), ObjectId('5eb940f8afecef72d421f86d'), ObjectId('5eb942ca6c178e0efd21f86d'), ObjectId('5eb94474a5cacd316f21f86d'), ObjectId('5eb945325c630e50b121f86d'), ObjectId('5eb945fbae4b1c370c21f86d'), ObjectId('5eb946b622486d789a21f86d'), ObjectId('5eb9476fbc961c207721f86d'), ObjectId('5eb9482c9f4c1019e321f86d'), ObjectId('5eb9492babf495d98021f86d'), ObjectId('5eb94a4a475222827e21f86d'), ObjectId('5eb94b5d81f9e4fb7a21f86d'), ObjectId('5eb94caf01a53921bf21f86d'), ObjectId('5eb94e5a2b07874ec121f86d'), ObjectId('5eb953a6814e7d21e321f86d'), ObjectId('5eb954b4f35a078cf721f86d'), ObjectId('5eb955a2e5f652442821f86d'), ObjectId('5eb95622a2c1b74c6221f86d'), ObjectId('5eb956c2bcbd15f71721f86d'), ObjectId('5eb9575c09862b02c421f86d'), ObjectId('5eb957e0b1f04156bd21f86d'), ObjectId('5eb958ead7392a242521f86d'), ObjectId('5eb959a6a700a8698721f86d'), ObjectId('5eb95a61fcaba234be21f86d'), ObjectId('5eb95b4882f4282eca21f86d'), ObjectId('5eb95cfb74762e537021f86d'), ObjectId('5eb95e0b322ca6d92b21f86d'), ObjectId('5eb95ee13787207a7121f86d'), ObjectId('5eb960159b562cfe5121f86d'), ObjectId('5eb961218c2c25bba721f86d'), ObjectId('5eb9623e7d5b6734b221f86d'), ObjectId('5eb9631ee5516c892621f86d'), ObjectId('5eb964411c69e097b721f86d'), ObjectId('5eb96558e18d2010a521f86d'), ObjectId('5eb96699db4578f41e21f86d'), ObjectId('5eb96777c06cc7453321f86d'), ObjectId('5eb968a6866513087c21f86d'), ObjectId('5eb969ff340cfd882f21f86d'), ObjectId('5eb96b5f67ab27c7ad21f86d'), ObjectId('5eb96c713854c44c7c21f86d'), ObjectId('5eb96e930abe67402d21f86d'), ObjectId('5eb96f8410dbd1b97121f86d'), ObjectId('5eb97050e14afd37d421f86d'), ObjectId('5eb97181a1c0acf29521f86d'), ObjectId('5eb9729dcfb1b5aedc21f86d'), ObjectId('5eb97380f4737bdfc621f86d'), ObjectId('5eb974b0d87fa029cc21f86d'), ObjectId('5eb975ec968778eb8321f86d'), ObjectId('5eb9773a705bc362dd21f86d'), ObjectId('5eb978928fcb381c9821f86d'), ObjectId('5eb979e6a8267a4cf321f86d'), ObjectId('5eb97b0f60e92f6b3c21f86d'), ObjectId('5eb97cb0b1b81f1f1121f86d'), ObjectId('5eb97d68a224556d5021f86d'), ObjectId('5eb97defa49bce200921f86d'), ObjectId('5eb97f0e0983cb7e1b21f86d'), ObjectId('5eb98037bd57a54e0921f86d'), ObjectId('5eb9814a3aa1b7828e21f86d'), ObjectId('5eb9828938c7d411f521f86d'), ObjectId('5eb983e524cbf9087f21f86d'), ObjectId('5eb98518b78a7be0a921f86d'), ObjectId('5eb985c3d4acd4f70321f86d'), ObjectId('5eb986b68377e255da21f86d'), ObjectId('5eb987b62d22e3927d21f86d'), ObjectId('5eb988e826bc569c4521f86d'), ObjectId('5eb98a0cf9f33e743e21f86d'), ObjectId('5eb98b60bd0350ef9421f86d'), ObjectId('5eb98c1aa42c5bfdb221f86d'), ObjectId('5eb98cc54fb80cdf1921f86d'), ObjectId('5eb98e6877b6929b6021f86d'), ObjectId('5eb98f63c77b06851a21f86d'), ObjectId('5eb98fe243b394756d21f86d'), ObjectId('5eb990fd55b72b8c5121f86d'), ObjectId('5eb991c373c817b2bb21f86d'), ObjectId('5eb992c4c0fd5f51a121f86d'), ObjectId('5eb99398736b4cd23721f86d'), ObjectId('5eb994d95eab3ba67221f86d'), ObjectId('5eb995d5fe3c5625c521f86d'), ObjectId('5eb996a983125131a121f86d'), ObjectId('5eb997dc39cd53206621f86d'), ObjectId('5eb998b240569a005a21f86d'), ObjectId('5eb999b37b891cb90621f86d'), ObjectId('5eb99acd846eb61f2a21f86d'), ObjectId('5eb99bcf2818e7046021f86d'), ObjectId('5eb99c9e646e68a4be21f86d'), ObjectId('5eb99d7f9b164a7cae21f86d'), ObjectId('5eb99e60690e8264fc21f86d'), ObjectId('5eb99f05e49d1227cd21f86d'), ObjectId('5eb99f72890089aa8921f86d'), ObjectId('5eb9a02446ec38c9b221f86d'), ObjectId('5eb9a0e02afb29a0c221f86d'), ObjectId('5eb9a2131454cdd80c21f86d'), ObjectId('5eb9a3161c2a9e14cd21f86d'), ObjectId('5eb9a4394b823b542921f86d'), ObjectId('5eb9a510ede9d735bb21f86d'), ObjectId('5eb9a5c5c24f6024db21f86d'), ObjectId('5eb9a6ddfce4130a7921f86d'), ObjectId('5eb9a7a0a5df084c9521f86d'), ObjectId('5eb9a90b6ed7a467e521f86d'), ObjectId('5eb9a9faae3bf308b421f86d'), ObjectId('5eb9ab221619cc9dc321f86d'), ObjectId('5eb9ac3d09f67fba8521f86d'), ObjectId('5eb9ad5d70c1226baa21f86d'), ObjectId('5eb9aea5fea105dfcb21f86d'), ObjectId('5eb9af637342fa7aa621f86d'), ObjectId('5eb9b040a8f4550b7f21f86d'), ObjectId('5eb9b1450406e3e2b321f86d'), ObjectId('5eb9b28a501fa5268421f86d'), ObjectId('5eb9b3072fc2705be521f86d'), ObjectId('5eb9b3801885a6622921f86d'), ObjectId('5eb9b44d4ee0fd99bb21f86d'), ObjectId('5eb9b517d4ae71db7f21f86d'), ObjectId('5eb9b5c9c60e3be81421f86d'), ObjectId('5eb9b7a6206f878ed521f86d'), ObjectId('5eb9b87e9dd4c7ca0621f86d'), ObjectId('5eb9b94210d23baa8f21f86d'), ObjectId('5eb9ba554ec213f32d21f86d'), ObjectId('5eb9bb86c18b4ececb21f86d'), ObjectId('5eb9bc50d2451747b621f86d'), ObjectId('5eb9bd5a3ad6427d8721f86d'), ObjectId('5eb9be1269310756c221f86d'), ObjectId('5eb9bf57b3f56179ae21f86d'), ObjectId('5eb9bfd43cef2bdc8b21f86d'), ObjectId('5eb9c193286421764421f86d'), ObjectId('5eb9c21d2884e8e37021f86d'), ObjectId('5eb9c35fea7b131dc021f86d'), ObjectId('5eb9c465c47657758321f86d'), ObjectId('5eb9c525b11354116b21f86d'), ObjectId('5eb9c643e192bb672a21f86d'), ObjectId('5eb9c762343f83b86d21f86d'), ObjectId('5eb9c864a7682e360921f86d'), ObjectId('5eb9c943cd65d837aa21f86d'), ObjectId('5eba2263f773e4001a6aa0f6'), ObjectId('5eba2352cedb2578006aa0f6'), ObjectId('5eba23efdd87446de86aa0f6'), ObjectId('5eba257fcc2f2c7c9c6aa0f6'), ObjectId('5eba2665b027044d6e6aa0f6'), ObjectId('5eba27389dcc86f4c06aa0f6'), ObjectId('5eba280fe4f85334f86aa0f6'), ObjectId('5eba28e8099768a4226aa0f6'), ObjectId('5eba29b6e888782e336aa0f6'), ObjectId('5eba2a5fec4bf6a2ac6aa0f6'), ObjectId('5eba2b4bc2a93be6f36aa0f6'), ObjectId('5eba2bcac660d396e06aa0f6'), ObjectId('5eba2c7910d3fcd0016aa0f6'), ObjectId('5eba2d1a34b0c190d96aa0f6'), ObjectId('5eba2df4477d2e3b636aa0f6'), ObjectId('5eba2f018e651e78046aa0f6'), ObjectId('5eba2f87b8a341be376aa0f6'), ObjectId('5eba300c9e893551cd6aa0f6'), ObjectId('5eba31b7f6172358836aa0f6'), ObjectId('5eba329963a55f0c8c6aa0f6'), ObjectId('5eba3301cfa7ca34776aa0f6'), ObjectId('5eba33ba769415bf8e6aa0f6'), ObjectId('5eba348b1bb03934586aa0f6'), ObjectId('5eba35a621d955a8846aa0f6'), ObjectId('5eba366d4f17291cf16aa0f6'), ObjectId('5eba377b06d5d7cae86aa0f6'), ObjectId('5eba37f95f008936766aa0f6'), ObjectId('5eba38c76af7ef3b7e6aa0f6'), ObjectId('5eba39d8508b3ebd7d6aa0f6'), ObjectId('5eba3ac085bbe969606aa0f6'), ObjectId('5eba3bc367f232bfc66aa0f6'), ObjectId('5eba3c539b68e6839d6aa0f6'), ObjectId('5eba3d4411a138ad6c6aa0f6'), ObjectId('5eba3e291a4d4152146aa0f6'), ObjectId('5eba3eb48cfb836bb26aa0f6'), ObjectId('5eba3f7712384cd39f6aa0f6'), ObjectId('5eba405603a6b818b36aa0f6'), ObjectId('5eba41451c03037ed46aa0f6'), ObjectId('5eba41f3e5f55f61626aa0f6'), ObjectId('5eba42c76eff662a836aa0f6'), ObjectId('5eba438af8df0e405c6aa0f6'), ObjectId('5eba44dffaff1040856aa0f6'), ObjectId('5eba465367e2e0746e6aa0f6'), ObjectId('5eba4709e77bc924246aa0f6'), ObjectId('5eba47b9b707e6f1e06aa0f6'), ObjectId('5eba48a2233f736bf66aa0f6'), ObjectId('5eba49569c892864786aa0f6'), ObjectId('5eba4a66d6d6339c0c6aa0f6'), ObjectId('5eba4d1c7865b19fa46aa0f6'), ObjectId('5eba4dd122d2726da76aa0f6'), ObjectId('5eba4f212327b4ff6a6aa0f6'), ObjectId('5eba4fe33a6073535d6aa0f6'), ObjectId('5eba5150149ebad13e6aa0f6'), ObjectId('5eba5331bb1bc22a246aa0f6'), ObjectId('5eba54d650564c9d836aa0f6'), ObjectId('5eba55801730aa03736aa0f6'), ObjectId('5eba567e096b17a0416aa0f6'), ObjectId('5eba57766d39f1ec2d6aa0f6'), ObjectId('5eba58cc19effd0e1a6aa0f6'), ObjectId('5eba59d4ae344110c06aa0f6'), ObjectId('5eba5b4b0f90c581b16aa0f6'), ObjectId('5eba5c24a3fd3760796aa0f6'), ObjectId('5eba5e0ce7638ef1516aa0f6'), ObjectId('5eba5ed41ca960da286aa0f6'), ObjectId('5eba60afba4fa3b36b6aa0f6'), ObjectId('5eba625b2d49e42e1c6aa0f6'), ObjectId('5eba630ac6804396ae6aa0f6'), ObjectId('5eba639dfe9d26a2cc6aa0f6'), ObjectId('5eba64b3905430eac56aa0f6'), ObjectId('5eba65976eef9fd32c6aa0f6'), ObjectId('5eba66a2de6f378f236aa0f6'), ObjectId('5eba67bb80950b7e306aa0f6'), ObjectId('5eba68fe5678fd00496aa0f6'), ObjectId('5eba6ab9dec9a444e86aa0f6'), ObjectId('5eba6bee75d3f006bf6aa0f6'), ObjectId('5eba6cd088ad4c0ff46aa0f6'), ObjectId('5eba6d4cd5ace97fb96aa0f6'), ObjectId('5eba6f05f4e96945a06aa0f6'), ObjectId('5eba7019c89d3f6e6a6aa0f6'), ObjectId('5eba711df07d9dbde96aa0f6'), ObjectId('5eba71b43d0da18b486aa0f6'), ObjectId('5eba72bf29bfd4fe486aa0f6'), ObjectId('5eba73be695509da3a6aa0f6'), ObjectId('5eba75450f6888ba2a6aa0f6'), ObjectId('5eba76512d6b7665f26aa0f6'), ObjectId('5eba7784b7471b3d796aa0f6'), ObjectId('5eba78960d9267723e6aa0f6'), ObjectId('5eba798394297e61d66aa0f6'), ObjectId('5eba7a7c8da40306ca6aa0f6'), ObjectId('5eba7bb375c77e62786aa0f6'), ObjectId('5eba7c6f8806297a7f6aa0f6'), ObjectId('5eba7d9acbebed16d16aa0f6'), ObjectId('5eba7e6a4ac93d07586aa0f6'), ObjectId('5eba7f641e610563e56aa0f6'), ObjectId('5eba8076eaae1336ac6aa0f6'), ObjectId('5eba81a29ac6ca027f6aa0f6'), ObjectId('5eba82d61569ae110d6aa0f6'), ObjectId('5eba83dc15c6efd50b6aa0f6'), ObjectId('5eba8547f25e4d61306aa0f6'), ObjectId('5eba873f2222b725b06aa0f6'), ObjectId('5eba87f883988b10aa6aa0f6'), ObjectId('5eba8963179bd48ab86aa0f6'), ObjectId('5eba8a414f293d8b036aa0f6'), ObjectId('5eba8b7bc165ac9a746aa0f6'), ObjectId('5eba8c007638f1558f6aa0f6'), ObjectId('5eba8ccb06aa805bef6aa0f6'), ObjectId('5eba8e0aae92c041386aa0f6'), ObjectId('5eba8ee7fbda26ac916aa0f6'), ObjectId('5eba9047a23e7af6b16aa0f6'), ObjectId('5eba91fff4b97f0bcb6aa0f6'), ObjectId('5eba9279d9e37a11566aa0f6'), ObjectId('5eba9323df5007ab736aa0f6'), ObjectId('5eba94739a5d337aba6aa0f6'), ObjectId('5eba9943e741efec006aa0f6'), ObjectId('5eba9a4ea65fa58bb06aa0f6'), ObjectId('5eba9b43e77fdcce046aa0f6'), ObjectId('5eba9c8a968247a8d76aa0f6'), ObjectId('5eba9dbe1bf1e1ed036aa0f6'), ObjectId('5eba9e6b969fcf61496aa0f6'), ObjectId('5eba9fd947665f99366aa0f6'), ObjectId('5ebaa11b7d17877bda6aa0f6'), ObjectId('5ebaa2c4104f2af4a96aa0f6'), ObjectId('5ebaa3cddd085426996aa0f6'), ObjectId('5ebaa4cbb057c14adb6aa0f6'), ObjectId('5ebaa5c8353d52e82e6aa0f6'), ObjectId('5ebaa6d4722cd892f56aa0f6'), ObjectId('5ebaa7cef9260e981b6aa0f6'), ObjectId('5ebaa88bb5b73f3fcb6aa0f6'), ObjectId('5ebaa9912eb6b5d8f26aa0f6'), ObjectId('5ebaaa8d1ac51d6f916aa0f6'), ObjectId('5ebaab8780587d952a6aa0f6'), ObjectId('5ebaac2b193157f6836aa0f6'), ObjectId('5ebaadebdb317e012b6aa0f6'), ObjectId('5ebaaedd4ced4de4306aa0f6'), ObjectId('5ebab0035cabfab4ef6aa0f6'), ObjectId('5ebab1279bd6e029266aa0f6'), ObjectId('5ebab2306a4e27a8386aa0f6'), ObjectId('5ebab33361d9f5e2666aa0f6'), ObjectId('5ebab3c510300b5ff76aa0f6'), ObjectId('5ebab4413d218c114f6aa0f6'), ObjectId('5ebab4fdbd5947bb256aa0f6'), ObjectId('5ebab5c182b35e046c6aa0f6'), ObjectId('5ebab6c12780d878da6aa0f6'), ObjectId('5ebab7794a8f375c3b6aa0f6'), ObjectId('5ebab834bfb2fd001a6aa0f6'), ObjectId('5ebab8b343f3393a5f6aa0f6'), ObjectId('5ebab9bc034f665cc26aa0f6'), ObjectId('5ebaba90ee31fa88276aa0f6'), ObjectId('5ebabb683764bc3eec6aa0f6'), ObjectId('5ebabcb754275a966c6aa0f6'), ObjectId('5ebabde785e42d4c986aa0f6'), ObjectId('5ebabf39293dbd093e6aa0f6'), ObjectId('5ebac08cffac78a0406aa0f6'), ObjectId('5ebac1f14aa92171216aa0f6'), ObjectId('5ebac30d8cb26d3f246aa0f6'), ObjectId('5ebac42d0ff4c7cf7a6aa0f6'), ObjectId('5ebac53e1a5cbe715b6aa0f6'), ObjectId('5ebac648b587a572b46aa0f6'), ObjectId('5ebac74e6acf2bb95e6aa0f6'), ObjectId('5ebac8372ee8ac336b6aa0f6'), ObjectId('5ebac8f47dd4237f9f6aa0f6'), ObjectId('5ebac9fe5b6414637b6aa0f6'), ObjectId('5ebacb1f229567f5d96aa0f6'), ObjectId('5ebacc2a81cd4e11bf6aa0f6'), ObjectId('5ebacd20a7b3dae2966aa0f6'), ObjectId('5ebacde1ae613e594b6aa0f6'), ObjectId('5ebacec04c41eee26f6aa0f6'), ObjectId('5ebad134649127b0af6aa0f6'), ObjectId('5ebad244d01ac6e8b06aa0f6'), ObjectId('5ebad345c5294710bd6aa0f6'), ObjectId('5ebad450edde3325cc6aa0f6'), ObjectId('5ebad5b1149ea3c87d6aa0f6'), ObjectId('5ebad67ab7380cbd126aa0f6'), ObjectId('5ebad76c8c21e0df746aa0f6'), ObjectId('5ebad8db94f2b114706aa0f6'), ObjectId('5ebadabfa4af8dfe4f6aa0f6'), ObjectId('5ebadbf9a0a8b573246aa0f6'), ObjectId('5ebadcb52dbeb1a2526aa0f6'), ObjectId('5ebadd7b6f82e334456aa0f6'), ObjectId('5ebaded573c25c747d6aa0f6'), ObjectId('5ebadfc61660f1acf06aa0f6'), ObjectId('5ebae0ebfbd5cc5b866aa0f6'), ObjectId('5ebae1e8f723d84a7e6aa0f6'), ObjectId('5ebae32315c974bd266aa0f6'), ObjectId('5ebae4895d510595eb6aa0f6'), ObjectId('5ebae51b6eb81889b66aa0f6'), ObjectId('5ebae5d0e078c54c4d6aa0f6'), ObjectId('5ebae692e2e081f7a56aa0f6'), ObjectId('5ebae79da17a846ef66aa0f6'), ObjectId('5ebae888c57f427f356aa0f6'), ObjectId('5ebae95136756eae276aa0f6'), ObjectId('5ebaea2741d1765d0f6aa0f6'), ObjectId('5ebaeadb466c8d6d1a6aa0f6'), ObjectId('5ebaebed364e6e646f6aa0f6'), ObjectId('5ebaecc5d4faa1b7116aa0f6'), ObjectId('5ebaedd33c500af46b6aa0f6'), ObjectId('5ebaeefe813b3d94046aa0f6'), ObjectId('5ebaf02f66e6b35cad6aa0f6'), ObjectId('5ebaf130a45a262ec36aa0f6'), ObjectId('5ebaf205269eba74566aa0f6'), ObjectId('5ebaf31c727be0a35f6aa0f6'), ObjectId('5ebaf4650f01d720626aa0f6'), ObjectId('5ebaf577044f6d8da06aa0f6'), ObjectId('5ebaf68a1c80e18bed6aa0f6'), ObjectId('5ebaf795137b20e3926aa0f6'), ObjectId('5ebaf8c4ae83bb5e476aa0f6'), ObjectId('5ebaf9e40d8eb1a5176aa0f6'), ObjectId('5ebafae203af48b0dd6aa0f6'), ObjectId('5ebafbf4c7ee87af176aa0f6'), ObjectId('5ebafd7507eff9111d6aa0f6'), ObjectId('5ebafe299ff39017936aa0f6'), ObjectId('5ebafee615da04b1646aa0f6'), ObjectId('5ebb0046ac06c34fc06aa0f6'), ObjectId('5ebb018598ee79d5536aa0f6'), ObjectId('5ebb038bd7e6a0bebc6aa0f6'), ObjectId('5ebb0457a0f18732ad6aa0f6'), ObjectId('5ebb057e834e6569dd6aa0f6'), ObjectId('5ebb06d867646869aa6aa0f6'), ObjectId('5ebb07c6f15e2d54bc6aa0f6'), ObjectId('5ebb08ce4151d3e1396aa0f6'), ObjectId('5ebb09ff7268acf8b56aa0f6'), ObjectId('5ebb0b08b2b6887d306aa0f6'), ObjectId('5ebb0c329735ae1f7f6aa0f6'), ObjectId('5ebb0d5f9cf7fb77476aa0f6'), ObjectId('5ebb0e492729174f736aa0f6'), ObjectId('5ebb0f4f6431a880276aa0f6'), ObjectId('5ebb102bf1e74e3c996aa0f6'), ObjectId('5ebb10dc2b7ed1c54d6aa0f6'), ObjectId('5ebb11e1da539786e56aa0f6'), ObjectId('5ebb12e5d3303de7976aa0f6'), ObjectId('5ebb13f027f78959816aa0f6'), ObjectId('5ebb14fb488f9a623b6aa0f6'), ObjectId('5ebb157b7b6f9f0ab06aa0f6'), ObjectId('5ebb16bcb3d0e568746aa0f6'), ObjectId('5ebb17d29f6f703ae16aa0f6'), ObjectId('5ebb1973869d3884ce6aa0f6'), ObjectId('5ebb1b2592796da28e6aa0f6'), ObjectId('5ebb1bad90ce0c25196aa0f6'), ObjectId('5ebb20a9dce43be37a6aa0f6'), ObjectId('5ebb21a830f9e211516aa0f6'), ObjectId('5ebb2304fb4ab518cb6aa0f6'), ObjectId('5ebb23d8615a7285726aa0f6'), ObjectId('5ebb246cb8f739279f6aa0f6'), ObjectId('5ebb2565bda0c8ad976aa0f6'), ObjectId('5ebb26a63768ab5fec6aa0f6'), ObjectId('5ebb27dc1e963b5e266aa0f6'), ObjectId('5ebb289996a0cbb8336aa0f6'), ObjectId('5ebb29102dcad31d896aa0f6'), ObjectId('5ebb2a101861d9bfd56aa0f6'), ObjectId('5ebb2b5759358f42b86aa0f6'), ObjectId('5ebb2bf6eef7c615c56aa0f6'), ObjectId('5ebb771c12d8507c296aa0f6'), ObjectId('5ebb7804dc3f93d04b6aa0f6'), ObjectId('5ebb78ed22da81f4096aa0f6'), ObjectId('5ebb79ae471ee598196aa0f6'), ObjectId('5ebb7ab29063aea3e96aa0f6'), ObjectId('5ebb7b9d643c42e52e6aa0f6'), ObjectId('5ebb7c96fb954f50b26aa0f6'), ObjectId('5ebb806d62aa3f1b736aa0f6'), ObjectId('5ebb81954f7aafaea36aa0f6'), ObjectId('5ebb8296a8ed6d09326aa0f6'), ObjectId('5ebb8429e7c427718e6aa0f6'), ObjectId('5ebb8569a436a562d76aa0f6'), ObjectId('5ebb863985f92bf7846aa0f6'), ObjectId('5ebb882f4f508a202c6aa0f6'), ObjectId('5ebb890e08de38906a6aa0f6'), ObjectId('5ebb8a5eac435a66bc6aa0f6'), ObjectId('5ebb8b8a247adf3bac6aa0f6'), ObjectId('5ebb8cdecc408edf436aa0f6'), ObjectId('5ebb8e4c80f02c418e6aa0f6'), ObjectId('5ebb8fea3499a27a476aa0f6'), ObjectId('5ebb914e219529bcd26aa0f6'), ObjectId('5ebb92cb76ec45be916aa0f6'), ObjectId('5ebb94372ad5f4459e6aa0f6'), ObjectId('5ebb954eb4b1733ba66aa0f6'), ObjectId('5ebb96b7b8ea5eddc86aa0f6'), ObjectId('5ebb981f578345eba46aa0f6'), ObjectId('5ebb98f9bb40e262a96aa0f6'), ObjectId('5ebb99e728578c91d56aa0f6'), ObjectId('5ebb9b3aa999402ad36aa0f6'), ObjectId('5ebb9c44c1b42cbbc56aa0f6'), ObjectId('5ebb9cbe6ea41c22346aa0f6'), ObjectId('5ebb9e08b5462147036aa0f6'), ObjectId('5ebb9fbe0739dc31176aa0f6'), ObjectId('5ebba11575f19b90476aa0f6'), ObjectId('5ebba293eb3408469f6aa0f6'), ObjectId('5ebba3e1b9a190811b6aa0f6'), ObjectId('5ebba5f7bc38d10fb76aa0f6'), ObjectId('5ebba6d482bda639156aa0f6'), ObjectId('5ebba7a353afb167066aa0f6'), ObjectId('5ebba856281233e3ec6aa0f6'), ObjectId('5ebba91e94db78e4eb6aa0f6'), ObjectId('5ebba9f416df4600a36aa0f6'), ObjectId('5ebbaab4446067c7656aa0f6'), ObjectId('5ebbab6dad852c37026aa0f6'), ObjectId('5ebbacc55e984c90896aa0f6'), ObjectId('5ebbae609ac80be49a6aa0f6'), ObjectId('5ebbaf5923e8de12726aa0f6'), ObjectId('5ebbb03674dee939a46aa0f6'), ObjectId('5ebbb0a28efd4d38d46aa0f6'), ObjectId('5ebbb14e4e694aa47d6aa0f6'), ObjectId('5ebbb1b85dfbaa4d786aa0f6'), ObjectId('5ebbb2c0cb9975fbf36aa0f6'), ObjectId('5ebbb46aa481553d446aa0f6'), ObjectId('5ebbb580d1393f6ff36aa0f6'), ObjectId('5ebbb6751b21c7ed6a6aa0f6'), ObjectId('5ebbb762f199d6ef886aa0f6'), ObjectId('5ebbb7d677a48dcddd6aa0f6'), ObjectId('5ebbb8d35d3880d4b16aa0f6'), ObjectId('5ebbb9935098991b3e6aa0f6'), ObjectId('5ebbba53ac65270bd06aa0f6'), ObjectId('5ebbbaec434b6f155b6aa0f6'), ObjectId('5ebbbbf72f5413756d6aa0f6'), ObjectId('5ebbbc8d7199b845bf6aa0f6'), ObjectId('5ebbbd1f442930d4936aa0f6'), ObjectId('5ebbbde28e5144df826aa0f6'), ObjectId('5ebbbf1cd3a944233a6aa0f6'), ObjectId('5ebbbff61549076a1b6aa0f6'), ObjectId('5ebbc0696cbe306f756aa0f6'), ObjectId('5ebbc14c1e9f60b2826aa0f6'), ObjectId('5ebbc219ae5d8bcd816aa0f6'), ObjectId('5ebbc3f44931fd15ad6aa0f6'), ObjectId('5ebbc4dd2563b3460d6aa0f6'), ObjectId('5ebbca20827f1af2c397178d'), ObjectId('5ebbcad24bdc100b9297178d'), ObjectId('5ebbcbd8e6ec72146a97178d'), ObjectId('5ebbcc99b03ab9032f97178d'), ObjectId('5ebbcd1b4e715b717b97178d'), ObjectId('5ebbce48438ab3f89797178d'), ObjectId('5ebbcf0ba231769fda97178d'), ObjectId('5ebbd01600a1c5e0fc97178d'), ObjectId('5ebbd0afae75f0608b97178d'), ObjectId('5ebbd13d126ffba29897178d'), ObjectId('5ebbd2161b5e9d954997178d'), ObjectId('5ebbd27d8816705d3e97178d'), ObjectId('5ebbd3601115d30fca97178d'), ObjectId('5ebbd42b4ee5dcfa8d97178d'), ObjectId('5ebbd5f5f1e510ea0e97178d'), ObjectId('5ebbd6d689d268831997178d'), ObjectId('5ebbd7af5ca946e06b97178d'), ObjectId('5ebbd8a31840d1cde197178d'), ObjectId('5ebbd9b45a74e14cdf97178d'), ObjectId('5ebbda9ee9ce37b87497178d'), ObjectId('5ebbdbdc70e15a08c397178d'), ObjectId('5ebbdd4d7655a83e6297178d'), ObjectId('5ebbde40e7d479de4a97178d'), ObjectId('5ebbdf1e4c04cacbb697178d'), ObjectId('5ebbdfe4e5ea81fcd297178d'), ObjectId('5ebbe0b386f2ef4c7b97178d'), ObjectId('5ebbe18dac66bed3de97178d'), ObjectId('5ebbe2b2b0a795f33f97178d'), ObjectId('5ebbe3b6102784fdea97178d'), ObjectId('5ebbe4af340990d62f97178d'), ObjectId('5ebbe5255d76242aef97178d'), ObjectId('5ebbe638671e802e6397178d'), ObjectId('5ebbe7300dbe31b16997178d'), ObjectId('5ebbe7cc430903f91597178d'), ObjectId('5ebbe87a8a059c7c6297178d'), ObjectId('5ebbeaf57cdedca11397178d'), ObjectId('5ebbeb9a4ce622fc5f97178d'), ObjectId('5ebbed663646af3c7b97178d'), ObjectId('5ebbee6a5f009009c597178d'), ObjectId('5ebbf1c39cc1200a2797178d'), ObjectId('5ebbf299c5a7f124b697178d'), ObjectId('5ebbf3360421d9c77797178d'), ObjectId('5ebbf3ed1166a781cc97178d'), ObjectId('5ebbf5959491ae92e997178d'), ObjectId('5ebbf642304c4f80ab97178d'), ObjectId('5ebbf73c8aae5c54cd97178d'), ObjectId('5ebbf84b53ba3184e697178d'), ObjectId('5ebbfac2f4308c2cc497178d'), ObjectId('5ebbfbdf6c99d1297497178d'), ObjectId('5ebbfd0a6291766e8c97178d'), ObjectId('5ebbfe2692b1ee138897178d'), ObjectId('5ebbfecd381a18083097178d'), ObjectId('5ebbffe954b500b09497178d'), ObjectId('5ebc00c75da3de695b97178d'), ObjectId('5ebc0276088a2cf87797178d'), ObjectId('5ebc034d1034c24aad97178d'), ObjectId('5ebc048e11ccbe0da897178d'), ObjectId('5ebc075694bc2c707997178d'), ObjectId('5ebc0875b11342f88097178d'), ObjectId('5ebc09a74efa0725f497178d'), ObjectId('5ebc0acbe84a4f5ebc97178d'), ObjectId('5ebc0bd6237a0574d297178d'), ObjectId('5ebc0d3c73e648b83597178d'), ObjectId('5ebc0dbe0dabb3379b97178d'), ObjectId('5ebc0ee1d9892b0c1b97178d'), ObjectId('5ebc13d75c86d945b197178d'), ObjectId('5ebc150e82d13b7b3697178d'), ObjectId('5ebc16489fcd033f6297178d'), ObjectId('5ebc17c2b4123e4f7197178d'), ObjectId('5ebc189513f4a8262197178d'), ObjectId('5ebc19aafc23d292fa97178d'), ObjectId('5ebc1adac6d203564e97178d'), ObjectId('5ebc1c5f3a0803f22f97178d'), ObjectId('5ebc1e001783515cd097178d'), ObjectId('5ebc1efebff60eafcc97178d'), ObjectId('5ebc1fa10215e6d08097178d'), ObjectId('5ebc2273674baef33497178d'), ObjectId('5ebc239dcf12c8ef1397178d'), ObjectId('5ebc24c73d53d2699c97178d'), ObjectId('5ebc2606a78eecfe5397178d'), ObjectId('5ebc27e9bd0f15a4d697178d'), ObjectId('5ebc28e2414c3fac1397178d'), ObjectId('5ebc2a0004edb50ae697178d'), ObjectId('5ebc2b0bf9360bbe0097178d'), ObjectId('5ebc2bd7c815a5eb3197178d'), ObjectId('5ebc2c7a12c0462f6597178d'), ObjectId('5ebc2e1cba7a46c38597178d'), ObjectId('5ebc2ee30d89056a5397178d'), ObjectId('5ebc3034223430f85897178d'), ObjectId('5ebc3169d17d5cf8b097178d'), ObjectId('5ebc32b53ef4cdcab097178d'), ObjectId('5ebc344e630bf85da197178d'), ObjectId('5ebc35b8f60ec679e997178d'), ObjectId('5ebc3732359c41b6fb97178d'), ObjectId('5ebc37fdd57cee6b8097178d'), ObjectId('5ebc3937d67ddeedc697178d'), ObjectId('5ebc3a2d3d43846c8097178d'), ObjectId('5ebc3b8c8f905cc1e997178d'), ObjectId('5ebc3d0f0f1bbea78f97178d'), ObjectId('5ebc3d972739abfa2597178d'), ObjectId('5ebc3e33f8232116ed97178d'), ObjectId('5ebc3f2f65d503e38b97178d'), ObjectId('5ebc3fe0843419ca2497178d'), ObjectId('5ebc44847ce40c9ba7bb9565'), ObjectId('5ebc452ac7057c1a4cbb9565'), ObjectId('5ebc475c409fdd7855bb9565'), ObjectId('5ebc4c4bff166bccf3bb9565'), ObjectId('5ebc4dc1a821835a79bb9565'), ObjectId('5ebc4edd839d7e0760bb9565'), ObjectId('5ebc5065dc5d111808bb9565'), ObjectId('5ebc51615809efe175bb9565'), ObjectId('5ebc524ab08e89b0dbbb9565'), ObjectId('5ebc53a9503b1f44d4bb9565'), ObjectId('5ebc54e10c8dd65b2ebb9565'), ObjectId('5ebc55d8b8becb694ebb9565'), ObjectId('5ebc56ea2e7d8c6aeebb9565'), ObjectId('5ebc5998cf082e6085bb9565'), ObjectId('5ebc5b1f9c4cc72ad1bb9565'), ObjectId('5ebc5bf2b3cbaa2082bb9565'), ObjectId('5ebc5d4be04b819ebbbb9565'), ObjectId('5ebc5e6ac44c18198cbb9565'), ObjectId('5ebc5f97704055e80fbb9565'), ObjectId('5ebc609f7eac357441bb9565'), ObjectId('5ebc61e72f2c7dada9bb9565'), ObjectId('5ebc6297ec72b05079bb9565'), ObjectId('5ebc63bfd0307282bfbb9565'), ObjectId('5ebc64ebef1ae0f93cbb9565'), ObjectId('5ebc662f30a73754bdbb9565'), ObjectId('5ebc670e0989242104bb9565'), ObjectId('5ebc67e2c23fb5f50fbb9565'), ObjectId('5ebc689e354f01cef5bb9565'), ObjectId('5ebc69f507bbf21102bb9565'), ObjectId('5ebc6b4ce3edb257d2bb9565'), ObjectId('5ebc6d29ef740596e3bb9565'), ObjectId('5ebc6e966b32dc548abb9565'), ObjectId('5ebc6fe10cc45c110abb9565'), ObjectId('5ebc70d663d25e7626bb9565'), ObjectId('5ebc71db7a7539f778bb9565'), ObjectId('5ebc73a5647bebbebebb9565'), ObjectId('5ebc754411d8be18d7bb9565'), ObjectId('5ebc766e133af6bd40bb9565'), ObjectId('5ebc7775f2d5414b72bb9565'), ObjectId('5ebc78525c1c202b83bb9565'), ObjectId('5ebc794dc19a9f9959bb9565'), ObjectId('5ebc7a0de27e58b722bb9565'), ObjectId('5ebc7aff7e8c51fa5cbb9565'), ObjectId('5ebc7c753b4b632571bb9565'), ObjectId('5ebc7dd360f39467b0bb9565'), ObjectId('5ebc7f0c9596b2c3c3bb9565'), ObjectId('5ebc802cdae450fef8bb9565'), ObjectId('5ebc81328a39a23545bb9565'), ObjectId('5ebc82311e0fecd49dbb9565'), ObjectId('5ebc8330d68e5922acbb9565'), ObjectId('5ebc845c0d4da08c6cbb9565'), ObjectId('5ebc856de0d100ac75bb9565'), ObjectId('5ebc8681384fba1159bb9565'), ObjectId('5ebc871ed930e86275bb9565'), ObjectId('5ebc885ca272f357d6bb9565'), ObjectId('5ebc895185be38e47dbb9565'), ObjectId('5ebc8a1782d758f81ebb9565'), ObjectId('5ebc8afd1a8aacb685bb9565'), ObjectId('5ebc8bcf0674f6a5cfbb9565'), ObjectId('5ebc8cb6cd39f22394bb9565'), ObjectId('5ebc8e617c59b90a2fbb9565'), ObjectId('5ebc8fbeea52288a8bbb9565'), ObjectId('5ebc91d972a50ff18ebb9565'), ObjectId('5ebc9256c5958bd302bb9565'), ObjectId('5ebc9362ebb1fc2b07bb9565'), ObjectId('5ebc94b647c2e77ca3bb9565'), ObjectId('5ebc95ea7cbc6a1403bb9565'), ObjectId('5ebc971bba16733a02bb9565'), ObjectId('5ebc984530037449c9bb9565'), ObjectId('5ebc9949a160c22deebb9565'), ObjectId('5ebc9a1c3e0aa5990cbb9565'), ObjectId('5ebc9b8128578a3d31bb9565'), ObjectId('5ebc9c74ab2ef6351bbb9565'), ObjectId('5ebc9d363989161b11bb9565'), ObjectId('5ebc9e03cafeebb26bbb9565'), ObjectId('5ebc9f2b619a56275fbb9565'), ObjectId('5ebca00d314c2dc72ebb9565'), ObjectId('5ebca14eba194fdeb1bb9565'), ObjectId('5ebca2376f78cb5a2bbb9565'), ObjectId('5ebca33057b4b2b734bb9565'), ObjectId('5ebca4cc099c653561bb9565'), ObjectId('5ebca5591baac0e83dbb9565'), ObjectId('5ebca66e74328e8022bb9565'), ObjectId('5ebca7cbe6c4023d26bb9565'), ObjectId('5ebca8cf6f840edcb3bb9565'), ObjectId('5ebcaaa8d0354e60babb9565'), ObjectId('5ebcabd24a644677ffbb9565'), ObjectId('5ebcacc3f7e2f8ee8bbb9565'), ObjectId('5ebcae4585e6061bd0bb9565'), ObjectId('5ebcaf4e9622183001bb9565'), ObjectId('5ebcb05aa44de503fabb9565'), ObjectId('5ebcb132a2093d13d0bb9565'), ObjectId('5ebcb2cd922e75c876bb9565'), ObjectId('5ebcb3cadc1a1388c7bb9565'), ObjectId('5ebcb523969284d23dbb9565'), ObjectId('5ebcb6ef119620ed97bb9565'), ObjectId('5ebcb7d69224a1b74bbb9565'), ObjectId('5ebcb885a6da1f930cbb9565'), ObjectId('5ebcb9a118d81d1cbbbb9565'), ObjectId('5ebcbb0d3f90784303bb9565'), ObjectId('5ebcbb957c67c9cef5bb9565'), ObjectId('5ebcbc85352785ec12bb9565'), ObjectId('5ebcbe138fff794862bb9565'), ObjectId('5ebcbf2b2af1f062e3bb9565'), ObjectId('5ebcc0475af8654d72bb9565'), ObjectId('5ebcc26b484ede5904bb9565'), ObjectId('5ebcc3221604f7f7d7bb9565'), ObjectId('5ebcc45397acd3f8a2bb9565'), ObjectId('5ebcc58db3643873f0bb9565'), ObjectId('5ebcc68da3ba29bee5bb9565'), ObjectId('5ebcc7e3353f259c9abb9565'), ObjectId('5ebcc8f0f96bd933a5bb9565'), ObjectId('5ebcc9fddc68e0bf3bbb9565'), ObjectId('5ebccb40f70ef18b49bb9565'), ObjectId('5ebccc66d9df03169dbb9565'), ObjectId('5ebccdc25d73fe7a88bb9565'), ObjectId('5ebccec14cf1a77a62bb9565'), ObjectId('5ebccf799a297ffebebb9565'), ObjectId('5ebcd0764dd2fbfc26bb9565'), ObjectId('5ebcd153160254fc9ebb9565'), ObjectId('5ebcd27767809786bbbb9565'), ObjectId('5ebcd34a6098473cd4bb9565'), ObjectId('5ebcd49deab020e028bb9565'), ObjectId('5ebcd58d767c6a2fe0bb9565'), ObjectId('5ebcd64ef2f9eecf34bb9565'), ObjectId('5ebcd7203769d8b4c0bb9565'), ObjectId('5ebcd8315d3c46bf0fbb9565'), ObjectId('5ebcd8f9be1e13b63dbb9565'), ObjectId('5ebcda7eba71eaca87bb9565'), ObjectId('5ebcdb34435b150550bb9565'), ObjectId('5ebcdbeae8aab054c3bb9565'), ObjectId('5ebcdd7c16e302af0ebb9565'), ObjectId('5ebcde7a6ebb152546bb9565'), ObjectId('5ebcdf95359df0d164bb9565'), ObjectId('5ebce0c51dd1903478bb9565'), ObjectId('5ebce1aeadd4c0a3e0bb9565'), ObjectId('5ebce3325e4212bb48bb9565'), ObjectId('5ebce442ac3373eba6bb9565'), ObjectId('5ebce6892067022a62bb9565'), ObjectId('5ebce7d93cbe748a83bb9565'), ObjectId('5ebce92bc83f027dd9bb9565'), ObjectId('5ebcea5cff05bac2f1bb9565'), ObjectId('5ebceb0d15a9e9eaeebb9565'), ObjectId('5ebcec1647057d3c45bb9565'), ObjectId('5ebcec9c106f4c3a1abb9565'), ObjectId('5ebced87f299814126bb9565'), ObjectId('5ebcee74bf85ed3c28bb9565'), ObjectId('5ebcef579014fddb7dbb9565'), ObjectId('5ebceffc85e7506011bb9565'), ObjectId('5ebcf08b9522522d60bb9565'), ObjectId('5ebcf108f63f96f109bb9565'), ObjectId('5ebcf1fbc6b289d0edbb9565'), ObjectId('5ebcf2cfd0b71e96f4bb9565'), ObjectId('5ebcf4890f1e5ba0b0bb9565'), ObjectId('5ebcf577f441e92192bb9565'), ObjectId('5ebcf6440dff2a61acbb9565'), ObjectId('5ebcf6bd7316da96c6bb9565'), ObjectId('5ebcf76e2566f6bb05bb9565'), ObjectId('5ebcf7ec5640f2f328bb9565'), ObjectId('5ebcf89836daf4509fbb9565'), ObjectId('5ebcf93215c77e8b87bb9565'), ObjectId('5ebcf9dd1301cad34fbb9565'), ObjectId('5ebcfb8cbc87dec79cbb9565'), ObjectId('5ebcfc44eb11b2e47dbb9565'), ObjectId('5ebcfd2cd7ea48b3e7bb9565'), ObjectId('5ebcfdbf9f11780689bb9565'), ObjectId('5ebcfe8e2952286fefbb9565'), ObjectId('5ebcff1f2a93fc931ebb9565'), ObjectId('5ebd0001b3509c960abb9565'), ObjectId('5ebd00dab8cc7ea5dabb9565'), ObjectId('5ebd015476f2c8cf87bb9565'), ObjectId('5ebd020f569f790404bb9565'), ObjectId('5ebd02c50f15cbd93ebb9565'), ObjectId('5ebd03e6f2c2c8038ebb9565'), ObjectId('5ebd053641df3cea32bb9565'), ObjectId('5ebd06cf8892fa02bdbb9565'), ObjectId('5ebd07eba463f4d183bb9565'), ObjectId('5ebd09a4d64c61ea04bb9565'), ObjectId('5ebd0bae98ffab8e7bbb9565'), ObjectId('5ebd0ce9c8aa38951ebb9565'), ObjectId('5ebd0e220b718b8620bb9565'), ObjectId('5ebd0ee0880136b7afbb9565'), ObjectId('5ebd10661c8d8ad3c3bb9565'), ObjectId('5ebd12255f594b4b6bbb9565'), ObjectId('5ebd1363f25e6f6546bb9565'), ObjectId('5ebd147c1119c14953bb9565'), ObjectId('5ebd1608d47c1e2418bb9565'), ObjectId('5ebd17086956b802f8bb9565'), ObjectId('5ebd17e68b7f616830bb9565'), ObjectId('5ebd18eaa5627dc978bb9565'), ObjectId('5ebd1a2393c45cb40ebb9565'), ObjectId('5ebd1bd524285f988ebb9565'), ObjectId('5ebd1d70fe9a4e44f4bb9565'), ObjectId('5ebd1f24a731947d23bb9565'), ObjectId('5ebd1fb4f902dca8cabb9565'), ObjectId('5ebd2277174a04dafebb9565'), ObjectId('5ebd2355666a191d89bb9565'), ObjectId('5ebd23fc201cd3e6bfbb9565'), ObjectId('5ebd24a06e160e43c7bb9565'), ObjectId('5ebd255d9fd249f446bb9565'), ObjectId('5ebd25dab8ddbb12a7bb9565'), ObjectId('5ebd26b2031e847836bb9565'), ObjectId('5ebd275825abac33cbbb9565'), ObjectId('5ebd27e02408aec98abb9565'), ObjectId('5ebd2901bb17922d7ebb9565'), ObjectId('5ebd29aa90e09a86f5bb9565'), ObjectId('5ebd2a999e04ea59e8bb9565'), ObjectId('5ebd2bc121c02d589bbb9565'), ObjectId('5ebd2ce2b594bfb1f2bb9565'), ObjectId('5ebd2da465c3917732bb9565'), ObjectId('5ebd2e4d3dedb20ec3bb9565'), ObjectId('5ebd2f1fd143dae4b2bb9565'), ObjectId('5ebd2f90141e8ce48dbb9565'), ObjectId('5ebd303965742b506dbb9565'), ObjectId('5ebd30ffb412a41516bb9565'), ObjectId('5ebd321634c77f5798bb9565'), ObjectId('5ebd32b7fd1b187544bb9565'), ObjectId('5ebd3a22f321cdd207d1b7ab'), ObjectId('5ebd3d8fdda69510b998bd17'), ObjectId('5ebd796a1bfded191c23510e'), ObjectId('5ebd7a3eda443a028023510e'), ObjectId('5ebd7ac8160e002bbf23510e'), ObjectId('5ebd7b3bd1fd26d5cc23510e'), ObjectId('5ebd7c7c3c6bb6723023510e'), ObjectId('5ebd7dad99369e7c8a23510e'), ObjectId('5ebd7efb7c379d2d3223510e'), ObjectId('5ebd80bea3836a0c0a23510e'), ObjectId('5ebd820d22437f5c2e23510e'), ObjectId('5ebd82952597752f6123510e'), ObjectId('5ebd83a67b2f65704b23510e'), ObjectId('5ebd846612cc2d9c4723510e'), ObjectId('5ebd8552b5ed2ef2ca23510e'), ObjectId('5ebd869733f40229cf23510e'), ObjectId('5ebd880505e303dbb623510e'), ObjectId('5ebd891ef3f083120923510e'), ObjectId('5ebd89935397bc7a1223510e'), ObjectId('5ebd89f973222ecec623510e'), ObjectId('5ebd8b2c57805a023423510e'), ObjectId('5ebd8bb7c7fcca593123510e'), ObjectId('5ebd8d2b33490849bf23510e'), ObjectId('5ebd8fbf8661ff060b23510e'), ObjectId('5ebd90482da109482423510e'), ObjectId('5ebd9115db4fc596b623510e'), ObjectId('5ebd91f955bf1e293e23510e'), ObjectId('5ebd933586a108cfb023510e'), ObjectId('5ebd94593ca68ec88723510e'), ObjectId('5ebd95693164a0561223510e'), ObjectId('5ebd967ef5ece6be7e23510e'), ObjectId('5ebd97ec7e075bdf1b23510e'), ObjectId('5ebd99ac214dbaec9623510e'), ObjectId('5ebd9ae62149a04ac623510e'), ObjectId('5ebd9bf1cf2d75f30f23510e'), ObjectId('5ebd9ce9eaadcab91823510e'), ObjectId('5ebd9e6071b196bdfc23510e'), ObjectId('5ebda025c44c9aff7223510e'), ObjectId('5ebda1a4a16b09d54a23510e'), ObjectId('5ebda2ba083600027023510e'), ObjectId('5ebda4d0e699595c9623510e'), ObjectId('5ebda614f739ee878c23510e'), ObjectId('5ebda6f5f677c6517323510e'), ObjectId('5ebda7e7c62ddf274523510e'), ObjectId('5ebda85963ec391d0423510e'), ObjectId('5ebda96cb1d8f4b5d123510e'), ObjectId('5ebdaa5980d75dbb8a23510e'), ObjectId('5ebdab1fa90496c00923510e'), ObjectId('5ebdac1e698107bc9823510e'), ObjectId('5ebdace3e64012f6a923510e'), ObjectId('5ebdad8cecd540c25723510e'), ObjectId('5ebdae9c34c98ecb7623510e'), ObjectId('5ebdaf8b9bc87e4ae123510e'), ObjectId('5ebdb0f46a8d6bcad323510e'), ObjectId('5ebdb1f814ffb1de1623510e'), ObjectId('5ebdb373d8a95e350723510e'), ObjectId('5ebdb47f71a9142a3023510e'), ObjectId('5ebdb569c9068fce6f23510e'), ObjectId('5ebdb99bc81520990b23510e'), ObjectId('5ebdbad429ebb8695723510e'), ObjectId('5ebdbc0b78d6e31acb23510e'), ObjectId('5ebdbd15c8a723347223510e'), ObjectId('5ebdbdd165c9f2bd2f23510e'), ObjectId('5ebdbeb84dfbdf1a7a23510e'), ObjectId('5ebdbf95ce002b817323510e'), ObjectId('5ebdc0fd5a8c685cac23510e'), ObjectId('5ebdc20a048a5606a723510e'), ObjectId('5ebdc34558c210e6ba23510e'), ObjectId('5ebdc42199677f61df23510e'), ObjectId('5ebdc5017211f4b06623510e'), ObjectId('5ebdc6236c117f8e5023510e'), ObjectId('5ebdc74811460dba3723510e'), ObjectId('5ebdc80f0c314bab7323510e'), ObjectId('5ebdc958c8f07adf0623510e'), ObjectId('5ebdcaad9cf085d4ca23510e'), ObjectId('5ebdcaffdc37ce0eb523510e'), ObjectId('5ebdcc63b52e86ccbb23510e'), ObjectId('5ebdcd27f635aea54523510e'), ObjectId('5ebdcea895901e01ea23510e'), ObjectId('5ebdd02873d18252e223510e'), ObjectId('5ebdd18870ec30b67223510e'), ObjectId('5ebdd26e1c338de66323510e'), ObjectId('5ebdd38c88cd8b3fd723510e'), ObjectId('5ebdd43fe809becffc23510e'), ObjectId('5ebdd55626d98da9da23510e'), ObjectId('5ebdd670c814f7619d23510e'), ObjectId('5ebdd74720861643ea23510e'), ObjectId('5ebdd85bbca17ead8e23510e'), ObjectId('5ebdd9a44e1876956023510e'), ObjectId('5ebddac50666fc8fdf23510e'), ObjectId('5ebddc8722342f2d5723510e'), ObjectId('5ebdddc7b8981578ff23510e'), ObjectId('5ebddf0e9c07e3009a23510e'), ObjectId('5ebde014b77485010323510e'), ObjectId('5ebde118ab63535ed623510e'), ObjectId('5ebde222c41ab21a8f23510e'), ObjectId('5ebde2be526174d1d423510e'), ObjectId('5ebde6341572b9f0a223510e'), ObjectId('5ebde728e9d9461b7f23510e'), ObjectId('5ebde81b6a78f4b2ac23510e'), ObjectId('5ebdea079e80f3015523510e'), ObjectId('5ebdeb3a8867ec6b5023510e'), ObjectId('5ebdec8b3f2db62a9a23510e'), ObjectId('5ebded47254503787123510e'), ObjectId('5ebdedff4bac6e548023510e'), ObjectId('5ebdeee5ca347a3a4023510e'), ObjectId('5ebdefedb6640fc26023510e'), ObjectId('5ebdf12c980c486e1923510e'), ObjectId('5ebdf1ee1c933824fa23510e'), ObjectId('5ebdf2f345de40632a23510e'), ObjectId('5ebdf3fe8014807b3023510e'), ObjectId('5ebdf62db6b0896a2823510e'), ObjectId('5ebdf723711cbc68f823510e'), ObjectId('5ebdf7e7a11831c6d923510e'), ObjectId('5ebdf969e41f17a4b223510e'), ObjectId('5ebdfa74cb8e7b4c4e23510e'), ObjectId('5ebdfaf5f7d4a26ae323510e'), ObjectId('5ebdfbd6a8c986176023510e'), ObjectId('5ebdfc9f10ddc6734e23510e'), ObjectId('5ebdfd3dbec363e31b23510e'), ObjectId('5ebdfeddbbcc93a8d223510e'), ObjectId('5ebdfff4de647a467f23510e'), ObjectId('5ebe00ca119d06ca3223510e'), ObjectId('5ebe01d5a1d5b4617023510e'), ObjectId('5ebe02c44897de14a923510e'), ObjectId('5ebe03c6baab1b599123510e'), ObjectId('5ebe04feb352a6756223510e'), ObjectId('5ebe06455b6ac2ba0323510e'), ObjectId('5ebe07d6812edc601b23510e'), ObjectId('5ebe08c8918a95661523510e'), ObjectId('5ebe0a0d110384add423510e'), ObjectId('5ebe0bb08df9dfa24723510e'), ObjectId('5ebe0c575ca295797423510e'), ObjectId('5ebe0cd9a0d22e0d5723510e'), ObjectId('5ebe0da5663c0d400d23510e'), ObjectId('5ebe0e4e173a912a8923510e'), ObjectId('5ebe0f126e2565a3c323510e'), ObjectId('5ebe102a6773d0b2e023510e'), ObjectId('5ebe114e7586bde45e23510e'), ObjectId('5ebe1252b1affb0b0223510e'), ObjectId('5ebe12faf9da04afc323510e'), ObjectId('5ebe13b5de4d6a45b423510e'), ObjectId('5ebe14b3c9699ceeaa23510e'), ObjectId('5ebe17207e47e5354a23510e'), ObjectId('5ebe17b768839a80c223510e'), ObjectId('5ebe184e197a75e64f23510e'), ObjectId('5ebe18e7baba7a348c23510e'), ObjectId('5ebe1a2f6a016e79f223510e'), ObjectId('5ebe1adfc02a37a04d23510e'), ObjectId('5ebe1b997ef9ba265c23510e'), ObjectId('5ebe1c36bc048b033d23510e'), ObjectId('5ebe1ccc9f4b32070b23510e'), ObjectId('5ebe1d5f229dc61a2c23510e'), ObjectId('5ebe1deb74e3e08f2f23510e'), ObjectId('5ebe1ec6ef211ca78a23510e'), ObjectId('5ebe1f7622f89fa85c23510e'), ObjectId('5ebe2082cb26ce3d9623510e'), ObjectId('5ebe2160729709f17023510e'), ObjectId('5ebe21f3ef0b7214b323510e'), ObjectId('5ebe22e7c0ed77f6d523510e'), ObjectId('5ebe23b6365f130bb623510e'), ObjectId('5ebe246b13657b035323510e'), ObjectId('5ebe255e4c5abad2c023510e'), ObjectId('5ebe25c747a6ac779b23510e'), ObjectId('5ebe2684bd1bf8333523510e'), ObjectId('5ebe27ce38d7be0c9023510e'), ObjectId('5ebe28e9361dd7cb3c23510e'), ObjectId('5ebe29a35b269bf26b23510e'), ObjectId('5ebe2a9000a6c0640423510e'), ObjectId('5ebe2b82008f27cd2923510e'), ObjectId('5ebe2c580e4ce0536723510e'), ObjectId('5ebe2d811f6f235f9423510e'), ObjectId('5ebe2f9594b8ddf1bf23510e'), ObjectId('5ebe3110c8eb4ce0d623510e'), ObjectId('5ebe32490e54e54ac323510e'), ObjectId('5ebe33cfe6adf5656423510e'), ObjectId('5ebe3587f54656eb7923510e'), ObjectId('5ebe371fee35df244c23510e'), ObjectId('5ebe380ed58d76612d23510e'), ObjectId('5ebe38fc932283cfde23510e'), ObjectId('5ebe39c4604716934c23510e'), ObjectId('5ebe3a796fce07fc0323510e'), ObjectId('5ebe3b841215466f7a23510e'), ObjectId('5ebe3c08a4fcb859d923510e'), ObjectId('5ebe3d2a685d3bbcd923510e'), ObjectId('5ebe3e3bdcc73fc7c123510e'), ObjectId('5ebe3ef42128e09edb23510e'), ObjectId('5ebe4189c511affa9a23510e'), ObjectId('5ebe4326ecd569c2ec23510e'), ObjectId('5ebe444e343cd5178023510e'), ObjectId('5ebe44edc3e237374723510e'), ObjectId('5ebe45b8c176a0ce0423510e'), ObjectId('5ebe471453b9ecf8ef23510e'), ObjectId('5ebe47fdc240012fb223510e'), ObjectId('5ebe489a345c2b4da723510e'), ObjectId('5ebe491ab0e14f5de823510e'), ObjectId('5ebe4a32c97f50467923510e'), ObjectId('5ebe4b4cd5f021d40a23510e'), ObjectId('5ebe4c1bd474c4e5b323510e'), ObjectId('5ebe4ca3cfd906efa323510e'), ObjectId('5ebe4d4b15a39a0c2e23510e'), ObjectId('5ebe4dd709926c96a223510e'), ObjectId('5ebe4e433674355bc023510e'), ObjectId('5ebe4eb5ca87309d1c23510e'), ObjectId('5ebe4fa68a8a10b98623510e'), ObjectId('5ebe50421cf82abcf923510e'), ObjectId('5ebe50bdc35eceb02023510e'), ObjectId('5ebe52e548f0ecc70f23510e'), ObjectId('5ebe5379cff7492f5623510e'), ObjectId('5ebe546483a93c8ddb23510e'), ObjectId('5ebe56fa3440fa97d523510e'), ObjectId('5ebe57ad48910a9ff723510e'), ObjectId('5ebe58ca83dd2353f023510e'), ObjectId('5ebe5a49e5dcabd06c23510e'), ObjectId('5ebe5ba075c5904fbc23510e'), ObjectId('5ebe5cbdc63f4a286123510e'), ObjectId('5ebe5d5a48b0eab19723510e'), ObjectId('5ebe5dfbb66c40d9a423510e'), ObjectId('5ebe5ebede558cbbb223510e'), ObjectId('5ebe5f3f177d38f8c523510e'), ObjectId('5ebe6024c21f8d600f23510e'), ObjectId('5ebe616a764275331523510e'), ObjectId('5ebe622b85dee1476423510e'), ObjectId('5ebe635d7a6f29121023510e'), ObjectId('5ebe647f5d46a1366b23510e'), ObjectId('5ebe65da6a9d6de27923510e'), ObjectId('5ebe678912502325db23510e'), ObjectId('5ebe69389a62211d6d23510e'), ObjectId('5ebe6adc56caef814023510e'), ObjectId('5ebe6cfe66ab22f9a923510e'), ObjectId('5ebe6e53860742577823510e'), ObjectId('5ebe6f0d98eff0aa6323510e'), ObjectId('5ebe70d1a7c94ecd7b23510e'), ObjectId('5ebe71d36c3fdeb61d23510e'), ObjectId('5ebe730e5d65d8d2ae23510e'), ObjectId('5ebe73928e1194814323510e'), ObjectId('5ec20a8df687ff620dd08ffd'), ObjectId('5ec20b2e7ee23711b9d08ffd'), ObjectId('5ec20bc95eb68a915cd08ffd'), ObjectId('5ec20cc7732097ba8ad08ffd'), ObjectId('5ec20dfbc8d363fe73d08ffd'), ObjectId('5ec20ede27fadfdd47d08ffd'), ObjectId('5ec20fc991aaa72304d08ffd'), ObjectId('5ec2104f497f895a9cd08ffd'), ObjectId('5ec211049bab3d37d2d08ffd'), ObjectId('5ec211e48505fe901dd08ffd'), ObjectId('5ec2136d9ac1ff38b0d08ffd'), ObjectId('5ec214765b9b6920ecd08ffd'), ObjectId('5ec215543a859fdf88d08ffd'), ObjectId('5ec21619438f8a1e8bd08ffd'), ObjectId('5ec216f0ca568a4941d08ffd'), ObjectId('5ec21799ae9dc7d64ed08ffd'), ObjectId('5ec21818ac63a29512d08ffd'), ObjectId('5ec21919b2f7815b96d08ffd'), ObjectId('5ec21a2ae157ec6308d08ffd'), ObjectId('5ec21aa965ad51eb4dd08ffd'), ObjectId('5ec21c219357b0c1eed08ffd'), ObjectId('5ec21d0c2fcab31316d08ffd'), ObjectId('5ec21dc7358961c823d08ffd'), ObjectId('5ec21e82438ec56770d08ffd'), ObjectId('5ec21f6a2befc723f3d08ffd'), ObjectId('5ec2203a335d298239d08ffd'), ObjectId('5ec220f8cf464d1769d08ffd'), ObjectId('5ec221a17d0d245a3cd08ffd'), ObjectId('5ec2224098e5201baed08ffd'), ObjectId('5ec2241725ade07b26d08ffd'), ObjectId('5ec22510147a0fc9b7d08ffd'), ObjectId('5ec225cdd083609887d08ffd'), ObjectId('5ec2269cac51bcdc4dd08ffd'), ObjectId('5ec22783a3b00a6f39d08ffd'), ObjectId('5ec2282e7de77a69b7d08ffd'), ObjectId('5ec229880457130f0ad08ffd'), ObjectId('5ec22a286aa7b2f87fd08ffd'), ObjectId('5ec22ba1294f6f446bd08ffd'), ObjectId('5ec22c3b7002e2b8a1d08ffd'), ObjectId('5ec22d02b7c830d85cd08ffd'), ObjectId('5ec22dbf4aca739bacd08ffd'), ObjectId('5ec22e41b6e6d4624bd08ffd'), ObjectId('5ec22efb08af4c47fdd08ffd'), ObjectId('5ec22fcb44f7b4dfb1d08ffd'), ObjectId('5ec230518227f7bceed08ffd'), ObjectId('5ec23104b2b6836637d08ffd'), ObjectId('5ec231c0bfac4de028d08ffd'), ObjectId('5ec232715b6a072779d08ffd'), ObjectId('5ec23348f5f268a3c0d08ffd'), ObjectId('5ec23455d964f932bdd08ffd'), ObjectId('5ec23538b951a56b4fd08ffd'), ObjectId('5ec235eab321c49b2bd08ffd'), ObjectId('5ec23710599a08c5fdd08ffd'), ObjectId('5ec239ff2238a1f9d2d08ffd'), ObjectId('5ec23ad2a2c9338e0dd08ffd'), ObjectId('5ec23b4c4a76c8c16ad08ffd'), ObjectId('5ec23c07016ceead4ad08ffd'), ObjectId('5ec23d01e7875d6ec6d08ffd'), ObjectId('5ec23df2bf7991c467d08ffd'), ObjectId('5ec23eb410081f5532d08ffd'), ObjectId('5ec23f90f441b7fd1fd08ffd'), ObjectId('5ec24063f679b60aafd08ffd'), ObjectId('5ec24155a66fea5c51d08ffd'), ObjectId('5ec2422c64e43b2f41d08ffd'), ObjectId('5ec242a19d1014af3bd08ffd'), ObjectId('5ec243424e63cb702fd08ffd'), ObjectId('5ec243ee34635d5f76d08ffd'), ObjectId('5ec244619729800771d08ffd'), ObjectId('5ec244fdfe651af9f0d08ffd'), ObjectId('5ec2459d77f945cad9d08ffd'), ObjectId('5ec24617506595602ad08ffd'), ObjectId('5ec246a8e9be5ce540d08ffd'), ObjectId('5ec24747d2654d3f9cd08ffd'), ObjectId('5ec248ac8c5bfb592fd08ffd'), ObjectId('5ec249bd1a6e53564bd08ffd'), ObjectId('5ec24a63548ffb04f5d08ffd'), ObjectId('5ec24b23af92ca5bcdd08ffd'), ObjectId('5ec24ce901e6de5db5d08ffd'), ObjectId('5ec24df67f29b5c53fd08ffd'), ObjectId('5ec24eb75c15c61225d08ffd'), ObjectId('5ec24f50aaf3998a63d08ffd'), ObjectId('5ec25055fb6c66bfe7d08ffd'), ObjectId('5ec25154e08a6f3b5bd08ffd'), ObjectId('5ec251d99c2b8f1c33d08ffd'), ObjectId('5ec2529091262b4135d08ffd'), ObjectId('5ec253a572e6a5b8dbd08ffd'), ObjectId('5ec2547eb817507ceed08ffd'), ObjectId('5ec2555f398fbddf6bd08ffd'), ObjectId('5ec25603ebe398f839d08ffd'), ObjectId('5ec25681f6686e65d6d08ffd'), ObjectId('5ec25723016ffa26a0d08ffd'), ObjectId('5ec2581cce74147a42d08ffd'), ObjectId('5ec258da1b87ceba8cd08ffd'), ObjectId('5ec2597f9f5d4ca8f6d08ffd'), ObjectId('5ec25a45f9c2319636d08ffd'), ObjectId('5ec25af1fe9551eae5d08ffd'), ObjectId('5ec25b8abc2df24082d08ffd'), ObjectId('5ec25c232cdcdffa69d08ffd'), ObjectId('5ec25d3620ca9d30b4d08ffd'), ObjectId('5ec25dc408daa00e01d08ffd'), ObjectId('5ec25ea2c46c77f8f3d08ffd'), ObjectId('5ec25f2057c1fb9268d08ffd'), ObjectId('5ec25fd2a46d610ba0d08ffd'), ObjectId('5ec2609daf69566ebfd08ffd'), ObjectId('5ec2618f08d578e86bd08ffd'), ObjectId('5ec2635d0c0df3decfd08ffd'), ObjectId('5ec2643f87dc5179e5d08ffd'), ObjectId('5ec264e5fde80534ead08ffd'), ObjectId('5ec265f19d421d6f34d08ffd'), ObjectId('5ec26671f3e39e07b9d08ffd'), ObjectId('5ec266f42405fcbc2fd08ffd'), ObjectId('5ec267a9614a677f4ad08ffd'), ObjectId('5ec26897b46ac02756d08ffd'), ObjectId('5ec26959705db73b99d08ffd'), ObjectId('5ec269e72bad462454d08ffd'), ObjectId('5ec26aae9c94c6b42dd08ffd'), ObjectId('5ec26ba58f056ca605d08ffd'), ObjectId('5ec26d0a7462e3b2b4d08ffd'), ObjectId('5ec26db22874d3e7a1d08ffd'), ObjectId('5ec26e366194d5671ad08ffd'), ObjectId('5ec26eccf4a1a69faad08ffd'), ObjectId('5ec26f2d384ef25892d08ffd'), ObjectId('5ec26f960c28425fc6d08ffd'), ObjectId('5ec270991df2b6dcb3d08ffd'), ObjectId('5ec2714b3ffee3bc9dd08ffd'), ObjectId('5ec271eb10b62fd1c2d08ffd'), ObjectId('5ec27288bd74feea65d08ffd'), ObjectId('5ec2734a8356c97f44d08ffd'), ObjectId('5ec274551c6cfd72bad08ffd'), ObjectId('5ec2750d493f9d64e3d08ffd'), ObjectId('5ec275ba97992f1134d08ffd'), ObjectId('5ec27641b4a189d3fad08ffd'), ObjectId('5ec27727fd3d080103d08ffd'), ObjectId('5ec277d5ca4f08b78dd08ffd'), ObjectId('5ec278aa7c9f8148cbd08ffd'), ObjectId('5ec27946ed9442bed0d08ffd'), ObjectId('5ec27a0560b88319b4d08ffd'), ObjectId('5ec27ace4475d6fc0cd08ffd'), ObjectId('5ec27be89d8a019a4dd08ffd'), ObjectId('5ec27c972320b2efd9d08ffd'), ObjectId('5ec27d29c1215c372ad08ffd'), ObjectId('5ec27daaca79a51e4ed08ffd'), ObjectId('5ec27e46d5c6b3d772d08ffd'), ObjectId('5ec27ef4b8aca303e8d08ffd'), ObjectId('5ec2800bb7d0988a19d08ffd'), ObjectId('5ec2809d68f85aca90d08ffd'), ObjectId('5ec2811a0358b118e9d08ffd'), ObjectId('5ec282a717f1a373ded08ffd'), ObjectId('5ec2834afada92cceed08ffd'), ObjectId('5ec285634cafcdb16dd08ffd'), ObjectId('5ec2861fe690a8c605d08ffd'), ObjectId('5ec2870297e71b2224d08ffd'), ObjectId('5ec2882e9b412efe2ed08ffd'), ObjectId('5ec289225b8276076bd08ffd'), ObjectId('5ec28a560042707268d08ffd'), ObjectId('5ec28b4c1a3f238debd08ffd'), ObjectId('5ec28c3711f50cb049d08ffd'), ObjectId('5ec28d33a1eaf8b38dd08ffd'), ObjectId('5ec28e72c900d3c5aad08ffd'), ObjectId('5ec28f7ea98b43e760d08ffd'), ObjectId('5ec2909b1642056f60d08ffd'), ObjectId('5ec29188a970126b6cd08ffd'), ObjectId('5ec29205199b47a279d08ffd'), ObjectId('5ec2931bc0ad9248e6d08ffd'), ObjectId('5ec2943099671b3926d08ffd'), ObjectId('5ec2957cf9ac784f00d08ffd'), ObjectId('5ec296461cd121f455d08ffd'), ObjectId('5ec297b81ea52b7eead08ffd'), ObjectId('5ec2987f03d6dfc76fd08ffd'), ObjectId('5ec298f4f5f0dd0ccdd08ffd'), ObjectId('5ec29f29d804f0761cd08ffd'), ObjectId('5ec2a06ee9d5ed6f19d08ffd'), ObjectId('5ec2a1e052c0d2770ed08ffd'), ObjectId('5ec2a31794d6625b4ed08ffd'), ObjectId('5ec2a471f8ab29096dd08ffd'), ObjectId('5ec2a580ab0402974bd08ffd'), ObjectId('5ec2a668d6612a93f5d08ffd'), ObjectId('5ec2a760509168bd48d08ffd'), ObjectId('5ec2a83dfd6180aba2d08ffd'), ObjectId('5ec2a952971a583df2d08ffd'), ObjectId('5ec2aa04af3b98009ad08ffd'), ObjectId('5ec2aadc412396f0cdd08ffd'), ObjectId('5ec2abe020315d5804d08ffd'), ObjectId('5ec2ad0b0e14d7a6d8d08ffd'), ObjectId('5ec2ae6e427f88452bd08ffd'), ObjectId('5ec2aef51e4f004dadd08ffd'), ObjectId('5ec2afca06665058c6d08ffd'), ObjectId('5ec2b0c945552336b5d08ffd'), ObjectId('5ec2b1ca31b9046978d08ffd'), ObjectId('5ec2b2b00e76e69558d08ffd'), ObjectId('5ec2b43685a2f92633d08ffd'), ObjectId('5ec2b5406c7dbb552ed08ffd'), ObjectId('5ec2b5f9df2124ca28d08ffd'), ObjectId('5ec2b76a09548e8058d08ffd'), ObjectId('5ec2b98bd80d085baed08ffd'), ObjectId('5ec2ba293cc97cfe03d08ffd'), ObjectId('5ec2bafb5942aca9f2d08ffd'), ObjectId('5ec2bc0bcbfab288a9d08ffd'), ObjectId('5ec2bcc322b5e302ead08ffd'), ObjectId('5ec2bd51c1fad7d413d08ffd'), ObjectId('5ec2bddd76eb2e5d07d08ffd'), ObjectId('5ec2beba23fd6fb2b8d08ffd'), ObjectId('5ec2bfbf01a412bb1fd08ffd'), ObjectId('5ec2c061dd4178beb5d08ffd'), ObjectId('5ec2c1282bf6d05dcfd08ffd'), ObjectId('5ec2c1bbfb16c38036d08ffd'), ObjectId('5ec2c306f214f4b61bd08ffd'), ObjectId('5ec2c3efd8d520e160d08ffd'), ObjectId('5ec2c46847f3a255d0d08ffd'), ObjectId('5ec2c51a045f1a7508d08ffd'), ObjectId('5ec2c5dbd348cd81fbd08ffd'), ObjectId('5ec2c6fab7d1f5624ad08ffd'), ObjectId('5ec2c7a08558b84b71d08ffd'), ObjectId('5ec2c8508bd6bdbdc0d08ffd'), ObjectId('5ec2c8e910bdf18b51d08ffd'), ObjectId('5ec2c9898fa16f4a79d08ffd'), ObjectId('5ec2ca00f18e322609d08ffd'), ObjectId('5ec2caa5f6a74cc792d08ffd'), ObjectId('5ec2cb9f4e9f0dd4a8d08ffd'), ObjectId('5ec2cdedb1f6b40b84d08ffd'), ObjectId('5ec2cefecd9f1f68a6d08ffd'), ObjectId('5ec2cfa75b2f7c2326d08ffd'), ObjectId('5ec2d09084399c9f05d08ffd'), ObjectId('5ec2d12c5caea061cad08ffd'), ObjectId('5ec2d1ed49fd07a0dcd08ffd'), ObjectId('5ec2d2cebb80b7166bd08ffd'), ObjectId('5ec2d39acc72f4d0a9d08ffd'), ObjectId('5ec2d48fcf5de39b25d08ffd'), ObjectId('5ec2d5b866a1cc5043d08ffd'), ObjectId('5ec2d70878eb72dd7cd08ffd'), ObjectId('5ec2d854ff096f7e22d08ffd'), ObjectId('5ec2d98e3b684229d1d08ffd'), ObjectId('5ec2dab10e1437ee20d08ffd'), ObjectId('5ec2dbc936d5fcca0dd08ffd'), ObjectId('5ec2dcf639fe0a0512d08ffd'), ObjectId('5ec2de1c1830cf434ad08ffd'), ObjectId('5ec2df4284310f309fd08ffd'), ObjectId('5ec2dfd22cd3eef557d08ffd'), ObjectId('5ec2e0550b1ee2fb8fd08ffd'), ObjectId('5ec2e124d477fee603d08ffd'), ObjectId('5ec2e3487c18ec185ad08ffd'), ObjectId('5ec2e4887921fa320ad08ffd'), ObjectId('5ec2e5b016c16643bdd08ffd'), ObjectId('5ec2e6314464e3b4b3d08ffd'), ObjectId('5ec2e7976dfe70ba67d08ffd'), ObjectId('5ec2e8435b8b633017d08ffd'), ObjectId('5ec2e8e601229acd4bd08ffd'), ObjectId('5ec2e9c78cb93d2419d08ffd'), ObjectId('5ec2eb4267d8606175d08ffd'), ObjectId('5ec2ebf8d07233da27d08ffd'), ObjectId('5ec2ed5c4f2c175bd9d08ffd'), ObjectId('5ec2eeb5856d69ccd0d08ffd'), ObjectId('5ec2f0c8536b732760d08ffd'), ObjectId('5ec2f1f8333a35d3fcd08ffd'), ObjectId('5ec2f324cd51f9c853d08ffd'), ObjectId('5ec2f49e235cdc5381d08ffd'), ObjectId('5ec2f60b07f2ba99b9d08ffd'), ObjectId('5ed3846f023b726e6d17d4f0'), ObjectId('5ed38b25d439f58cc06e5825'), ObjectId('5ed38d5420653aee6e3220c8'), ObjectId('5ed38efe1838c05e0c6fb6e4'), ObjectId('5ed3900863e5bffa1d2b4e2f'), ObjectId('5ed391925d33c4975503bb94'), ObjectId('5ed394144eb75866dfdcdc0d'), ObjectId('5ed39521d784bdc428779a0f'), ObjectId('5ed3966ae5903d41b23471ba'), ObjectId('5ed3980c016ddd49b0f4c304'), ObjectId('5ed3996045e3020d63762dce'), ObjectId('5ed39b1195eba19024e714bf'), ObjectId('5ed39d3781f6df0d82e6bfda'), ObjectId('5ed39f30fc1a9fd5e77e332f'), ObjectId('5ed3a07a5dbe3d7cdbc0a11f'), ObjectId('5ed3a21a7deae88594ebebcb'), ObjectId('5ed3a430b15357da758e9aaf'), ObjectId('5ed3a65cc612795088fb19b8'), ObjectId('5ed3a8655fa4a60f979e1f88'), ObjectId('5ed3ac8b4daab633d19b58d8'), ObjectId('5ed3add3461496c2716f7235'), ObjectId('5ed3af522f225fd825bf711a'), ObjectId('5ed3b088624645fcbe0374c5'), ObjectId('5ed3b2383758cc50c8bdd137'), ObjectId('5ed3b766a882d958e63eb52e')]
edu_set = [ObjectId('5eb62e2a134cc6fb9536e93d'), ObjectId('5eb630147afe26eca4ba7bfa'), ObjectId('5eb6311c86662885174692de'), ObjectId('5eb631f1fac479799dedd1f8'), ObjectId('5eb6331597c8f5512179c4f1'), ObjectId('5eb634492802acb8c48e02aa'), ObjectId('5eb63539be65b70e5af0c7a9'), ObjectId('5eb6363894bd0b097f9c2734'), ObjectId('5eb6378b772150870b5c8d27'), ObjectId('5eb639ee2c60aae411d1ae8b'), ObjectId('5eb63aff81de1c4846fd91ab'), ObjectId('5eb63c1e9c69232f6ed6edd8'), ObjectId('5eb63d1b9d2ec0b892c42dd5'), ObjectId('5eb63e1ee805d1cff3d80a25'), ObjectId('5eb63ee743b668cb27ef8137'), ObjectId('5eb640560732058562a400b3'), ObjectId('5eb646ce3b4442b4da91c057'), ObjectId('5eb6479687b6932b9e6de098'), ObjectId('5eb648bf6bc924ef46ab60da'), ObjectId('5eb64a8e96bdd2bbbb3287e5'), ObjectId('5eb64bc810a22fecd4eca987'), ObjectId('5eb64cfc8c94747a21f39855'), ObjectId('5eb64e13158973dfa9982019'), ObjectId('5eb64f4ea0549166c51ca057'), ObjectId('5eb650acab06d680d6990351'), ObjectId('5eb651bc5fa088c453991725'), ObjectId('5eb652de55de509b4a9efaf4'), ObjectId('5eb65433af5bcc3efe32c504'), ObjectId('5eb6556c29c37695bc97bec4'), ObjectId('5eb6567909d0de1b6b708cf8'), ObjectId('5eb657e754ee9cbe1a7388c8'), ObjectId('5eb65942b46918d079adebe9'), ObjectId('5eb65a927cb5b3a1ff4ae362'), ObjectId('5eb65b645417d406270e7e63'), ObjectId('5eb65d83728ad01002b3a5f6'), ObjectId('5eb65f2cde8cab37cd68dffd'), ObjectId('5eb6603b6e69c6f2e1092cf8'), ObjectId('5eb661a6796445df9bfd756d'), ObjectId('5eb6631b245b7e033d0f92ed'), ObjectId('5eb66401b0e60a643fae0467'), ObjectId('5eb6651284c93e9e1b685024'), ObjectId('5eb66682dc99a524418da337'), ObjectId('5eb667a554cc6bc47dbfea44'), ObjectId('5eb6688cf9acda3a876322e4'), ObjectId('5eb669883e6dc49bd6f1540f'), ObjectId('5eb66a9b90f9dd06f1107866'), ObjectId('5eb66bb449a0728d932475bc'), ObjectId('5eb66ce4535d821544a14dee'), ObjectId('5eb66dabf3d5b58ef16a4c74'), ObjectId('5eb66e99e95b7d86f2518828'), ObjectId('5eb66fa738555190120005d2'), ObjectId('5eb670c2382a70cea3c90149'), ObjectId('5eb672382cf60f5b673dc845'), ObjectId('5eb6734f61272a1489607d7c'), ObjectId('5eb6746b3f8078c646a32068'), ObjectId('5eb675384beae11731a0ce35'), ObjectId('5eb676209d0d155a1c6530f3'), ObjectId('5eb6777b140e783b3524f4d9'), ObjectId('5eb6783b3dd775bea489b02d'), ObjectId('5eb67952c38498d75c86627f'), ObjectId('5eb67a4c109ddab70aec7b2d'), ObjectId('5eb67bc12373d9a910e8750f'), ObjectId('5eb67d3dd9818bcd44884d39'), ObjectId('5eb67e66b7921dcf1c2e6805'), ObjectId('5eb67fa821374c1c36ea76bb'), ObjectId('5eb680d98c70c48229cd26b6'), ObjectId('5eb6820dcc1fecfea5009f48'), ObjectId('5eb682ecd810c81378eb806d'), ObjectId('5eb68405b8f3f1e1b3084a52'), ObjectId('5eb6853a626f824ef428e315'), ObjectId('5eb688a782ee2ac4699515f2'), ObjectId('5eb689814e048265dd507dbc'), ObjectId('5eb68a771a268ae85ef97960'), ObjectId('5eb68b52298db2bd4cebdd0e'), ObjectId('5eb68c65501e64174bede873'), ObjectId('5eb68d458e708541f4671189'), ObjectId('5eb68e2fab2ce0451e2b4056'), ObjectId('5eb68edce0b5b75b05fba1e6'), ObjectId('5eb690038f7f6e26b6253fd5'), ObjectId('5eb690bd8d99ac316303ffb6'), ObjectId('5eb6918fa2e66438837c2d83'), ObjectId('5eb6925a31a5f94e1207b916'), ObjectId('5eb6944565d7b2466379f198'), ObjectId('5eb694f59c10ae1d407b7c2a'), ObjectId('5eb695e1ffe996bbe09292fe'), ObjectId('5eb696f6ef36438bec383b7e'), ObjectId('5eb697cac579ca076779cb0f'), ObjectId('5eb698a46de98c90f95a497d'), ObjectId('5eb699a671806057e76f0141'), ObjectId('5eb69a7d5587c492135fd56c'), ObjectId('5eb69b6fc6cad85bd913e12a'), ObjectId('5eb69c52d1ecab806f2beead'), ObjectId('5eb69cefc81bdf1aac4bf6a1'), ObjectId('5eb69e087e9ea4385e20beed'), ObjectId('5eb69f48a04ce33b509b4895'), ObjectId('5eb6a058cd265d6ef2ee766f'), ObjectId('5eb6a12f7ef80a97c531cc67'), ObjectId('5eb6a21fe632eaf0b1d593db'), ObjectId('5eb6a63fc0820e4534126e94'), ObjectId('5eb6a72dfc5d1c47d4ca9cd1'), ObjectId('5eb6a8462d272649f7b4df95'), ObjectId('5eb6a930b440ebf60d42d6c2'), ObjectId('5eb6aa15b5b4db2c7393254c'), ObjectId('5eb6ab260aef4a583d77118f'), ObjectId('5eb6ac1bfff106a6f58c42e7'), ObjectId('5eb6ad1662db4e6c180a378b'), ObjectId('5eb6ae390bdb0b194f41f9b3'), ObjectId('5eb6af2a6012ca09c1728130'), ObjectId('5eb6afc4e15b344d1a3aafa0'), ObjectId('5eb6b19b1c6e630676c62445'), ObjectId('5eb6b2a5a9211572420260e9'), ObjectId('5eb6b38eeb5e21b75a0d7cdb'), ObjectId('5eb6b45f4dab807be8d7a28a'), ObjectId('5eb6b53fd8471918b43146b7'), ObjectId('5eb6b61fabf00d5fdb2d05a3'), ObjectId('5eb6b71e5cd9b7b54c7d9961'), ObjectId('5eb6b9158f232307ce0bdc13'), ObjectId('5eb6b9dbb8b6b03010c4dcc6'), ObjectId('5eb6bad32c05d6f34cf32652'), ObjectId('5eb6bbbee2f17c3f3238cec8'), ObjectId('5eb6bca1b68e7672cd0ef210'), ObjectId('5eb6bdb1e7b6cc4614eb0edb'), ObjectId('5eb6beca47492aa1e0553de4'), ObjectId('5eb6bfc707fd60d7d77844de'), ObjectId('5ed3846f023b726e6d17d4f0'), ObjectId('5ed38b25d439f58cc06e5825'), ObjectId('5ed38d5420653aee6e3220c8'), ObjectId('5ed38efe1838c05e0c6fb6e4'), ObjectId('5ed3900863e5bffa1d2b4e2f'), ObjectId('5ed391925d33c4975503bb94'), ObjectId('5ed394144eb75866dfdcdc0d'), ObjectId('5ed39521d784bdc428779a0f'), ObjectId('5ed3966ae5903d41b23471ba'), ObjectId('5ed3980c016ddd49b0f4c304'), ObjectId('5ed3996045e3020d63762dce'), ObjectId('5ed39b1195eba19024e714bf'), ObjectId('5ed39d3781f6df0d82e6bfda'), ObjectId('5ed39f30fc1a9fd5e77e332f'), ObjectId('5ed3a07a5dbe3d7cdbc0a11f'), ObjectId('5ed3a21a7deae88594ebebcb'), ObjectId('5ed3a430b15357da758e9aaf'), ObjectId('5ed3a65cc612795088fb19b8'), ObjectId('5ed3a8655fa4a60f979e1f88'), ObjectId('5ed3ac8b4daab633d19b58d8'), ObjectId('5ed3add3461496c2716f7235'), ObjectId('5ed3af522f225fd825bf711a'), ObjectId('5ed3b088624645fcbe0374c5'), ObjectId('5ed3b2383758cc50c8bdd137'), ObjectId('5ed3b766a882d958e63eb52e')]
left_set = [item for item in all_ids_fixed if item not in edu_set]

# main_founder_search_v2(edu_set[:2])