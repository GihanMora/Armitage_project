import pymongo
from bson import ObjectId


def refer_simplified_dump_col_min():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    # myclient = pymongo.MongoClient(
    #     "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["simplified_dump_min"]  # creates a collection
    return mycol
def refer_collection():
  myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  # myclient = pymongo.MongoClient(
  #     "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
  # mydb = myclient["CompanyDatabase"]  # creates a database
  mydb = myclient["miner"]  # creates a database

  mycol = mydb["comp_data_cleaned"]  # creates a collection
  return mycol

def update_rich_description(id_list):
    mycol = refer_collection()
    min_col = refer_simplified_dump_col_min()
    for id_a in id_list:
        entry = mycol.find({"_id": id_a})
        data = [d for d in entry]
        entry_min = min_col.find({"_id": id_a})
        data_min = [d for d in entry_min]
        rich_description = data[0]['rich_description']
        description = data_min[0]['description']
        print('**', rich_description)
        print('--', description)
        if(rich_description=='None' or rich_description==''):

            rich_description = description
        min_col.update_one({'_id': id_a},
                         {'$set': {'description':rich_description}})

assets= [ObjectId('5f76ec8f087161005148ece3'), ObjectId('5f76cb2b087161005148eb9f'), ObjectId('5f6437688af3a4af8c749f01'), ObjectId('5f76c4b1087161005148eb6b'), ObjectId('5f76e7ac087161005148eca9'), ObjectId('5f76e7fe087161005148ecad'), ObjectId('5f76e69a087161005148eca0'), ObjectId('5f76d1f0087161005148ebe0'), ObjectId('5f76d1a1087161005148ebdc'), ObjectId('5f76f8be087161005148ed47'), ObjectId('5f759f47087161005148e8c9'), ObjectId('5f76d14d087161005148ebd8'), ObjectId('5f70d93d0269a3cd9caf5128'), ObjectId('5f76df57087161005148ec60'), ObjectId('5f76f5f1087161005148ed31'), ObjectId('5f76f854087161005148ed44'), ObjectId('5f76b30c087161005148eaea'), ObjectId('5f75b8b5087161005148e9bf'), ObjectId('5f76b114087161005148eae1'), ObjectId('5f76dec8087161005148ec5c'), ObjectId('5f76f487087161005148ed24'), ObjectId('5f70ca3e0269a3cd9caf5074'), ObjectId('5f76f633087161005148ed33'), ObjectId('5f76c0f5087161005148eb4f'), ObjectId('5f7701de087161005148ed85'), ObjectId('5f76e417087161005148ec8a'), ObjectId('5f76b472087161005148eaf2'), ObjectId('5f76dafc087161005148ec35'), ObjectId('5f19d55909e1c3c7030256ab'), ObjectId('5f76d28e087161005148ebe6'), ObjectId('5f76dea4087161005148ec5a'), ObjectId('5f76edca087161005148ecee'), ObjectId('5f68359a9d6d5b0536dfd377'), ObjectId('5f19c8f009e1c3c703025670'), ObjectId('5f76e265087161005148ec7c'), ObjectId('5f76ecb8087161005148ece5'), ObjectId('5f6835fa9d6d5b0536dfd37d'), ObjectId('5f76c486087161005148eb69'), ObjectId('5f76cf06087161005148ebc8'), ObjectId('5f770a5b087161005148edbf'), ObjectId('5f758107087161005148e7b5'), ObjectId('5f76ec3e087161005148ece0'), ObjectId('5f76e5a4087161005148ec97'), ObjectId('5f76c428087161005148eb66'), ObjectId('5f76a470087161005148eaa6'), ObjectId('5f770236087161005148ed89'), ObjectId('5f76db20087161005148ec37'), ObjectId('5f76e0fb087161005148ec6f'), ObjectId('5f76e1a8087161005148ec77'), ObjectId('5f76b342087161005148eaec'), ObjectId('5f76cbc6087161005148eba4'), ObjectId('5f76ec10087161005148ecde'), ObjectId('5f76e290087161005148ec7e'), ObjectId('5f76d79b087161005148ec0e'), ObjectId('5f76ef07087161005148ecfa'), ObjectId('5f76a332087161005148ea9f'), ObjectId('5f76e042087161005148ec68'), ObjectId('5f75bb46087161005148e9d3'), ObjectId('5f75684c087161005148e6b3'), ObjectId('5f75b696087161005148e9af'), ObjectId('5f76f3dd087161005148ed20'), ObjectId('5f75a410087161005148e8ef'), ObjectId('5f76ae75087161005148ead1'), ObjectId('5f6835ba9d6d5b0536dfd379'), ObjectId('5f758438087161005148e7d2'), ObjectId('5f76bac7087161005148eb18'), ObjectId('5f76efb0087161005148ed00'), ObjectId('5f76d9bf087161005148ec1f'), ObjectId('5f76bb08087161005148eb1a'), ObjectId('5f76e891087161005148ecb4'), ObjectId('5f76bec1087161005148eb3c'), ObjectId('5f76ce73087161005148ebc3'), ObjectId('5f76f010087161005148ed03'), ObjectId('5f76e016087161005148ec66'), ObjectId('5f76ee87087161005148ecf4'), ObjectId('5f6437528af3a4af8c749eff'), ObjectId('5f76b0d3087161005148eadf'), ObjectId('5f76bc7b087161005148eb2e'), ObjectId('5f75ab4b087161005148e93f'), ObjectId('5f76a714087161005148eab4'), ObjectId('5f757af0087161005148e76f'), ObjectId('5f75b835087161005148e9ba'), ObjectId('5f75a551087161005148e904'), ObjectId('5f76c1ed087161005148eb55'), ObjectId('5f76eead087161005148ecf6'), ObjectId('5f76d6df087161005148ec08'), ObjectId('5f76fd8c087161005148ed6b'), ObjectId('5f76c830087161005148eb87'), ObjectId('5f76c939087161005148eb8e'), ObjectId('5f75bc04087161005148e9da'), ObjectId('5f76d603087161005148ebff'), ObjectId('5f76af76087161005148ead7'), ObjectId('5f76adda087161005148eace'), ObjectId('5f76b8b2087161005148eb0c'), ObjectId('5f75a954087161005148e92c'), ObjectId('5f76cfae087161005148ebcd'), ObjectId('5f76e0ab087161005148ec6c'), ObjectId('5f76e15d087161005148ec73'), ObjectId('5f76d3c4087161005148ebef'), ObjectId('5f76e949087161005148ecba'), ObjectId('5f76eb43087161005148ecd7'), ObjectId('5f76f104087161005148ed0c'), ObjectId('5f770a2f087161005148edbd'), ObjectId('5f76f28f087161005148ed16'), ObjectId('5f75ae6b087161005148e958'), ObjectId('5f76db77087161005148ec3a'), ObjectId('5f76b70a087161005148eb01'), ObjectId('5f76ba22087161005148eb14'), ObjectId('5f76a522087161005148eaaa'), ObjectId('5f76e8f5087161005148ecb7'), ObjectId('5f76eeda087161005148ecf8'), ObjectId('5f76e7d8087161005148ecab'), ObjectId('5f76e49a087161005148ec8f'), ObjectId('5f75bb1c087161005148e9d1'), ObjectId('5f19ca5e09e1c3c703025690'), ObjectId('5f76ed74087161005148ecea'), ObjectId('5f76f225087161005148ed13'), ObjectId('5f76de1a087161005148ec56'), ObjectId('5f76f353087161005148ed1c'), ObjectId('5f76f767087161005148ed3b'), ObjectId('5f76bf47087161005148eb40'), ObjectId('5f76da03087161005148ec22'), ObjectId('5f76d174087161005148ebda'), ObjectId('5f76e642087161005148ec9d'), ObjectId('5f76d35f087161005148ebec'), ObjectId('5f76e3e8087161005148ec88'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('5f7705ce087161005148ed9f'), ObjectId('5f7582bc087161005148e7c3'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f75b34b087161005148e988'), ObjectId('5f70c86a0269a3cd9caf5063'), ObjectId('5f76c9fe087161005148eb96'), ObjectId('5f76b99a087161005148eb10'), ObjectId('5f76f58d087161005148ed2f'), ObjectId('5f76f15f087161005148ed0f'), ObjectId('5f76ece4087161005148ece7'), ObjectId('5f76f544087161005148ed2b'), ObjectId('5f76c30a087161005148eb5d'), ObjectId('5f76f6be087161005148ed36'), ObjectId('5f709be90269a3cd9caf4fd4'), ObjectId('5f76cae4087161005148eb9d'), ObjectId('5f70c7df0269a3cd9caf505e'), ObjectId('5f757a68087161005148e76a'), ObjectId('5f76dc20087161005148ec40'), ObjectId('5f76e9fc087161005148eccb'), ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f76e3b2087161005148ec86'), ObjectId('5f76ab3b087161005148eac4'), ObjectId('5f76e844087161005148ecb1'), ObjectId('5f76d717087161005148ec0a'), ObjectId('5f76cb54087161005148eba1'), ObjectId('5f75893f087161005148e800'), ObjectId('5f76df82087161005148ec62'), ObjectId('5f76d060087161005148ebd2'), ObjectId('5f76e5f0087161005148ec99'), ObjectId('5f70d60b0269a3cd9caf5101'), ObjectId('5f76c572087161005148eb71'), ObjectId('5f76d1c4087161005148ebde'), ObjectId('5f7577b0087161005148e74f'), ObjectId('5f76ce4f087161005148ebc1'), ObjectId('5f76e454087161005148ec8c'), ObjectId('5f76c18d087161005148eb52'), ObjectId('5f76ea22087161005148eccd'), ObjectId('5f76eda5087161005148ecec'), ObjectId('5f76bb54087161005148eb1c'), ObjectId('5f76ddfe087161005148ec54'), ObjectId('5f1ecf5362de5888b3f12f04'), ObjectId('5f76d65e087161005148ec03'), ObjectId('5f76b9dd087161005148eb12'), ObjectId('5f76b749087161005148eb03'), ObjectId('5f76bf6e087161005148eb42'), ObjectId('5f770534087161005148ed9a'), ObjectId('5f76da81087161005148ec31'), ObjectId('5f76ee12087161005148ecf0'), ObjectId('5f76b61c087161005148eafb'), ObjectId('5f770688087161005148eda5'), ObjectId('5f76e33b087161005148ec82'), ObjectId('5f76bd6c087161005148eb32'), ObjectId('5f76e6f1087161005148eca3'), ObjectId('5f19d59a09e1c3c7030256b1'), ObjectId('5f77086d087161005148edb1'), ObjectId('5f76d6af087161005148ec06'), ObjectId('5f6de2d2144e831840676870'), ObjectId('5f76aea8087161005148ead3'), ObjectId('5f76f323087161005148ed1a'), ObjectId('5f76dc89087161005148ec44'), ObjectId('5f76ebea087161005148ecdc'), ObjectId('5f76d919087161005148ec19'), ObjectId('5f76e99d087161005148ecc8'), ObjectId('5f76c35c087161005148eb60'), ObjectId('5f76f7ba087161005148ed3f'), ObjectId('5f76c062087161005148eb4b'), ObjectId('5f76ff6d087161005148ed75'), ObjectId('5f76afdb087161005148ead9'), ObjectId('5f709ec20269a3cd9caf4ff0'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f76a7ca087161005148eab7'), ObjectId('5f76a58e087161005148eaae'), ObjectId('5f76b698087161005148eafe'), ObjectId('5f76af3b087161005148ead5'), ObjectId('5f75bbcf087161005148e9d8'), ObjectId('5f76d4c5087161005148ebf7'), ObjectId('5f76d82f087161005148ec12'), ObjectId('5f76f03b087161005148ed05'), ObjectId('5f76bbc6087161005148eb1f'), ObjectId('5f76f56b087161005148ed2d'), ObjectId('5f76f908087161005148ed49'), ObjectId('5f76c03d087161005148eb49'), ObjectId('5f76cd00087161005148ebba'), ObjectId('5f77016e087161005148ed81'), ObjectId('5f76bd93087161005148eb34'), ObjectId('5f76f78d087161005148ed3d'), ObjectId('5f75b5ac087161005148e9a2'), ObjectId('5f76c773087161005148eb81'), ObjectId('5f76ceb7087161005148ebc5'), ObjectId('5f76d895087161005148ec15'), ObjectId('5f76eb1b087161005148ecd5'), ObjectId('5f75983d087161005148e88e'), ObjectId('5f76b04d087161005148eadb'), ObjectId('5f76b82d087161005148eb08'), ObjectId('5f76bf94087161005148eb44'), ObjectId('5f76c6c6087161005148eb7c'), ObjectId('5f76c7a4087161005148eb83'), ObjectId('5f76b878087161005148eb0a'), ObjectId('5f76d632087161005148ec01'), ObjectId('5f76dcf2087161005148ec49'), ObjectId('5f76f4e2087161005148ed28'), ObjectId('5f76c3b8087161005148eb63'), ObjectId('5f76c988087161005148eb92'), ObjectId('5f76c246087161005148eb58'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f76e12b087161005148ec71'), ObjectId('5f18841f35a2278f64f9e5f4'), ObjectId('5f19d54209e1c3c7030256a9'), ObjectId('5f76b784087161005148eb05'), ObjectId('5f76b20a087161005148eae6'), ObjectId('5f76dde3087161005148ec52'), ObjectId('5f76b08c087161005148eadd'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f76dd3c087161005148ec4c'), ObjectId('5f76d265087161005148ebe4'), ObjectId('5f76ef33087161005148ecfc'), ObjectId('5f76e616087161005148ec9b'), ObjectId('5f770205087161005148ed87'), ObjectId('5f76b5d7087161005148eaf9'), ObjectId('5f76c5be087161005148eb74'), ObjectId('5f76a55d087161005148eaac'), ObjectId('5f75b9c8087161005148e9c6'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f76eaca087161005148ecd2'), ObjectId('5f76ba6c087161005148eb16'), ObjectId('5f756a60087161005148e6c5'), ObjectId('5f76c503087161005148eb6e'), ObjectId('5f76f821087161005148ed42'), ObjectId('5f76cce2087161005148ebb8'), ObjectId('5f76b4b9087161005148eaf4'), ObjectId('5f76d59f087161005148ebfc'), ObjectId('5f76dba7087161005148ec3c'), ObjectId('5f76a8f1087161005148eabd'), ObjectId('5f76b18a087161005148eae3'), ObjectId('5f76dca5087161005148ec46'), ObjectId('5f76e81e087161005148ecaf'), ObjectId('5f76e184087161005148ec75'), ObjectId('5f76ada5087161005148eacc'), ObjectId('5f76e4e9087161005148ec92'), ObjectId('5f76d414087161005148ebf2'), ObjectId('5f76a3b4087161005148eaa2'), ObjectId('5f75b933087161005148e9c2'), ObjectId('5f76e746087161005148eca6'), ObjectId('5f76b4f1087161005148eaf6'), ObjectId('5f76c66d087161005148eb79'), ObjectId('5f76c962087161005148eb90'), ObjectId('5f76d99a087161005148ec1d'), ObjectId('5f19c98709e1c3c70302567e'), ObjectId('5f6ddf0b144e831840676837'), ObjectId('5f76f0c1087161005148ed09'), ObjectId('5f76f4b7087161005148ed26'), ObjectId('5f76e526087161005148ec94')]
ndis = [ObjectId('5f759112087161005148e847'), ObjectId('5f759644087161005148e872'), ObjectId('5f75b490087161005148e994'), ObjectId('5f75a2c1087161005148e8e4'), ObjectId('5f757b5f087161005148e774'), ObjectId('5f7594c8087161005148e865'), ObjectId('5f757c05087161005148e77c'), ObjectId('5f75ab1e087161005148e93d'), ObjectId('5f757570087161005148e736'), ObjectId('5f757ee2087161005148e794'), ObjectId('5f709ec20269a3cd9caf4ff0'), ObjectId('5f757243087161005148e70d'), ObjectId('5f75751a087161005148e732'), ObjectId('5f758324087161005148e7c5'), ObjectId('5f756b98087161005148e6cf'), ObjectId('5f7574de087161005148e72e'), ObjectId('5f7566da087161005148e6a8'), ObjectId('5f758e08087161005148e82f'), ObjectId('5f756edf087161005148e6eb'), ObjectId('5f757f85087161005148e79a'), ObjectId('5f75a551087161005148e904'), ObjectId('5f756a60087161005148e6c5'), ObjectId('5f75a613087161005148e90d'), ObjectId('5f7569f5087161005148e6c1'), ObjectId('5f758030087161005148e7a1'), ObjectId('5f75ae44087161005148e956'), ObjectId('5f7581ef087161005148e7bb'), ObjectId('5f75bf72087161005148e9fb'), ObjectId('5f75ca29087161005148ea4b'), ObjectId('5f756958087161005148e6bb'), ObjectId('5f7598d6087161005148e897'), ObjectId('5f75b882087161005148e9bd'), ObjectId('5f756cb8087161005148e6d8'), ObjectId('5f756a8c087161005148e6c7'), ObjectId('5f75c020087161005148ea00'), ObjectId('5f75a7e0087161005148e91c'), ObjectId('5f75be3c087161005148e9e7'), ObjectId('5f756708087161005148e6aa'), ObjectId('5f75af0b087161005148e95c'), ObjectId('5f7596ec087161005148e879'), ObjectId('5f758f57087161005148e839'), ObjectId('5f75bbcf087161005148e9d8'), ObjectId('5f759c13087161005148e8b2'), ObjectId('5f75972e087161005148e87c'), ObjectId('5f75c3e6087161005148ea1e'), ObjectId('5f75bb46087161005148e9d3'), ObjectId('5f75b1c7087161005148e97b'), ObjectId('5f75a3ed087161005148e8ed'), ObjectId('5f7592f0087161005148e857'), ObjectId('5f75adcd087161005148e952'), ObjectId('5f75b933087161005148e9c2'), ObjectId('5f757be1087161005148e77a'), ObjectId('5f7586b4087161005148e7ec'), ObjectId('5f75b330087161005148e986'), ObjectId('5f756605087161005148e6a2'), ObjectId('5f75826d087161005148e7bf'), ObjectId('5f759e42087161005148e8c2'), ObjectId('5f75b515087161005148e999'), ObjectId('5f758ab9087161005148e80c'), ObjectId('5f75700e087161005148e6f7'), ObjectId('5f756f45087161005148e6ef'), ObjectId('5f7565b7087161005148e6a0'), ObjectId('5f75c521087161005148ea29'), ObjectId('5f757674087161005148e742'), ObjectId('5f75b8b5087161005148e9bf'), ObjectId('5f757a68087161005148e76a'), ObjectId('5f75a410087161005148e8ef'), ObjectId('5f757857087161005148e758'), ObjectId('5f756c72087161005148e6d6'), ObjectId('5f75b316087161005148e984'), ObjectId('5f759f47087161005148e8c9'), ObjectId('5f75c5fd087161005148ea30'), ObjectId('5f75ab4b087161005148e93f'), ObjectId('5f7564f4087161005148e69c'), ObjectId('5f1ecdec62de5888b3f12ee7'), ObjectId('5f757bb3087161005148e778'), ObjectId('5f6f432745dea3de84616921'), ObjectId('5f75ca53087161005148ea4d'), ObjectId('5f757c4b087161005148e77e'), ObjectId('5f75881d087161005148e7f9'), ObjectId('5f757213087161005148e70b'), ObjectId('5f75bd43087161005148e9e2'), ObjectId('5f757a23087161005148e767'), ObjectId('5f758696087161005148e7ea'), ObjectId('5f758528087161005148e7dc'), ObjectId('5f7585c7087161005148e7e0'), ObjectId('5f7573a7087161005148e71a'), ObjectId('5f75ba51087161005148e9ca'), ObjectId('5f75805f087161005148e7a3'), ObjectId('5f75703c087161005148e6f9'), ObjectId('5f1ece2062de5888b3f12eeb'), ObjectId('5f757309087161005148e715'), ObjectId('5f756bd4087161005148e6d1'), ObjectId('5f758374087161005148e7c9'), ObjectId('5f75ac8e087161005148e949'), ObjectId('5f757e19087161005148e78c'), ObjectId('5f75ad68087161005148e94e'), ObjectId('5f709f0e0269a3cd9caf4ff3'), ObjectId('5f757769087161005148e74c'), ObjectId('5f75a0a1087161005148e8d3'), ObjectId('5f75b7e5087161005148e9b7'), ObjectId('5f756906087161005148e6b9'), ObjectId('5f75c7bc087161005148ea3b'), ObjectId('5f75ca87087161005148ea4f'), ObjectId('5f756f18087161005148e6ed'), ObjectId('5f75961f087161005148e870'), ObjectId('5f7570ff087161005148e701'), ObjectId('5f757e3b087161005148e78e'), ObjectId('5f75af97087161005148e961'), ObjectId('5f7569be087161005148e6bf'), ObjectId('5f75719c087161005148e707'), ObjectId('5f75a22d087161005148e8df'), ObjectId('5f75789a087161005148e75c'), ObjectId('5f757f59087161005148e798'), ObjectId('5f75b249087161005148e97e'), ObjectId('5f759ba5087161005148e8ae'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f758de7087161005148e82d'), ObjectId('5f7575ad087161005148e738'), ObjectId('5f75aa92087161005148e936'), ObjectId('5f756e7b087161005148e6e7'), ObjectId('5f759399087161005148e85b'), ObjectId('5f6dddda144e83184067682d'), ObjectId('5f75c7ec087161005148ea3d'), ObjectId('5f757643087161005148e73e'), ObjectId('5f758c3f087161005148e816'), ObjectId('5f75aafd087161005148e93b'), ObjectId('5f75907d087161005148e843'), ObjectId('5f75a802087161005148e91e'), ObjectId('5f75a18f087161005148e8da'), ObjectId('5f757a01087161005148e765'), ObjectId('5f75adac087161005148e950'), ObjectId('5f7588c3087161005148e7fd'), ObjectId('5f75781d087161005148e754'), ObjectId('5f758676087161005148e7e8'), ObjectId('5f756b59087161005148e6cd'), ObjectId('5f758c67087161005148e818'), ObjectId('5f758780087161005148e7f3'), ObjectId('5f757836087161005148e756'), ObjectId('5f75a485087161005148e8fe'), ObjectId('5f7568cf087161005148e6b7'), ObjectId('5f7593cd087161005148e85d'), ObjectId('5f75bcb7087161005148e9df'), ObjectId('5f70e85b0269a3cd9caf51d9'), ObjectId('5f758dae087161005148e82b'), ObjectId('5f758459087161005148e7d4'), ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f7576bd087161005148e745'), ObjectId('5f75a259087161005148e8e1'), ObjectId('5f70c65e0269a3cd9caf504d'), ObjectId('5f756f79087161005148e6f1'), ObjectId('5f757e71087161005148e790'), ObjectId('5f758419087161005148e7d0'), ObjectId('5f75aab1087161005148e938'), ObjectId('5f75a5cd087161005148e90a'), ObjectId('5f75c979087161005148ea46'), ObjectId('5f758723087161005148e7f1'), ObjectId('5f75b9c8087161005148e9c6'), ObjectId('5f75654d087161005148e69e'), ObjectId('5f75677c087161005148e6ac'), ObjectId('5f75706e087161005148e6fb'), ObjectId('5f75b9f6087161005148e9c8'), ObjectId('5f7598a0087161005148e893'), ObjectId('5f757279087161005148e70f'), ObjectId('5f75aa09087161005148e932'), ObjectId('5f759db2087161005148e8bc'), ObjectId('5f75ab78087161005148e941'), ObjectId('5f757af0087161005148e76f'), ObjectId('5f6de1f6144e831840676867'), ObjectId('5f75749e087161005148e72c'), ObjectId('5f759535087161005148e869'), ObjectId('5f75983d087161005148e88e'), ObjectId('5f19ca4a09e1c3c70302568e'), ObjectId('5f75a745087161005148e918'), ObjectId('5f758299087161005148e7c1'), ObjectId('5f75a982087161005148e92e'), ObjectId('5f758438087161005148e7d2'), ObjectId('5f758006087161005148e79f'), ObjectId('5f759167087161005148e84b'), ObjectId('5f757b3b087161005148e772'), ObjectId('5f75a885087161005148e923'), ObjectId('5f709c4e0269a3cd9caf4fd8'), ObjectId('5f7584c9087161005148e7d8'), ObjectId('5f70ed210269a3cd9caf5213'), ObjectId('5f7571e3087161005148e709'), ObjectId('5f7567de087161005148e6b0'), ObjectId('5f759f9b087161005148e8cc'), ObjectId('5f75bacd087161005148e9cd'), ObjectId('5f75a8c0087161005148e927'), ObjectId('5f757fdb087161005148e79d'), ObjectId('5f75709a087161005148e6fd'), ObjectId('5f758508087161005148e7da'), ObjectId('5f758107087161005148e7b5'), ObjectId('5f75765b087161005148e740'), ObjectId('5f7593fa087161005148e85f'), ObjectId('5f75a82e087161005148e920'), ObjectId('5f75a8de087161005148e929'), ObjectId('5f758962087161005148e802'), ObjectId('5f7583f3087161005148e7ce'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f756eac087161005148e6e9'), ObjectId('5f757545087161005148e734'), ObjectId('5f756984087161005148e6bd'), ObjectId('5f6460344c677bfa552c5be7'), ObjectId('5f757372087161005148e718'), ObjectId('5f75b604087161005148e9a7'), ObjectId('5f7587d8087161005148e7f6'), ObjectId('5f756fd9087161005148e6f5'), ObjectId('5f75b3dd087161005148e98e'), ObjectId('5f75c4d6087161005148ea26'), ObjectId('5f7577b0087161005148e74f'), ObjectId('5f758ae7087161005148e80e'), ObjectId('5f759b5e087161005148e8ab'), ObjectId('5f75c059087161005148ea03'), ObjectId('5f75b67c087161005148e9ad'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f75bc04087161005148e9da'), ObjectId('5f759cc6087161005148e8b6'), ObjectId('5f758b3d087161005148e810'), ObjectId('5f70a3ba0269a3cd9caf501e'), ObjectId('5f70ec280269a3cd9caf51fc'), ObjectId('5f70ca580269a3cd9caf5076'), ObjectId('5f75687a087161005148e6b5'), ObjectId('5f75bb93087161005148e9d6'), ObjectId('5f7570cb087161005148e6ff'), ObjectId('5f75b5ac087161005148e9a2'), ObjectId('5f75787a087161005148e75a'), ObjectId('5f758a6b087161005148e809'), ObjectId('5f757d70087161005148e787'), ObjectId('5f75a954087161005148e92c'), ObjectId('5f682585a7cef498a185c2a6'), ObjectId('5f757733087161005148e749'), ObjectId('5f7574ff087161005148e730'), ObjectId('5f75893f087161005148e800'), ObjectId('5f70f28c0269a3cd9caf524c'), ObjectId('5f7596c5087161005148e877'), ObjectId('5f7583c4087161005148e7cc'), ObjectId('5f756fab087161005148e6f3'), ObjectId('5f75950e087161005148e867'), ObjectId('5f75b58c087161005148e9a0'), ObjectId('5f759df9087161005148e8bf'), ObjectId('5f7591ae087161005148e84d'), ObjectId('5f70cc670269a3cd9caf5098'), ObjectId('5f75a1af087161005148e8dc'), ObjectId('5f75baf3087161005148e9cf'), ObjectId('5f70efbe0269a3cd9caf522c'), ObjectId('5f756e20087161005148e6e3'), ObjectId('5f756a2c087161005148e6c3'), ObjectId('5f1ed7ee62de5888b3f12f21'), ObjectId('5f75966e087161005148e874'), ObjectId('5f75b364087161005148e98a'), ObjectId('5f758f80087161005148e83b'), ObjectId('5f75a8a2087161005148e925'), ObjectId('5f75b34b087161005148e988'), ObjectId('5f75c0d1087161005148ea08'), ObjectId('5f75acfb087161005148e94c'), ObjectId('5f75b620087161005148e9a9'), ObjectId('5f758d50087161005148e828'), ObjectId('5f759fce087161005148e8ce'), ObjectId('5f759281087161005148e854'), ObjectId('5f757ab4087161005148e76d'), ObjectId('5f756c03087161005148e6d3'), ObjectId('5f757f1b087161005148e796'), ObjectId('5f75899f087161005148e804'), ObjectId('5f75958c087161005148e86c'), ObjectId('5f7566ab087161005148e6a6'), ObjectId('5f757136087161005148e703'), ObjectId('5f75b54f087161005148e99c'), ObjectId('5f75c747087161005148ea37'), ObjectId('5f75a340087161005148e8e8'), ObjectId('5f757165087161005148e705'), ObjectId('5f7590d6087161005148e845'), ObjectId('5f758708087161005148e7ef'), ObjectId('5f758648087161005148e7e6'), ObjectId('5f75985d087161005148e890'), ObjectId('5f75b56b087161005148e99e'), ObjectId('5f75c19e087161005148ea0d'), ObjectId('5f758084087161005148e7a5'), ObjectId('5f758b5d087161005148e812'), ObjectId('5f75976e087161005148e87e'), ObjectId('5f758615087161005148e7e4'), ObjectId('5f756deb087161005148e6e1'), ObjectId('5f75834f087161005148e7c7'), ObjectId('5f75b05a087161005148e966'), ObjectId('5f75c417087161005148ea20'), ObjectId('5f75b29a087161005148e980'), ObjectId('5f7582bc087161005148e7c3'), ObjectId('5f75ae6b087161005148e958'), ObjectId('5f756e4d087161005148e6e5'), ObjectId('5f75a578087161005148e906'), ObjectId('5f75b6bb087161005148e9b1'), ObjectId('5f75a5a8087161005148e908'), ObjectId('5f75b835087161005148e9ba'), ObjectId('5f7585eb087161005148e7e2'), ObjectId('5f75c1be087161005148ea0f'), ObjectId('5f75ae03087161005148e954'), ObjectId('5f6437328af3a4af8c749efd'), ObjectId('5f759ac1087161005148e8a5'), ObjectId('5f75a6a9087161005148e913'), ObjectId('5f75684c087161005148e6b3'), ObjectId('5f756d0c087161005148e6da'), ObjectId('5f7591df087161005148e84f'), ObjectId('5f756d41087161005148e6dc'), ObjectId('5f7598bc087161005148e895'), ObjectId('5f75a62f087161005148e90f'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f7567aa087161005148e6ae'), ObjectId('5f757cd7087161005148e782'), ObjectId('5f759137087161005148e849'), ObjectId('5f75746f087161005148e72a'), ObjectId('5f75b5ea087161005148e9a5'), ObjectId('5f758e28087161005148e831'), ObjectId('5f75af75087161005148e95f'), ObjectId('5f7580a4087161005148e7a7'), ObjectId('5f759492087161005148e863'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f75bc63087161005148e9dc'), ObjectId('5f70a2170269a3cd9caf5011'), ObjectId('5f7578da087161005148e75e'), ObjectId('5f757d4e087161005148e785'), ObjectId('5f7572a8087161005148e711'), ObjectId('5f758ee4087161005148e836'), ObjectId('5f757b86087161005148e776'), ObjectId('5f75900c087161005148e840'), ObjectId('5f75bb1c087161005148e9d1'), ObjectId('5f756d76087161005148e6de'), ObjectId('5f756677087161005148e6a4'), ObjectId('5f756abd087161005148e6c9'), ObjectId('5f6db7bc7e23326b374cc472'), ObjectId('5f7572dc087161005148e713'), ObjectId('5f75b696087161005148e9af')]

ids_first = [ObjectId('5f19d55909e1c3c7030256ab'), ObjectId('5f7b937ff5bb1adde1413e72'), ObjectId('5f757733087161005148e749'), ObjectId('5f75b5ac087161005148e9a2'), ObjectId('5f1ed9a162de5888b3f12f4a'), ObjectId('5f18ed5035a2278f64f9e6bd'), ObjectId('5f1ed98b62de5888b3f12f48'), ObjectId('5f7b9e6cf5bb1adde1413f02'), ObjectId('5f7b67aff5bb1adde1413dd3'), ObjectId('5f70a2170269a3cd9caf5011'), ObjectId('5f183f13464603f10dce0dba'), ObjectId('5f6437688af3a4af8c749f01'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f7b66d6f5bb1adde1413dc8'), ObjectId('5f76ea22087161005148eccd'), ObjectId('5f7b8fb5f5bb1adde1413e40'), ObjectId('5f7b9865f5bb1adde1413eb3'), ObjectId('5f645f754c677bfa552c5bd2'), ObjectId('5f76c773087161005148eb81'), ObjectId('5f75b6bb087161005148e9b1'), ObjectId('5f7b902ff5bb1adde1413e45'), ObjectId('5f75983d087161005148e88e'), ObjectId('5f7ba504f5bb1adde1413f5a'), ObjectId('5f758438087161005148e7d2'), ObjectId('5f6835da9d6d5b0536dfd37b'), ObjectId('5f7ba3abf5bb1adde1413f3e'), ObjectId('5f7ba94df5bb1adde1413f7f'), ObjectId('5f19d6df09e1c3c7030256cd'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('5f76ba6c087161005148eb16'), ObjectId('5f758107087161005148e7b5'), ObjectId('5f75893f087161005148e800'), ObjectId('5f645f944c677bfa552c5bd4'), ObjectId('5f7b9241f5bb1adde1413e5f'), ObjectId('5f756abd087161005148e6c9'), ObjectId('5f7bb0fdf5bb1adde1413fcd'), ObjectId('5f19c98709e1c3c70302567e'), ObjectId('5f7ba2baf5bb1adde1413f31'), ObjectId('5f183e14464603f10dce0da6'), ObjectId('5f19c8bc09e1c3c70302566c'), ObjectId('5f76bf47087161005148eb40'), ObjectId('5f7b9276f5bb1adde1413e62'), ObjectId('5f19cabe09e1c3c703025698'), ObjectId('5f770a2f087161005148edbd'), ObjectId('5f1ece2062de5888b3f12eeb'), ObjectId('5f70eda40269a3cd9caf5217'), ObjectId('5f19c87c09e1c3c703025666'), ObjectId('5f7ba0eef5bb1adde1413f19'), ObjectId('5f7baae8f5bb1adde1413f8b'), ObjectId('5f7b64aef5bb1adde1413da9'), ObjectId('5f7ba054f5bb1adde1413f12'), ObjectId('5f7570ff087161005148e701'), ObjectId('5f759cc6087161005148e8b6'), ObjectId('5f19d6b209e1c3c7030256c9'), ObjectId('5f7baff0f5bb1adde1413fc3'), ObjectId('5f76e290087161005148ec7e'), ObjectId('5f7b90d3f5bb1adde1413e4e'), ObjectId('5f7ba204f5bb1adde1413f27'), ObjectId('5f7ba6bff5bb1adde1413f6b'), ObjectId('5f758528087161005148e7dc'), ObjectId('5f6437128af3a4af8c749efb'), ObjectId('5f76d59f087161005148ebfc'), ObjectId('5f7b6409f5bb1adde1413da0'), ObjectId('5f7b6465f5bb1adde1413da6'), ObjectId('5f7592f0087161005148e857'), ObjectId('5f6460344c677bfa552c5be7'), ObjectId('5f7b9d59f5bb1adde1413ef4'), ObjectId('5f75ae6b087161005148e958'), ObjectId('5f7b9db8f5bb1adde1413ef8'), ObjectId('5f6835ba9d6d5b0536dfd379'), ObjectId('5f76b784087161005148eb05'), ObjectId('5f7b69b0f5bb1adde1413dea'), ObjectId('5f76aea8087161005148ead3'), ObjectId('5f7b65fef5bb1adde1413dbc'), ObjectId('5f183efd464603f10dce0db8'), ObjectId('5f1ecdec62de5888b3f12ee7'), ObjectId('5f7b8f0bf5bb1adde1413e37'), ObjectId('5f6f4fcb41c09be1b8045811'), ObjectId('5f1ed7ee62de5888b3f12f21'), ObjectId('5f7b930bf5bb1adde1413e6a'), ObjectId('5f19d59a09e1c3c7030256b1'), ObjectId('5f7b8db4f5bb1adde1413e2b'), ObjectId('5f7b6524f5bb1adde1413db1'), ObjectId('5f7b8d46f5bb1adde1413e27'), ObjectId('5f7b9320f5bb1adde1413e6c'), ObjectId('5f70a3ba0269a3cd9caf501e'), ObjectId('5f7b665af5bb1adde1413dc2'), ObjectId('5f7b8a75f5bb1adde1413dfb'), ObjectId('5f75958c087161005148e86c'), ObjectId('5f7ba776f5bb1adde1413f70'), ObjectId('5f76ee87087161005148ecf4'), ObjectId('5f1eadd362de5888b3f12eb3'), ObjectId('5f7b9e83f5bb1adde1413f04'), ObjectId('5f7ba265f5bb1adde1413f2d'), ObjectId('5f7bb5bef5bb1adde1413fff'), ObjectId('5f7b643df5bb1adde1413da3'), ObjectId('5f7b97a5f5bb1adde1413ea9'), ObjectId('5f7ba617f5bb1adde1413f65'), ObjectId('5f19d5af09e1c3c7030256b3'), ObjectId('5f7ba341f5bb1adde1413f37'), ObjectId('5f76d6df087161005148ec08'), ObjectId('5f77086d087161005148edb1'), ObjectId('5f70c86a0269a3cd9caf5063'), ObjectId('5f7b9b6cf5bb1adde1413ed7'), ObjectId('5f1ed90062de5888b3f12f3c'), ObjectId('5f76ff6d087161005148ed75'), ObjectId('5f7b6854f5bb1adde1413ddc'), ObjectId('5f75719c087161005148e707'), ObjectId('5f7b8b50f5bb1adde1413e0f'), ObjectId('5f7ba21af5bb1adde1413f29'), ObjectId('5f7582bc087161005148e7c3'), ObjectId('5f70ca580269a3cd9caf5076'), ObjectId('5f19d78d09e1c3c7030256dd'), ObjectId('5f7b67e3f5bb1adde1413dd6'), ObjectId('5f7b8c4af5bb1adde1413e1b'), ObjectId('5f76adda087161005148eace'), ObjectId('5f709c4e0269a3cd9caf4fd8'), ObjectId('5f75961f087161005148e870'), ObjectId('5f75b9f6087161005148e9c8'), ObjectId('5f7b8bdff5bb1adde1413e16'), ObjectId('5f7b8c1df5bb1adde1413e19'), ObjectId('5f6437528af3a4af8c749eff'), ObjectId('5f7b9a50f5bb1adde1413ec9'), ObjectId('5f1eaef362de5888b3f12ed2'), ObjectId('5f756a60087161005148e6c5'), ObjectId('5f7b96b6f5bb1adde1413e9d'), ObjectId('5f7ba119f5bb1adde1413f1d'), ObjectId('5f7b9465f5bb1adde1413e85'), ObjectId('5f75881d087161005148e7f9'), ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f76bd93087161005148eb34'), ObjectId('5f7bac35f5bb1adde1413f9c'), ObjectId('5f7bac60f5bb1adde1413fa0'), ObjectId('5f75aafd087161005148e93b'), ObjectId('5f7ba5c7f5bb1adde1413f62'), ObjectId('5f7bb407f5bb1adde1413feb'), ObjectId('5f19d54209e1c3c7030256a9'), ObjectId('5f76f4b7087161005148ed26'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f7b9b3ff5bb1adde1413ed5'), ObjectId('5f7b9534f5bb1adde1413e8d'), ObjectId('5f75ad68087161005148e94e'), ObjectId('5f757243087161005148e70d'), ObjectId('5f7b68eef5bb1adde1413de2'), ObjectId('5f76f8be087161005148ed47'), ObjectId('5f7ba53df5bb1adde1413f5d'), ObjectId('5f7b8a01f5bb1adde1413df5'), ObjectId('5f19d58409e1c3c7030256af'), ObjectId('5f7b9f38f5bb1adde1413f0b'), ObjectId('5f1ece0162de5888b3f12ee9'), ObjectId('5f7b978ff5bb1adde1413ea7'), ObjectId('5f7b6697f5bb1adde1413dc5'), ObjectId('5f75b56b087161005148e99e'), ObjectId('5f7b928cf5bb1adde1413e64'), ObjectId('5f76a332087161005148ea9f'), ObjectId('5f7bb4faf5bb1adde1413ff6'), ObjectId('5f76a7ca087161005148eab7'), ObjectId('5f18ece535a2278f64f9e6b6'), ObjectId('5f19ca9409e1c3c703025694'), ObjectId('5f76c486087161005148eb69'), ObjectId('5f7b9ed6f5bb1adde1413f07'), ObjectId('5f7b984ef5bb1adde1413eb1'), ObjectId('5f7b69eef5bb1adde1413dee'), ObjectId('5f7bb093f5bb1adde1413fc8'), ObjectId('5f183e89464603f10dce0dae'), ObjectId('5f1e99ee62de5888b3f12e46'), ObjectId('5f7b9e09f5bb1adde1413efc'), ObjectId('5f1ecf5362de5888b3f12f04'), ObjectId('5f7b9215f5bb1adde1413e5b'), ObjectId('5f7b89c4f5bb1adde1413df2'), ObjectId('5f6de160144e831840676860'), ObjectId('5f75bb46087161005148e9d3'), ObjectId('5f7babdff5bb1adde1413f97'), ObjectId('5f76c5be087161005148eb74'), ObjectId('5f19d70b09e1c3c7030256d1'), ObjectId('5f7b94c8f5bb1adde1413e89'), ObjectId('5f19ca5e09e1c3c703025690'), ObjectId('5f7b960cf5bb1adde1413e98'), ObjectId('5f183dde464603f10dce0da2'), ObjectId('5f7bac4af5bb1adde1413f9e'), ObjectId('5f70d60b0269a3cd9caf5101'), ObjectId('5f7bb593f5bb1adde1413ffd'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f709be90269a3cd9caf4fd4'), ObjectId('5f70fa840269a3cd9caf52b5'), ObjectId('5f7b8b9ef5bb1adde1413e13'), ObjectId('5f7ba3ebf5bb1adde1413f43'), ObjectId('5f7b9070f5bb1adde1413e48'), ObjectId('5f18eca435a2278f64f9e6b0'), ObjectId('5f709f0e0269a3cd9caf4ff3'), ObjectId('5f7ba3c1f5bb1adde1413f40'), ObjectId('5f7b8d02f5bb1adde1413e23'), ObjectId('5f18841f35a2278f64f9e5f4'), ObjectId('5f7b6612f5bb1adde1413dbe'), ObjectId('5f7b9a87f5bb1adde1413ecc'), ObjectId('5f76a470087161005148eaa6'), ObjectId('5f7b8e14f5bb1adde1413e2f'), ObjectId('5f7596c5087161005148e877'), ObjectId('5f7b922bf5bb1adde1413e5d'), ObjectId('5f6ddf0b144e831840676837'), ObjectId('5f7ba37ff5bb1adde1413f3b'), ObjectId('5f7ba355f5bb1adde1413f39'), ObjectId('5f758ee4087161005148e836'), ObjectId('5f7b934bf5bb1adde1413e6f'), ObjectId('5f7ba90cf5bb1adde1413f7d'), ObjectId('5f7b980df5bb1adde1413eae'), ObjectId('5f76d174087161005148ebda'), ObjectId('5f19d56f09e1c3c7030256ad'), ObjectId('5f70c65e0269a3cd9caf504d'), ObjectId('5f183e29464603f10dce0da8'), ObjectId('5f75b882087161005148e9bd'), ObjectId('5f1e9cb062de5888b3f12e6d'), ObjectId('5f76c7a4087161005148eb83'), ObjectId('5f7b699cf5bb1adde1413de8'), ObjectId('5f18ec8435a2278f64f9e6ae'), ObjectId('5f7ba85ef5bb1adde1413f77'), ObjectId('5f7bb5f3f5bb1adde1414002'), ObjectId('5f7bab76f5bb1adde1413f92'), ObjectId('5f7b98c6f5bb1adde1413eb8'), ObjectId('5f18750a182dbb7a59a62642'), ObjectId('5f7b9750f5bb1adde1413ea3'), ObjectId('5f7b9f8bf5bb1adde1413f0e'), ObjectId('5f7b692cf5bb1adde1413de5'), ObjectId('5f75684c087161005148e6b3'), ObjectId('5f75b8b5087161005148e9bf'), ObjectId('5f7b95a1f5bb1adde1413e93'), ObjectId('5f7b9abdf5bb1adde1413ecf'), ObjectId('5f7ba190f5bb1adde1413f22'), ObjectId('5f75b696087161005148e9af'), ObjectId('5f7b65a1f5bb1adde1413db8'), ObjectId('5f7b8f95f5bb1adde1413e3e'), ObjectId('5f7572dc087161005148e713'), ObjectId('5f7b9e34f5bb1adde1413eff'), ObjectId('5f7ba73ff5bb1adde1413f6e'), ObjectId('5f75bacd087161005148e9cd'), ObjectId('5f7b8f72f5bb1adde1413e3c'), ObjectId('5f75700e087161005148e6f7'), ObjectId('5f7ba9e0f5bb1adde1413f84'), ObjectId('5f7bab60f5bb1adde1413f90'), ObjectId('5f7bab11f5bb1adde1413f8d'), ObjectId('5f7b8ad9f5bb1adde1413e0a'), ObjectId('5f7b90eaf5bb1adde1413e50'), ObjectId('5f76b82d087161005148eb08'), ObjectId('5f76bf94087161005148eb44'), ObjectId('5f76c4b1087161005148eb6b'), ObjectId('5f7b954df5bb1adde1413e8f'), ObjectId('5f7b9afff5bb1adde1413ed2'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f7b6503f5bb1adde1413daf'), ObjectId('5f7b90bdf5bb1adde1413e4c'), ObjectId('5f7b8a61f5bb1adde1413df9'), ObjectId('5f7b6754f5bb1adde1413dcf'), ObjectId('5f76d28e087161005148ebe6'), ObjectId('5f75b5ea087161005148e9a5'), ObjectId('5f7b98fdf5bb1adde1413ebc'), ObjectId('5f7ba075f5bb1adde1413f14'), ObjectId('5f1eae8662de5888b3f12ec8'), ObjectId('5f7b6735f5bb1adde1413dcd'), ObjectId('5f7ba66cf5bb1adde1413f68'), ObjectId('5f7ba805f5bb1adde1413f74'), ObjectId('5f7ba4c2f5bb1adde1413f57'), ObjectId('5f7ba104f5bb1adde1413f1b'), ObjectId('5f19ca4a09e1c3c70302568e'), ObjectId('5f7b64c2f5bb1adde1413dab'), ObjectId('5f7b658cf5bb1adde1413db6'), ObjectId('5f7b98dcf5bb1adde1413eba'), ObjectId('5f757e19087161005148e78c'), ObjectId('5f7bb160f5bb1adde1413fd2'), ObjectId('5f7ba40af5bb1adde1413f45'), ObjectId('5f75bbcf087161005148e9d8'), ObjectId('5f75b933087161005148e9c2'), ObjectId('5f7b6820f5bb1adde1413dd9'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f7574de087161005148e72e'), ObjectId('5f682585a7cef498a185c2a6'), ObjectId('5f7bb4c2f5bb1adde1413ff3')]
# update_rich_description(ndis)

