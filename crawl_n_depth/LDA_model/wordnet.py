import json
import os

import matplotlib.pyplot as plt
from wordcloud import WordCloud
# Join the different processed titles together.
# long_string = ','.join(list(papers['paper_text_processed'].values))
# Create a WordCloud object
# path_to_json = "F://Armitage_project/crawl_n_depth/extracted_json_files/www.negotiations.com_3_data.json"
# json_paths = [os.path.abspath(x) for x in os.listdir("../extracted_json_files/")]
# path_to_jsons = "F:/Armitage_project/crawl_n_depth/extracted_json_files/"#specify the path for json files
# json_list = os.listdir(path_to_jsons)
# print(json_list)
def run_wordcloud_model(path_to_json):  # this will extract paragraph and header text from given json file and extract the topics from that
    with open(path_to_json) as json_file:
        data = json.load(json_file)
        for p in data:
            h_p_data =  p["header_text"]+p["paragraph_text"]
    print("wordcloud model is running")
    wordcloud = WordCloud(background_color="white", max_words=5000, contour_width=3, contour_color='steelblue')
    # Generate a word cloud
    combined_text = " ".join(h_p_data)
    try:
        wordcloud.generate(combined_text)
    except ValueError:
        print("cannot make word cloud for empty text")
        return "Vocabulary is empty"
    # Visualize the word cloud
    wordcloud.to_image()
    print(wordcloud.words_)
    word_cloud_results = []
    for each_res in wordcloud.words_:
        word_cloud_results.append([each_res,wordcloud.words_[each_res]])
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis("off")

    # plt.savefig("../wordclouds/"+each_json[:-4]+".png")
    # plt.show()
    data[0]['wordcloud_resutls'] = word_cloud_results
    with open(path_to_json, 'w') as outfile:
        json.dump(data, outfile)


# run_wordcloud_model("F://Armitage_project/crawl_n_depth/extracted_json_files/australianhelp.com_6_data.json")