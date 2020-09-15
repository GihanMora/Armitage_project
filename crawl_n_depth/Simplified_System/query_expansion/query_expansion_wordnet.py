from nltk.corpus import wordnet

def get_synonyms(word,number_of_syn):
    synonyms = []


    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonyms.append(l.name())

    # print(synonyms)
    u_synonyms = []
    [u_synonyms.append(x) for x in synonyms if x not in u_synonyms]
    # print(u_synonyms)
    return u_synonyms[:number_of_syn]

# print(get_synonyms('security',3))
def expand_queries(query):
    expanded_queries = []
    query_terms = query.strip().split(" ")
    for i,each_term in enumerate(query_terms):
        syn_for_each_term = get_synonyms(each_term,4)
        # print(i,each_term,syn_for_each_term)
        for each_s in syn_for_each_term:
            modified_query_terms = query_terms
            modified_query_terms[i] = each_s
            # print(" ".join(modified_query_terms))
            expanded_queries.append(" ".join(modified_query_terms))

    u_expanded_queries = []
    [u_expanded_queries.append(x) for x in expanded_queries if x not in u_expanded_queries]
    return u_expanded_queries

u_qs =  expand_queries("risk management systems")
for k in u_qs:
    print(k)