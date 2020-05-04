import spacy
import nltk

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load('en_core_web_sm')
nltk.download('averaged_perceptron_tagger')


def get_is_verb(text):
    doc = nlp(text)
    is_verb = False
    for token in doc:
        if token.pos_ == 'VERB':
            is_verb = True

    return is_verb


def get_nouns_spacy(text):
    doc = nlp(text)
    nouns = []
    for token in doc:
        if token.pos_ == 'NOUN' and token.ent_type_ == '':
            nouns.append(token.text)
        # print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
        #       token.shape_, token.is_alpha, token.is_stop)

    return nouns


def get_enitites_spacy(text):
    doc = nlp(text)
    entity_list = []
    # Find named entities, phrases and concepts
    for entity in doc.ents:
        entity_list.append([entity.text, entity.label_])

    return entity_list


def get_enitites_nltk(text):
    tokens = nltk.word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    print(pos_tags)

    noun_phrases = []
    for term in pos_tags:
        if term[1] in ['NN', 'NNS', 'NE']:
            noun_phrases.append(term[0])

    return noun_phrases


def get_similarity_score(text1, text2):
    similarity = text1.similarity(text2)
    return similarity


def get_noun_phrases(text):
    tokens = nltk.word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    # print(pos_tags)

    noun_phrases = []
    for term in pos_tags:
        if term[1] in ['NN', 'NNS', 'NE']:
            noun_phrases.append(term[0])
    return noun_phrases

