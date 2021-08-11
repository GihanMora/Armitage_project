
from bson import ObjectId
import sys
from os.path import dirname as up
import pandas as pd


three_up = up(up(up(__file__)))

sys.path.insert(0, three_up)
from Simplified_System.end_to_end.repair_profiles import get_entries_project
from Simplified_System.Database.db_connect import refer_collection,refer_query_col,simplified_export,simplified_export_via_queue,add_to_simplified_export_queue,refer_projects_col,simplified_export_with_sources_and_confidence
from Simplified_System.web_profile_data_crawler.avention_scraper import get_aven_data,add_to_avention_queue,get_aven_data_via_queue

# get_entries_project(ObjectId('604e4854edb24f74a2dc6c31'))
profiles_list = [ObjectId('604f898da8ff6195bc26d992'), ObjectId('604f9917a8ff6195bc26da46'), ObjectId('602f9b7b7ba8308c59e0f51b'), ObjectId('604f7322a8ff6195bc26d86f'), ObjectId('604f838fa8ff6195bc26d943'), ObjectId('604f8926a8ff6195bc26d98c'), ObjectId('604fa8075080c72c8450402d'), ObjectId('604f86bba8ff6195bc26d973'), ObjectId('604f92b0a8ff6195bc26d9f3'), ObjectId('604f9390a8ff6195bc26da00'), ObjectId('60420760a63926c168451567'), ObjectId('602cc22c4512a34739136411'), ObjectId('604f75fda8ff6195bc26d88d'), ObjectId('604f77c4a8ff6195bc26d8a1'), ObjectId('602aa10d1a03b37ed3a71dd6'), ObjectId('604fa4c55080c72c84504003'), ObjectId('604f776ca8ff6195bc26d89d'), ObjectId('604f7a43a8ff6195bc26d8c8'), ObjectId('604f7ad1a8ff6195bc26d8d0'), ObjectId('604f7b96a8ff6195bc26d8dc'), ObjectId('604f963ba8ff6195bc26da21'), ObjectId('604fac095080c72c8450405d'), ObjectId('604f93eba8ff6195bc26da04'), ObjectId('604f89e5a8ff6195bc26d996'), ObjectId('604fae7a5080c72c8450407f'), ObjectId('604f76cfa8ff6195bc26d895'), ObjectId('604f7906a8ff6195bc26d8b5'), ObjectId('6041d54fa63926c168451454'), ObjectId('604f9020a8ff6195bc26d9da'), ObjectId('604fadf25080c72c84504079'), ObjectId('604f977ca8ff6195bc26da33'), ObjectId('604f8caba8ff6195bc26d9b8'), ObjectId('604fa1fd5080c72c84503fe0'), ObjectId('604fa2bf5080c72c84503feb'), ObjectId('604f9133a8ff6195bc26d9e4'), ObjectId('604f9a78a8ff6195bc26da59'), ObjectId('604f9504a8ff6195bc26da10'), ObjectId('604f7ee5a8ff6195bc26d907'), ObjectId('604f8a92a8ff6195bc26d99f'), ObjectId('604f804fa8ff6195bc26d919'), ObjectId('604f8e1ba8ff6195bc26d9c6'), ObjectId('604f9c92a8ff6195bc26da73'), ObjectId('604faed95080c72c84504084'), ObjectId('604fafaf5080c72c8450408d'), ObjectId('602f18ca7ba8308c59e0f239'), ObjectId('604f7872a8ff6195bc26d8ad'), ObjectId('602ab05a1a03b37ed3a71e49'), ObjectId('604f8553a8ff6195bc26d961'), ObjectId('604f8408a8ff6195bc26d94b'), ObjectId('604fb1d25080c72c845040a7'), ObjectId('604f8739a8ff6195bc26d978'), ObjectId('604f808ea8ff6195bc26d91d'), ObjectId('604f7940a8ff6195bc26d8b9'), ObjectId('604f72dba8ff6195bc26d86b'), ObjectId('604fb8935080c72c845040ea'), ObjectId('604f92f0a8ff6195bc26d9f7'), ObjectId('604f9b94a8ff6195bc26da68'), ObjectId('604fa0e45080c72c84503fd4'), ObjectId('604f74a1a8ff6195bc26d87f'), ObjectId('604f9674a8ff6195bc26da25'), ObjectId('604fb2ac5080c72c845040b3'), ObjectId('604f729ca8ff6195bc26d867'), ObjectId('604f85eca8ff6195bc26d96a'), ObjectId('604fa84c5080c72c84504032'), ObjectId('6041b2a5a63926c168451374'), ObjectId('604f8629a8ff6195bc26d96e'), ObjectId('602a991e1a03b37ed3a71d96'), ObjectId('604fa5295080c72c84504009'), ObjectId('604f4093a8ff6195bc26d52d'), ObjectId('604fb6885080c72c845040d6'), ObjectId('604f9439a8ff6195bc26da09'), ObjectId('602a9b671a03b37ed3a71da8'), ObjectId('604f724ea8ff6195bc26d863'), ObjectId('604f7db9a8ff6195bc26d8fc'), ObjectId('602ab5221a03b37ed3a71e66'), ObjectId('604fa34c5080c72c84503ff1'), ObjectId('604f9b32a8ff6195bc26da64'), ObjectId('604f7684a8ff6195bc26d891'), ObjectId('604f8a23a8ff6195bc26d99a'), ObjectId('604f7ff6a8ff6195bc26d915'), ObjectId('604fb5b25080c72c845040cd'), ObjectId('6041c80ba63926c168451408'), ObjectId('604f7bd6a8ff6195bc26d8e0'), ObjectId('602ab9191a03b37ed3a71e7b'), ObjectId('604fe0925080c72c84504334'), ObjectId('604f8be4a8ff6195bc26d9af'), ObjectId('604fad1f5080c72c8450406b'), ObjectId('604f78bfa8ff6195bc26d8b1'), ObjectId('604f8fd5a8ff6195bc26d9d6'), ObjectId('604f8788a8ff6195bc26d97c'), ObjectId('604f933ba8ff6195bc26d9fc'), ObjectId('604f9d45a8ff6195bc26da7c'), ObjectId('604f95d3a8ff6195bc26da1b'), ObjectId('604f9729a8ff6195bc26da2f'), ObjectId('604f82bba8ff6195bc26d936'), ObjectId('602f95e97ba8308c59e0f4fd'), ObjectId('604f8470a8ff6195bc26d953'), ObjectId('604fb22a5080c72c845040ac'), ObjectId('604f7f82a8ff6195bc26d90f'), ObjectId('604fb5745080c72c845040c9'), ObjectId('604fad5e5080c72c8450406f'), ObjectId('604f8341a8ff6195bc26d93f'), ObjectId('604fa7755080c72c84504027'), ObjectId('604f7c2ea8ff6195bc26d8e4'), ObjectId('604f7f2ba8ff6195bc26d90b'), ObjectId('604fadba5080c72c84504075'), ObjectId('604fa1bb5080c72c84503fdc'), ObjectId('604f84c8a8ff6195bc26d958'), ObjectId('604f850da8ff6195bc26d95d'), ObjectId('604fb1945080c72c845040a3'), ObjectId('604f7833a8ff6195bc26d8a9'), ObjectId('604f88caa8ff6195bc26d987'), ObjectId('604f81c2a8ff6195bc26d92a'), ObjectId('604faa685080c72c84504047'), ObjectId('604f83e3a8ff6195bc26d947'), ObjectId('604f735da8ff6195bc26d873'), ObjectId('604fa6835080c72c8450401e'), ObjectId('604f73e9a8ff6195bc26d87b'), ObjectId('602e4c9fa4a518be2f97bee7'), ObjectId('604fa5835080c72c8450400e'), ObjectId('602a9f981a03b37ed3a71dca'), ObjectId('604f7b57a8ff6195bc26d8d8'), ObjectId('604f8dc7a8ff6195bc26d9c1'), ObjectId('604f9cf0a8ff6195bc26da78'), ObjectId('604fa25b5080c72c84503fe5'), ObjectId('602b08211a03b37ed3a72045'), ObjectId('602aa7e91a03b37ed3a71e0c'), ObjectId('604fb4985080c72c845040bf'), ObjectId('602f21237ba8308c59e0f26c'), ObjectId('604f8f47a8ff6195bc26d9cf'), ObjectId('604fa04d5080c72c84503fd0'), ObjectId('604f74fda8ff6195bc26d883'), ObjectId('604f9ae4a8ff6195bc26da5f'), ObjectId('604f98b1a8ff6195bc26da41'), ObjectId('604fdefa5080c72c8450431b'), ObjectId('604fe0435080c72c8450432f')]

# add_to_avention_queue(profiles_list)



def check_cb(id_list):
    mycol = refer_collection()
    id_l = []
    has_verified_cb_profile = []
    cb_hq = []
    df = pd.DataFrame()
    for each_id in id_list:
        is_yes = mycol.find({"_id": each_id})
        data = [d for d in is_yes]
        id_l.append(each_id)
        if('comp_headquaters_cb' in data[0].keys()):
            if(data[0]['link']==data[0]['comp_website_cb']):
                print(data[0]['comp_headquaters_cb'])
                print(data[0]['comp_website_cb'])
                print(data[0]['link'])
                print()
                has_verified_cb_profile.append('yes')
                cb_hq.append(data[0]['comp_headquaters_cb'])
            elif(data[0]['comp_name'] in data[0]['comp_website_cb']):
                print(data[0]['comp_headquaters_cb'])
                print(data[0]['comp_website_cb'])
                print(data[0]['link'])
                print()
                has_verified_cb_profile.append('yes')
                cb_hq.append(data[0]['comp_headquaters_cb'])
            else:
                print('No profile')
                has_verified_cb_profile.append('no')
                cb_hq.append('')
        else:
            print('No profile')
            has_verified_cb_profile.append('no')
            cb_hq.append('')

    print(len(id_l))
    print(len(has_verified_cb_profile))
    print(len(cb_hq))
    df['id'] = id_l
    df['has_verified_cb_profile'] = has_verified_cb_profile
    df['cb_hq'] = cb_hq

    df.to_csv('C:\Project_files\\armitage\\armitage_worker\Armitage_project\crawl_n_depth\Simplified_System\end_to_end\\cb_report.csv')
            #

    # return data


def check_aven(id_list):
    mycol = refer_collection()
    id_l = []
    aven_hq = []
    aven_link = []
    aven_ty = []
    df = pd.DataFrame()
    for each_id in id_list:
        is_yes = mycol.find({"_id": each_id})
        data = [d for d in is_yes]
        id_l.append(each_id)
        'website_link_aven'
        'Company_Type:_aven'
        'address_aven'
        if ('website_link_aven' in data[0].keys()):
            aven_link.append(data[0]['website_link_aven'])
        else:
            aven_link.append('No data')

        if ('Company_Type:_aven' in data[0].keys()):
            aven_ty.append(data[0]['Company_Type:_aven'])
        else:
            aven_ty.append('No data')

        if ('address_aven' in data[0].keys()):
            aven_hq.append(data[0]['address_aven'])
        else:
            aven_hq.append('No data')



    df['id'] = id_l
    df['avention_link'] = aven_link
    df['avention_address'] = aven_hq
    df['avention_type'] = aven_ty

    df.to_csv(
        'C:\Project_files\\armitage\\armitage_worker\Armitage_project\crawl_n_depth\Simplified_System\end_to_end\\aven_report.csv')

# check_cb(profiles_list)
check_aven(profiles_list)
