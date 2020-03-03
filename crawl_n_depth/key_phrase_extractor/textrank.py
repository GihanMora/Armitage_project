import spacy
import pytextrank
import json

# example text
def run_textrank_model(path_to_json,phrase_limit,summery_limit):  # this will extract paragraph and header text from given json file and extract the topics from that
    with open(path_to_json) as json_file:
        data = json.load(json_file)
        for p in data:
            # h_p_data =  p["header_text"]+p["paragraph_text"]
            h_p_data = p["description"]
    # combined_text = " ".join(h_p_data)
    combined_text = h_p_data
    print(combined_text)
    print("running textrank model")
    # load a spaCy model, depending on language, scale, etc.
    nlp = spacy.load("en_core_web_sm")

    # add PyTextRank to the spaCy pipeline
    tr = pytextrank.TextRank()
    nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)
    nlp.max_length = 150000000
    doc = nlp(combined_text)

    # examine the top-ranked phrases in the document
    tr_results = []
    for p in doc._.phrases[:phrase_limit]:
        print("{:.4f} {:5d}  {}".format(p.rank, p.count, p.text))
        tr_results.append([p.rank,p.count, p.text])
        # print(p.chunks)
    summery_res = []
    for sent in doc._.textrank.summary(limit_sentences=summery_limit):
        print(sent)
        summery_res.append(str(sent))
    print(tr_results)
    print(summery_res)
    data[0]['textrank_resutls'] = tr_results  # dump the extracted topics back to the json file
    data[0]['textrank_summery__resutls'] = summery_res
    with open(path_to_json, 'w') as outfile:
        json.dump(data, outfile)

# run_textrank_model("F://Armitage_project//crawl_n_depth//extracted_json_files//4_australianassignmenthelp.com_data.json",50,5)