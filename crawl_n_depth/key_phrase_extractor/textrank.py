import spacy
import pytextrank
import json

# example text
text = "Compatibility of systems of linear constraints over the set of natural numbers. Criteria of compatibility of a system of linear Diophantine equations, strict inequations, and nonstrict inequations are considered. Upper bounds for components of a minimal set of solutions and algorithms of construction of minimal generating sets of solutions for all types of systems are given. These criteria and the corresponding algorithms for constructing a minimal supporting set of solutions can be used in solving all the considered types systems and systems of mixed types."
path_to_json = "F://Armitage_project/crawl_n_depth/extracted_json_files/www.axcelerate.com.au_0_data.json"

with open(path_to_json) as json_file:
    data = json.load(json_file)
    for p in data['attributes']:
        h_p_data = p["header_text"]
combined_text = " ".join(h_p_data)
# load a spaCy model, depending on language, scale, etc.
nlp = spacy.load("en_core_web_sm")

# add PyTextRank to the spaCy pipeline
tr = pytextrank.TextRank()
nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)

doc = nlp(combined_text)

# examine the top-ranked phrases in the document
for p in doc._.phrases[:20]:

    print("{:.4f} {:5d}  {}".format(p.rank, p.count, p.text))
    # print(p.chunks)

for sent in doc._.textrank.summary(limit_phrases=1000, limit_sentences=5):
    print(sent)