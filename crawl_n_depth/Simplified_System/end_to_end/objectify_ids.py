from bson import ObjectId


def obs(id):
    return ObjectId(id)

f = open('id_listss.txt','r')
ids_l = [obs(i.strip()) for i in f.readlines()]
print(ids_l)