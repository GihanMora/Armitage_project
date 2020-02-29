# import json
#
# from topia.termextract import extract
# text = "Compatibility of systems..."
#
#
# path_to_json = "F://Armitage_project/crawl_n_depth/extracted_json_files/www.negotiations.com_3_data.json"
#
# with open(path_to_json) as json_file:
#     data = json.load(json_file)
#     for p in data['attributes']:
#         h_p_data = p["paragraph_text"] + p["header_text"]
# combined_text = " ".join(h_p_data)
#
#
# extractor = extract.TermExtractor()
# extractor.filter(extract.DefaultFilter())
# print(extractor(combined_text))