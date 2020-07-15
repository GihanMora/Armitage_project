# Author        :Sajani Ranasinghe
# Task          :Extract the founders, co-founders and important persons of an organization through the deep crawled pages
# Pre-conditions:The script uses RocketReach, NeverBounce APIs and AllenNLP, Glove Stanford embeddings

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
import allennlp_models.ner.crf_tagger
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
        except Exception as e:
            print("Exception Occured while extracting contacts from website",e)





def main():


    # The founders/important persons of an organization can be found by running the main_founder_search(entry_id_list),
    # eg: main_founder_search(['5eb703a2a86cec7b42163618', '5eb703b9a86cec7b42163619'])
    # or
    # The main_founder_search(entry_id_list) can be embedded in the main pipeline
    # eg: main_founder_search(['5eb63aff81de1c4846fd91ab'])

    # The following entry ids are updated with the important_person_company key value pair, in the refer_cleaned_collection()
    # updated_entry_id_list = ['5eb703a2a86cec7b42163618','5eb703b9a86cec7b42163619','5eb6a058cd265d6ef2ee766f','5eb66dabf3d5b58ef16a4c74','5eb7c4fd9a65a3d7609e4fd1','5eb7f2e0a97054c1c28ae403','5eb71606b7411bc8fe5ec287','5eb68e2fab2ce0451e2b4056','5eb762a5646627514dad781a','5eb67a4c109ddab70aec7b2d','5eb652de55de509b4a9efaf4','5eb76342646627514dad781f','5eb71564b7411bc8fe5ec282','5eb66bb449a0728d932475bc','5eb6a21fe632eaf0b1d593db','5eb65f2cde8cab37cd68dffd','5eb6820dcc1fecfea5009f48','5eb762fd646627514dad781c','5eb7d6a0f75273c9af329f7a','5eb6bbbee2f17c3f3238cec8','5eb689814e048265dd507dbc','5eb650acab06d680d6990351','5eb639ee2c60aae411d1ae8b','5eb8081955584ed5ddbe68f3','5eb7026aa86cec7b4216360a','5eb6734f61272a1489607d7c','5eb64a8e96bdd2bbbb3287e5','5eb672382cf60f5b673dc845','5eb8080355584ed5ddbe68f2','5eb6a930b440ebf60d42d6c2','5eb697cac579ca076779cb0f','5eb7c5bb9a65a3d7609e4fd4','5eb7c5d19a65a3d7609e4fd5','5eb7f3a7a97054c1c28ae40a','5eb64bc810a22fecd4eca987','5eb661a6796445df9bfd756d','5eb698a46de98c90f95a497d','5eb7f323a97054c1c28ae405','5eb70280a86cec7b4216360b','5eb7d6e4f75273c9af329f7d','5eb7f34ea97054c1c28ae407','5eb699a671806057e76f0141','5eb65433af5bcc3efe32c504','5eb727682d11eabb9aa47f83','5eb6567909d0de1b6b708cf8','5eb64f4ea0549166c51ca057','5eb6bdb1e7b6cc4614eb0edb','5eb6afc4e15b344d1a3aafa0','5eb695e1ffe996bbe09292fe','5eb6ab260aef4a583d77118f','5eb7273c2d11eabb9aa47f81','5eb7f364a97054c1c28ae408','5eb7f415a97054c1c28ae40f','5eb63539be65b70e5af0c7a9','5eb8085b55584ed5ddbe68f6','5eb7038ca86cec7b42163617','5eb70333a86cec7b42163613','5eb8084555584ed5ddbe68f5','5eb67bc12373d9a910e8750f','5eb646ce3b4442b4da91c057','5eb66a9b90f9dd06f1107866','5eb66ce4535d821544a14dee','5eb690bd8d99ac316303ffb6','5eb6944565d7b2466379f198','5eb7157ab7411bc8fe5ec283','5eb7639d646627514dad7822','5eb657e754ee9cbe1a7388c8','5eb651bc5fa088c453991725','5eb6556c29c37695bc97bec4','5eb68d458e708541f4671189','5eb7d6fbf75273c9af329f7e','5eb7f441a97054c1c28ae411','5eb634492802acb8c48e02aa','5eb70305a86cec7b42163611','5eb68405b8f3f1e1b3084a52','5eb67952c38498d75c86627f','5eb7d6b7f75273c9af329f7b','5eb6853a626f824ef428e315','5eb7f3d3a97054c1c28ae40c','5eb7d5d6f75273c9af329f72','5eb6631b245b7e033d0f92ed','5eb6b9158f232307ce0bdc13','5eb676209d0d155a1c6530f3','5eb6378b772150870b5c8d27','5eb76261646627514dad7817','5eb6af2a6012ca09c1728130','5eb762e6646627514dad781b','5eb76385646627514dad7821','5eb808f055584ed5ddbe68f9','5eb6688cf9acda3a876322e4','5eb68b52298db2bd4cebdd0e','5eb690038f7f6e26b6253fd5','5eb7d61bf75273c9af329f75','5eb62e2a134cc6fb9536e93d','5eb7d631f75273c9af329f76','5eb69a7d5587c492135fd56c','5eb6b71e5cd9b7b54c7d9961','5eb6311c86662885174692de','5eb808a355584ed5ddbe68f7','5eb682ecd810c81378eb806d','5eb7154eb7411bc8fe5ec281','5eb6479687b6932b9e6de098','5eb7f3e9a97054c1c28ae40d','5eb71591b7411bc8fe5ec284','5eb7d604f75273c9af329f74','5eb6783b3dd775bea489b02d','5eb6a8462d272649f7b4df95','5eb680d98c70c48229cd26b6','5eb7f338a97054c1c28ae406','5eb807ec55584ed5ddbe68f1','5eb6363894bd0b097f9c2734','5eb6ac1bfff106a6f58c42e7','5eb7161db7411bc8fe5ec288','5eb714ebb7411bc8fe5ec27d','5eb65942b46918d079adebe9','5eb640560732058562a400b3','5eb7628f646627514dad7819','5eb69c52d1ecab806f2beead','5eb67d3dd9818bcd44884d39','5eb694f59c10ae1d407b7c2a','5eb64e13158973dfa9982019','5eb6918fa2e66438837c2d83','5eb8091c55584ed5ddbe68fb','5eb68edce0b5b75b05fba1e6','5eb670c2382a70cea3c90149','5eb7d6cef75273c9af329f7c','5eb68c65501e64174bede873','5eb6b38eeb5e21b75a0d7cdb','5eb6b45f4dab807be8d7a28a','5eb69b6fc6cad85bd913e12a','5eb6bca1b68e7672cd0ef210','5eb67e66b7921dcf1c2e6805','5eb702d9a86cec7b4216360f','5eb7c4bb9a65a3d7609e4fcf','5eb69cefc81bdf1aac4bf6a1','5eb630147afe26eca4ba7bfa','5eb7277f2d11eabb9aa47f84','5eb66401b0e60a643fae0467','5eb6603b6e69c6f2e1092cf8','5eb675384beae11731a0ce35','5eb7031ca86cec7b42163612','5eb6a72dfc5d1c47d4ca9cd1','5eb7d689f75273c9af329f79','5eb7f2f8a97054c1c28ae404','5eb7f461a97054c1c28ae412','5eb7d5eef75273c9af329f73','5eb6925a31a5f94e1207b916','5eb7f37aa97054c1c28ae409','5eb76205646627514dad7813','5eb7c5149a65a3d7609e4fd2','5eb70376a86cec7b42163616','5eb7624b646627514dad7816','5eb70254a86cec7b42163609','5eb7c5e89a65a3d7609e4fd6','5eb727522d11eabb9aa47f82','5eb64cfc8c94747a21f39855','5eb702c2a86cec7b4216360e','5eb63c1e9c69232f6ed6edd8','5eb65d83728ad01002b3a5f6','5eb68a771a268ae85ef97960','5eb6ad1662db4e6c180a378b','5eb7621e646627514dad7814','5eb6bfc707fd60d7d77844de','5eb6b53fd8471918b43146b7','5eb7636f646627514dad7820','5eb6777b140e783b3524f4d9','5eb8093255584ed5ddbe68fc','5eb6746b3f8078c646a32068','5eb6ae390bdb0b194f41f9b3','5eb66682dc99a524418da337','5eb7f3bda97054c1c28ae40b','5eb76278646627514dad7818','5eb7f3ffa97054c1c28ae40e','5eb702efa86cec7b42163610','5eb6bad32c05d6f34cf32652','5eb7d72bf75273c9af329f7f','5eb7d652f75273c9af329f77','5eb715a7b7411bc8fe5ec285','5eb6a12f7ef80a97c531cc67','5eb63e1ee805d1cff3d80a25','5eb6beca47492aa1e0553de4','5eb70296a86cec7b4216360c','5eb7023ba86cec7b42163608','5eb688a782ee2ac4699515f2','5eb726fb2d11eabb9aa47f7f','5eb71538b7411bc8fe5ec280','5eb6b19b1c6e630676c62445','5eb648bf6bc924ef46ab60da','5eb67fa821374c1c36ea76bb','5eb69e087e9ea4385e20beed','5eb6b61fabf00d5fdb2d05a3','5eb71518b7411bc8fe5ec27f','5eb7f42aa97054c1c28ae410','5eb71501b7411bc8fe5ec27e','5eb6aa15b5b4db2c7393254c','5eb63ee743b668cb27ef8137','5eb715bdb7411bc8fe5ec286','5eb63aff81de1c4846fd91ab','5eb65b645417d406270e7e63','5eb65a927cb5b3a1ff4ae362','5eb70349a86cec7b42163614','5eb808d955584ed5ddbe68f8','5eb7d669f75273c9af329f78','5eb6b9dbb8b6b03010c4dcc6','5eb7c55d9a65a3d7609e4fd3','5eb6a63fc0820e4534126e94','5eb667a554cc6bc47dbfea44','5eb7d742f75273c9af329f80','5eb66e99e95b7d86f2518828','5eb63d1b9d2ec0b892c42dd5','5eb8082f55584ed5ddbe68f4','5eb66fa738555190120005d2','5eb6331597c8f5512179c4f1','5eb696f6ef36438bec383b7e','5eb714d5b7411bc8fe5ec27c','5eb69f48a04ce33b509b4895','5eb702aca86cec7b4216360d','5eb6651284c93e9e1b685024','5eb669883e6dc49bd6f1540f','5eb631f1fac479799dedd1f8','5eb6b2a5a9211572420260e9','5eb8090655584ed5ddbe68fa','5eb70360a86cec7b42163615','5eb714beb7411bc8fe5ec27b']


    # main_founder_search() function is updated to main_founder_search_v2()
    # Where the founders/important persons of an organization is extracted from crawled text without cross checking through LinkedIn
    main_founder_search_v2(['5eb63aff81de1c4846fd91ab'])



# if __name__ == "__main__":
#     main()

main_founder_search_v2(['5eb63aff81de1c4846fd91ab'])