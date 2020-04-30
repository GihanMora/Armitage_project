import gensim

# Load pre-trained Word2Vec model.
from bson import ObjectId

from Classification.multiclass_classifier import process_data_m
from Simplified_System.Database.db_connect import refer_collection

model = gensim.models.Doc2Vec.load("F:\Armitage_project\crawl_n_depth\Classification\classification.model")

    #setting testing data
def predict_class_tags(id_list):
    print("Preparing testing data")
    test_out = process_data_m(id_list,'test')
    test_tagged_data = [item[1] for item in test_out]
    test_ids = [item[0] for item in test_out]
    mycol= refer_collection()
    # predictions = []
    print("Prediction started..")
    for i, each in enumerate(test_tagged_data):
        print('entry_id',test_ids[i])
        print('company name',each[1])
        test_data = each[0]
        v1 = model.infer_vector(test_data)
        sims = model.docvecs.most_similar([v1])
        print('first 3 predictions',sims[:3])
        mycol.update_one({'_id': test_ids[i]},
                         {'$set': {'comp_type_pred': sims[:3]}})
        print("Successfully extended the data entry with company type predictions", test_ids[i])
    # predictions.append(sims[0][0])

# predict_class_tags([ObjectId('5ea5c4eecd9a0d942213d1ad'),ObjectId('5ea85f13b24221ec35ed81e4'),ObjectId('5ea5c4eecd9a0d942213d1ad')])
