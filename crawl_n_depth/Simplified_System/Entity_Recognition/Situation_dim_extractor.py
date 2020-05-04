"""
Date: 4/12/2020 5:43 PM
Author: Achini
"""
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import nlp.Entity_feature_extraction as ENTITY_EXT
import tqdm


def extract_dimesions(df, search_phrase):

    clause_entity_info = []
    for row in tqdm.tqdm(df.itertuples(index=False), total=df.shape[0]):
        sent = row.sent
        p_id = 'P_' + str(row.para_id)
        sent_index = row.sent_index

        if type(row.subject) == str:
            subject = row.subject
            verb = row.verb
            object = str(row.object).strip()
            stopwords_list = stopwords.words('english')
            stopwords_list.extend(['The', 'A', 'An'])

            if object not in stopwords_list and subject not in stopwords_list:

                entities_spacy = ENTITY_EXT.get_enitites_spacy(subject)
                date = []
                location = []
                fac = []
                loc = []
                product = []
                event = []
                art = []

                source_entity = False
                entity_type = ''
                for ent in entities_spacy:
                    key = ent[0]
                    ent_type = ent[1]

                    if ent_type in ['PERSON', 'ORG', 'NORP', 'GPE', 'FAC']:
                        source_entity = True
                        entity_type = ent_type
                        subject = key

                if not entity_type:
                    np_list = ENTITY_EXT.get_noun_phrases(subject)
                    if len(np_list) > 0:
                        source_entity = True
                        if entity_type == '':
                            entity_type = "NP"

                entities_spacy_obj = ENTITY_EXT.get_enitites_spacy(sent)
                for ent_obj in entities_spacy_obj:
                    key_obj = ent_obj[0]
                    ent_type_obj = ent_obj[1]

                    if ent_type_obj == 'DATE':
                        date.append(key_obj)

                    if ent_type_obj == 'GPE':
                        location.append(key_obj)

                    if ent_type_obj == 'FAC':
                        fac.append(key_obj)

                    if ent_type_obj == 'LOC':
                        loc.append(key_obj)

                    if ent_type_obj == 'PRODUCT':
                        product.append(key_obj)

                    if ent_type_obj == 'EVENT':
                        event.append(key_obj)

                    if ent_type_obj == 'WORK_OF_ART':
                        art.append(key_obj)

                if source_entity:
                    nouns = ENTITY_EXT.get_nouns_spacy(object)
                    noun_list = []
                    if len(nouns) != 0:
                        noun_list = nouns
                    subject = subject.translate(str.maketrans('', '', string.punctuation))
                    text_tokens = word_tokenize(subject)
                    clean_subject_arr = [word for word in text_tokens if not word in stopwords_list]
                    clean_subject = ' '.join(clean_subject_arr).strip()
                    clause_entity_info.append([p_id, sent_index, clean_subject,  verb, object, entity_type, verb + ' ' + object, date, noun_list, location, fac, loc, product, event, art, sent])

    clause_df = pd.DataFrame(clause_entity_info, columns=['para_id', 'sent_index', 'subject', 'verb', 'object', 'entity_type', 'clause', 'date', 'nouns', 'location', 'fac', 'loc', 'product', 'event', 'art','sent'])
    clause_df.to_csv('output/'+search_phrase+'/situation_dims.csv')
    return clause_df
