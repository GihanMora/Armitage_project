import pymongo
import spacy
import pytextrank
import json

# example text
from Simplified_System.Database.db_connect import refer_collection


def run_textrank_model(entry_id,phrase_limit):  # this will extract paragraph and header text from given json file and extract the topics from that
    mycol = refer_collection()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    print("textrank model started", str(data[0]['_id']), data[0]['link'])
    try:
        h_p_data = data[0]["paragraph_text"] + data[0]["header_text"]  # do topic extraction on paragraph and header text

        combined_text = " ".join(h_p_data)

        # load a spaCy model, depending on language, scale, etc.
        nlp = spacy.load("en_core_web_sm")

        # add PyTextRank to the spaCy pipeline
        tr = pytextrank.TextRank()
        nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)
        nlp.max_length = 150000000
        doc = nlp(combined_text)

        # examine the top-ranked phrases in the document
        tr_results = []
        tr_words = []
        for p in doc._.phrases[:phrase_limit]:
            tr_results.append([p.rank,p.count, p.text])
            tr_words.append(p.text)
            # print(p.chunks)
        # summery_res = []
        # for sent in doc._.textrank.summary(limit_sentences=summery_limit):
        #     print(sent)
        #     summery_res.append(str(sent))
        # print(summery_res)
        if (len(tr_words)):
            print(tr_words)
            mycol.update_one({'_id': entry_id},
                             {'$set': {'textrank_results': tr_words}})
            print("Successfully extended the data entry with textrank results", entry_id)
        else:
            mycol.update_one({'_id': entry_id},
                             {'$set': {'textrank_results': []}})
            print("vocabulary is empty")
    except Exception:
        mycol.update_one({'_id': entry_id},
                         {'$set': {'textrank_results': []}})
        print("vocabulary is empty")


# run_textrank_model("F://Armitage_project_v1//crawl_n_depth//extracted_json_files//0_www.sureway.com.au_data.json",50,5)