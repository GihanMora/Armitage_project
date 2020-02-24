import json
from rake_nltk import Rake, Metric

path_to_json = "F://Armitage_project/crawl_n_depth/extracted_json_files/www.axcelerate.com.au_0_data.json"

with open(path_to_json) as json_file:
    data = json.load(json_file)
    for p in data['attributes']:
        h_p_data = p["header_text"]
combined_text = " ".join(h_p_data)
# print(combined_text)
# r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.

text = "RAKE short for Rapid Automatic Keyword Extraction algorithm, " \
       "is a domain independent keyword extraction algorithm which tries " \
       "to determine key phrases in a body of text by analyzing the frequency " \
       "of word appearance and its co-occurance with other words in the text."
r = Rake(ranking_metric=Metric.DEGREE_TO_FREQUENCY_RATIO)
r.extract_keywords_from_text(combined_text)
 # To get keyword phrases ranked highest to lowest.
res = r.get_ranked_phrases_with_scores()
f = open("rake_output.txt",'w')
for each in res:
    print(each)
    f.write(str(each)+'\n')