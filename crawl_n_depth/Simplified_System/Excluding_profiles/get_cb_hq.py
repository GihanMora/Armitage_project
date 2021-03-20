from crawl_n_depth.Simplified_System.Database.db_connect import refer_collection


# f = open('all_OS.txt','r')
#
# comp_list = f.readlines()

# mycol = refer_collection()
# for ll in comp_list:
#     print(ll.strip())
#     ll=ll.strip()
#     # entry = mycol.find({"link": ll})
#     # data = [d for d in entry]
#     # print(data[0]['_id'])
#     mycol.update_one({"link": ll}, {'$set': {'ignore_flag': '1'}})
#
#     print("********************************************************")
#     # break

# def adding_ig(id_list):
#
#     mycol = refer_collection()
#     for id_a in id_list:
#         entry = mycol.find({"link": id_a})
#         data = [d for d in entry]
#         print(data[0]['_id'])
#         mycol.update_one({'_id': id_a}, {'$set': {'ignore_flag': '1'}})