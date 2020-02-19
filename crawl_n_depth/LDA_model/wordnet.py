import json
import os

import matplotlib.pyplot as plt
from wordcloud import WordCloud
# Join the different processed titles together.
# long_string = ','.join(list(papers['paper_text_processed'].values))
# Create a WordCloud object
# path_to_json = "F://Armitage_project/crawl_n_depth/extracted_json_files/www.negotiations.com_3_data.json"
json_paths = [os.path.abspath(x) for x in os.listdir("../extracted_json_files/")]
path_to_jsons = "F:/Armitage_project/crawl_n_depth/extracted_json_files/"#specify the path for json files
json_list = os.listdir(path_to_jsons)
for each_json in json_list:
    with open(path_to_jsons+each_json) as json_file:
        data = json.load(json_file)
        for p in data['attributes']:
            h_p_data = p["paragraph_text"] + p["header_text"]
    wordcloud = WordCloud(background_color="white", max_words=5000, contour_width=3, contour_color='steelblue')
    # Generate a word cloud
    combined_text = " ".join(h_p_data)
    wordcloud.generate(combined_text)
    # Visualize the word cloud
    wordcloud.to_image()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

    plt.savefig("../wordclouds/"+each_json[:-4]+".png")
    plt.show()