
from bson import ObjectId
import sys
from os.path import dirname as up



three_up = up(up(up(__file__)))

sys.path.insert(0, three_up)
# sys.path.insert(0,'C:/Project_files/Armitage_project_v1/crawl_n_depth')
# print(three_up)
# print(sys.path)
from fake_useragent import UserAgent
from selenium import webdriver
from datetime import datetime
from multiprocessing import Process
from Simplified_System.Initial_Crawling.main import search_a_company,search_a_query,search_a_company_alpha,update_a_company
from Simplified_System.Deep_Crawling.main import deep_crawl,add_to_deep_crawling_queue,run_crawlers_via_queue_chain
from Simplified_System.Database.db_connect import refer_collection,refer_query_col,simplified_export,simplified_export_via_queue,add_to_simplified_export_queue,refer_projects_col,simplified_export_with_sources_and_confidence
from Simplified_System.Feature_Extraction.main import extract_features,extract_features_via_queue_chain
from Classification.predict_class import predict_class_tags,predict_class_tags_via_queue
from Simplified_System.web_profile_data_crawler.scrape_dnb import get_dnb_data,add_to_dnb_queue,get_dnb_data_via_queue
from Simplified_System.web_profile_data_crawler.scrape_oc import get_oc_data,add_to_oc_queue,get_oc_data_via_queue
from Simplified_System.web_profile_data_crawler.scrape_crunchbase import get_cb_data,add_to_cb_queue,get_cb_data_via_queue
from Simplified_System.web_profile_data_crawler.avention_scraper import get_aven_data,add_to_avention_queue,get_aven_data_via_queue
# from Simplified_System.linkedin_data_crawler.linkedin_crawling import get_li_data
from Simplified_System.google_for_data.address_extraction.address_from_google import get_ad_from_google,add_to_ad_queue,get_ad_from_google_via_queue
from Simplified_System.google_for_data.contacts_from_google.get_contacts_google import get_cp_from_google,add_to_cp_queue,get_cp_from_google_via_queue
from Simplified_System.google_for_data.scrape_owler_data.owler_extractor import get_qa_from_google,add_to_qa_queue,get_qa_from_google_via_queue
from Simplified_System.google_for_data.get_li_employees.scrape_linkedin_employees import get_li_emp,add_to_li_cp_queue,get_li_emp_via_queue
from Simplified_System.google_for_data.phone_number_extraction.get_tp_num import get_tp_from_google,add_to_tp_queue,get_tp_from_google_via_queue
from Simplified_System.end_to_end.create_projects import get_projects_via_queue


def get_entries_project(project_id):
    completed_count = []
    incomplete_count = 0
    incompletes = []
    problems = []
    all_entires = []
    profile_col = refer_collection()
    projects_col= refer_projects_col()
    query_collection = refer_query_col()
    proj_data_entry = projects_col.find({"_id": project_id})
    print('proj',proj_data_entry)
    proj_data = [i for i in proj_data_entry]
    print('data',len(proj_data))
    proj_attribute_keys = list(proj_data[-1].keys())
    if ('associated_queries' in proj_attribute_keys):
        associated_queries = proj_data[-1]['associated_queries']
        for each_query in associated_queries:
            query_data_entry = query_collection.find({"_id": ObjectId(each_query)})
            query_data = [i for i in query_data_entry]
            print([query_data[0]['search_query'],query_data[0]['state'],query_data[0]['_id']])
            query_attribute_keys = list(query_data[0].keys())
            if ('associated_entries' in query_attribute_keys):
                associated_entries = query_data[0]['associated_entries']
                # print('kk',associated_entries)
                obs_ids = [ObjectId(i) for i in associated_entries]


                for k in obs_ids:
                    try:
                        prof_data_entry = profile_col.find({"_id": k})
                        # print('proj', proj_data_entry)
                        prof_data = [i for i in prof_data_entry]
                        prof_attribute_keys = list(prof_data[0].keys())
                        if(prof_data[0]['ignore_flag']=='1'):continue
                        all_entires.extend([k])

                        if ('simplified_dump_state' in prof_attribute_keys):
                            if(prof_data[0]['simplified_dump_state']=='Completed'):
                                completed_count.append(k)
                            # else:print(prof_data[0]['simplified_dump_state'])
                            elif (prof_data[0]['simplified_dump_state'] == 'Incomplete'):
                                incomplete_count+= 1
                                incompletes.append(k)
                            else:
                                problems.append(k)
                        else:
                            problems.append(k)
                    except Exception:
                        print(k)
                        print('error')
                        ddt = {'_id': k,'ignore_flag': '1'}

                        profile_col.insert_one(ddt)
                        continue
                #
                # print(['completed',completed_count,'all',len(obs_ids),'incompleted',incomplete_count,incompletes,'prob',problems])
                # # filt = []
                # # for k in obs_ids:
                # #     if(k not in problems):
                # #         filt.append(k)
                # # print('filt',filt)
                # if(completed_count==len(obs_ids)):
                #     query_collection.update_one({'_id': ObjectId(each_query)}, {'$set': {'state': 'Completed'}})

                # return obs_ids

        print('completed_count',len(list(set(completed_count))))
        print('incomplete_count',incomplete_count)
        print('incompletes',list(set(incompletes)))
        print('problems',list(set(problems)))
        print('all',list(set(all_entires)))
        return {'incompletes':list(set(incompletes)),'problems':list(set(problems))}
        # all_entires = list(set(all_entires))m
        # return all_entires
    else:
        print("This project do not have any queries yet")
        return []


def repair_wanted_parts(entry_id_list):
    profile_col = refer_collection()
    for k in entry_id_list:
        print('*****************')
        prof_data_entry = profile_col.find({"_id": k})
        # print('proj', proj_data_entry)
        prof_data = [i for i in prof_data_entry]
        prof_attribute_keys = list(prof_data[0].keys())
        if('deep_crawling_state' in prof_attribute_keys):
            print('yes')
            if(prof_data[0]['deep_crawling_state']=='Completed'):
                print('deep_crawling_state_already_done')
            else:
                add_to_deep_crawling_queue([k])
        else:
            add_to_deep_crawling_queue([k])
        if ('feature_extraction_state' in prof_attribute_keys):
            if (prof_data[0]['feature_extraction_state'] == 'Completed'):
                print('feature_extraction_state_already_done')
            else:
                add_to_deep_crawling_queue([k])
        else:
            add_to_deep_crawling_queue([k])
        #
        if ('classification_state' in prof_attribute_keys):
            if (prof_data[0]['classification_state'] == 'Completed'):
                print('classification_state_already_done')
            else:
                add_to_deep_crawling_queue([k])
        else:
            add_to_deep_crawling_queue([k])

        if ('owler_qa_state' in prof_attribute_keys):
            if (prof_data[0]['owler_qa_state'] == 'Completed'):
                print('owler_qa_state_already_done')
            else:
                print("Adding to Owler QA extraction queue")
                add_to_qa_queue([k])
        else:
            print("Adding to Owler QA extraction queue")
            add_to_qa_queue([k])

        if ('google_cp_state' in prof_attribute_keys):
            if (prof_data[0]['google_cp_state'] == 'Completed'):
                print('google_cp_state_already_done')
            else:
                print("Adding to google contact person extraction queue")
                add_to_cp_queue([k])
        else:
            print("Adding to google contact person extraction queue")
            add_to_cp_queue([k])

        if ('oc_extraction_state' in prof_attribute_keys):
            if (prof_data[0]['oc_extraction_state'] == 'Completed'):
                print('oc_extraction_state_already_done')
            else:
                print("Adding to Opencorporates extraction queue")
                add_to_oc_queue([k])
        else:
            print("Adding to Opencorporates extraction queue")
            add_to_oc_queue([k])


        if ('google_address_state' in prof_attribute_keys):
            if (prof_data[0]['google_address_state'] == 'Completed'):
                print('google_address_state_already_done')
            else:
                print("Adding to google address extraction queue")
                add_to_ad_queue([k])
        else:
            print("Adding to google address extraction queue")
            add_to_ad_queue([k])

        if ('dnb_extraction_state' in prof_attribute_keys):
            if (prof_data[0]['dnb_extraction_state'] == 'Completed'):
                print('dnb_extraction_state_already_done')
            else:
                print("Adding to DNB extraction queue")
                add_to_dnb_queue([k])
        else:
            print("Adding to DNB extraction queue")
            add_to_dnb_queue([k])

        #
        if ('google_tp_state' in prof_attribute_keys):
            if (prof_data[0]['google_tp_state'] == 'Completed'):
                print('google_tp_state_already_done')
            else:
                print("Adding to google tp extraction queue")
                add_to_tp_queue([k])
        else:
            print("Adding to google tp extraction queue")
            add_to_tp_queue([k])
        #
        #
        if ('crunchbase_extraction_state' in prof_attribute_keys):
            if (prof_data[0]['crunchbase_extraction_state'] == 'Completed'):
                print('crunchbase_extraction_state_already_done')
            else:
                print("Adding to Crunchbase extraction queue")
                add_to_cb_queue([k])
        else:
            print("Adding to Crunchbase extraction queue")
            add_to_cb_queue([k])
        #
        #
        if ('li_cp_state' in prof_attribute_keys):
            if (prof_data[0]['li_cp_state'] == 'Completed'):
                print('li_cp_state_already_done')
            else:
                print("Adding to linkedin cp extraction queue")
                add_to_li_cp_queue([k])
        else:
            print("Adding to linkedin cp extraction queue")
            add_to_li_cp_queue([k])
        #
        #
        #
        #
        if ('simplified_dump_state' in prof_attribute_keys):
            if (prof_data[0]['simplified_dump_state'] == 'Completed'):
                print('simplified_dump_state already_done')
            else:
                print("Adding to simplified dump queue")
                add_to_simplified_export_queue([k])
        else:
            print("Adding to simplified dump queue")
            add_to_simplified_export_queue([k])


def repair_wanted_parts_updated(entry_id_list):
    profile_col = refer_collection()
    for k in entry_id_list:
        print('*****************')
        prof_data_entry = profile_col.find({"_id": k})
        print('proj', prof_data_entry)
        prof_data = [i for i in prof_data_entry]
        print(prof_data)
        prof_attribute_keys = list(prof_data[0].keys())

        if ('crunchbase_extraction_state' in prof_attribute_keys):
            if (prof_data[0]['crunchbase_extraction_state'] == 'Completed'):
                print('crunchbase_extraction_state_already_done')
                if ('deep_crawling_state' in prof_attribute_keys):
                    print('yes')
                    if (prof_data[0]['deep_crawling_state'] == 'Completed'):
                        print('deep_crawling_state_already_done')
                    else:
                        add_to_deep_crawling_queue([k])
                else:
                    add_to_deep_crawling_queue([k])
                if ('feature_extraction_state' in prof_attribute_keys):
                    if (prof_data[0]['feature_extraction_state'] == 'Completed'):
                        print('feature_extraction_state_already_done')
                    else:
                        add_to_deep_crawling_queue([k])
                else:
                    add_to_deep_crawling_queue([k])
                    #
                if ('classification_state' in prof_attribute_keys):
                    if (prof_data[0]['classification_state'] == 'Completed'):
                        print('classification_state_already_done')
                    else:
                        add_to_deep_crawling_queue([k])
                else:
                    add_to_deep_crawling_queue([k])

                if ('owler_qa_state' in prof_attribute_keys):
                    if (prof_data[0]['owler_qa_state'] == 'Completed'):
                        print('owler_qa_state_already_done')
                    else:
                        print("Adding to Owler QA extraction queue")
                        add_to_qa_queue([k])
                else:
                    print("Adding to Owler QA extraction queue")
                    add_to_qa_queue([k])

                if ('google_cp_state' in prof_attribute_keys):
                    if (prof_data[0]['google_cp_state'] == 'Completed'):
                        print('google_cp_state_already_done')
                    else:
                        print("Adding to google contact person extraction queue")
                        add_to_cp_queue([k])
                else:
                    print("Adding to google contact person extraction queue")
                    add_to_cp_queue([k])

                if ('oc_extraction_state' in prof_attribute_keys):
                    if (prof_data[0]['oc_extraction_state'] == 'Completed'):
                        print('oc_extraction_state_already_done')
                    else:
                        print("Adding to Opencorporates extraction queue")
                        add_to_oc_queue([k])
                else:
                    print("Adding to Opencorporates extraction queue")
                    add_to_oc_queue([k])

                if ('google_address_state' in prof_attribute_keys):
                    if (prof_data[0]['google_address_state'] == 'Completed'):
                        print('google_address_state_already_done')
                    else:
                        print("Adding to google address extraction queue")
                        add_to_ad_queue([k])
                else:
                    print("Adding to google address extraction queue")
                    add_to_ad_queue([k])

                if ('dnb_extraction_state' in prof_attribute_keys):
                    if (prof_data[0]['dnb_extraction_state'] == 'Completed'):
                        print('dnb_extraction_state_already_done')
                    else:
                        print("Adding to DNB extraction queue")
                        add_to_dnb_queue([k])
                else:
                    print("Adding to DNB extraction queue")
                    add_to_dnb_queue([k])

                    #
                if ('google_tp_state' in prof_attribute_keys):
                    if (prof_data[0]['google_tp_state'] == 'Completed'):
                        print('google_tp_state_already_done')
                    else:
                        print("Adding to google tp extraction queue")
                        add_to_tp_queue([k])
                else:
                    print("Adding to google tp extraction queue")
                    add_to_tp_queue([k])
                    #
                    #

                    #
                    #
                if ('li_cp_state' in prof_attribute_keys):
                    if (prof_data[0]['li_cp_state'] == 'Completed'):
                        print('li_cp_state_already_done')
                    else:
                        print("Adding to linkedin cp extraction queue")
                        add_to_li_cp_queue([k])
                else:
                    print("Adding to linkedin cp extraction queue")
                    add_to_li_cp_queue([k])
                    #
                    #
                    #
                    #
                if ('simplified_dump_state' in prof_attribute_keys):
                    if (prof_data[0]['simplified_dump_state'] == 'Completed'):
                        print('simplified_dump_state already_done')
                    else:
                        print("Adding to simplified dump queue")
                        add_to_simplified_export_queue([k])
                else:
                    print("Adding to simplified dump queue")
                    add_to_simplified_export_queue([k])


                if ('avention_extraction_state' in prof_attribute_keys):
                    if (prof_data[0]['avention_extraction_state'] == 'Completed'):
                        print('avention_extraction_state already_done')
                    else:
                        print("Adding to Avention dump queue")
                        add_to_avention_queue([k])
                else:
                    print("Adding to Avention extraction queue")
                    add_to_avention_queue([k])







            else:
                print("Adding to Crunchbase extraction queue")
                add_to_cb_queue([k])
        else:
            print("Adding to Crunchbase extraction queue")
            add_to_cb_queue([k])





def repair_profiles(entry_id_list):
    print("Adding to deep_crawling_chain(deep_crawling,feature_extraction,classification_model)")
    add_to_deep_crawling_queue(entry_id_list)
    print("Adding to Owler QA extraction queue")
    add_to_qa_queue(entry_id_list)
    print("Adding to google contact person extraction queue")
    add_to_cp_queue(entry_id_list)
    print("Adding to Opencorporates extraction queue")
    add_to_oc_queue(entry_id_list)
    print("Adding to google address extraction queue")
    add_to_ad_queue(entry_id_list)
    print("Adding to DNB extraction queue")
    add_to_dnb_queue(entry_id_list)
    print("Adding to google tp extraction queue")
    add_to_tp_queue(entry_id_list)

    print("Adding to Crunchbase extraction queue")
    add_to_cb_queue(entry_id_list)
    print("Adding to linkedin cp extraction queue")
    add_to_li_cp_queue(entry_id_list)
    print("Adding to simplified dump queue")
    add_to_simplified_export_queue(entry_id_list)


    print("Adding to Avention extraction queue")
    add_to_avention_queue(entry_id_list)
# repair_profiles([ObjectId('5fae23aeffaa7d52304bce06'), ObjectId('5fae25edffaa7d52304bce15'), ObjectId('5fae1f47ffaa7d52304bcdec'), ObjectId('5fae2588ffaa7d52304bce11'), ObjectId('5fae1e5cffaa7d52304bcde6'), ObjectId('5fae1a2cffaa7d52304bcdd4'), ObjectId('5fae19e2ffaa7d52304bcdd2'), ObjectId('5fae20d1ffaa7d52304bcdf3'), ObjectId('5fae23f7ffaa7d52304bce08'), ObjectId('5f7b064ccc367eae52280948'), ObjectId('5f7c8d77536aa6fa3903918b'), ObjectId('5fae1dbfffaa7d52304bcde3'), ObjectId('5f7a7dc6b01f5030d514b2de'), ObjectId('5fae21d4ffaa7d52304bcdfa'), ObjectId('5fae215effaa7d52304bcdf6'), ObjectId('5fae24d4ffaa7d52304bce0d'), ObjectId('5f7b3f4e999b5546e9a889b1'), ObjectId('5f7b0fd4c0092b71a2c6dab2'), ObjectId('5fae1c39ffaa7d52304bcddb'), ObjectId('5fae225affaa7d52304bcdfe'), ObjectId('5fae22ddffaa7d52304bce02'), ObjectId('5fae1bc2ffaa7d52304bcdd8'), ObjectId('5f7a5fa70a1b11a515b1e2ea'), ObjectId('5f7b0facc0092b71a2c6daaf'), ObjectId('5f769ffd087161005148ea94'), ObjectId('5f7a82fbb01f5030d514b300'), ObjectId('5fae228fffaa7d52304bce00'), ObjectId('5fae1e92ffaa7d52304bcde8'), ObjectId('5fae1b90ffaa7d52304bcdd6'), ObjectId('5fae25bcffaa7d52304bce13'), ObjectId('5f7a7b33b01f5030d514b2d0'), ObjectId('5fae2220ffaa7d52304bcdfc')])
# repair_profiles( [ObjectId('5f769a66087161005148ea76'), ObjectId('5f7a60150a1b11a515b1e2ed'), ObjectId('5f769859087161005148ea68'), ObjectId('5f7a63970a1b11a515b1e306'), ObjectId('5f7a61b50a1b11a515b1e2f7'), ObjectId('5f7a5e890a1b11a515b1e2e2'), ObjectId('5f7a61b50a1b11a515b1e2f7'), ObjectId('5f7b1031c0092b71a2c6dab8'), ObjectId('5f7b3ffd999b5546e9a889bc'), ObjectId('5f769a66087161005148ea76'), ObjectId('5f7a5e890a1b11a515b1e2e2'), ObjectId('5f7a60a40a1b11a515b1e2f0'), ObjectId('5f7a63970a1b11a515b1e306'), ObjectId('5fae2436ffaa7d52304bce0a'), ObjectId('5f7b4114999b5546e9a889d0'), ObjectId('5fae19a5ffaa7d52304bcdd0'), ObjectId('5f7b1151c0092b71a2c6dac9'), ObjectId('5f769859087161005148ea68'), ObjectId('5f7b41cd999b5546e9a889dc'), ObjectId('5f7b39994a8281a499ea953d'), ObjectId('5fb0c5bd3ed5000dbe3636bb'), ObjectId('5fb0c6633ed5000dbe3636be'), ObjectId('5fae19a5ffaa7d52304bcdd0')])

# to_rep = [ObjectId('5fae1c39ffaa7d52304bcddb'), ObjectId('5f7c8d77536aa6fa3903918b'), ObjectId('5fae225affaa7d52304bcdfe'), ObjectId('5fae215effaa7d52304bcdf6'), ObjectId('5fae228fffaa7d52304bce00'), ObjectId('5fae20d1ffaa7d52304bcdf3'), ObjectId('5fae25bcffaa7d52304bce13'), ObjectId('5fae1e92ffaa7d52304bcde8'), ObjectId('5fae1e5cffaa7d52304bcde6'), ObjectId('5f7b3f4e999b5546e9a889b1'), ObjectId('5fae1bc2ffaa7d52304bcdd8'), ObjectId('5f7a7dc6b01f5030d514b2de'), ObjectId('5fae19e2ffaa7d52304bcdd2'), ObjectId('5fae24d4ffaa7d52304bce0d'), ObjectId('5fae21d4ffaa7d52304bcdfa'), ObjectId('5fae25edffaa7d52304bce15'), ObjectId('5f7b064ccc367eae52280948'), ObjectId('5fae1dbfffaa7d52304bcde3'), ObjectId('5fae22ddffaa7d52304bce02'), ObjectId('5fae23f7ffaa7d52304bce08'), ObjectId('5f7b0fd4c0092b71a2c6dab2'), ObjectId('5f7a5fa70a1b11a515b1e2ea'), ObjectId('5fae1a2cffaa7d52304bcdd4'), ObjectId('5fae2588ffaa7d52304bce11'), ObjectId('5fae23aeffaa7d52304bce06'), ObjectId('5fae1f47ffaa7d52304bcdec'), ObjectId('5f7a7b33b01f5030d514b2d0'), ObjectId('5f769ffd087161005148ea94'), ObjectId('5f7b0facc0092b71a2c6daaf'), ObjectId('5fae2220ffaa7d52304bcdfc'), ObjectId('5fae1b90ffaa7d52304bcdd6'), ObjectId('5f7a82fbb01f5030d514b300')]
to_l = [ObjectId('5fae1a2cffaa7d52304bcdd4'), ObjectId('5fae22ddffaa7d52304bce02'), ObjectId('5fae2220ffaa7d52304bcdfc'), ObjectId('5fae1bc2ffaa7d52304bcdd8'), ObjectId('5f7a5fa70a1b11a515b1e2ea'), ObjectId('5fae23aeffaa7d52304bce06'), ObjectId('5fae1e5cffaa7d52304bcde6'), ObjectId('5fae20d1ffaa7d52304bcdf3'), ObjectId('5f7b064ccc367eae52280948'), ObjectId('5fae25bcffaa7d52304bce13'), ObjectId('5f7b0facc0092b71a2c6daaf'), ObjectId('5f7a7dc6b01f5030d514b2de'), ObjectId('5f7b0fd4c0092b71a2c6dab2'), ObjectId('5f7a82fbb01f5030d514b300'), ObjectId('5fae21d4ffaa7d52304bcdfa'), ObjectId('5f7a7b33b01f5030d514b2d0'), ObjectId('5fae2588ffaa7d52304bce11'), ObjectId('5fae1b90ffaa7d52304bcdd6'), ObjectId('5fae1f47ffaa7d52304bcdec'), ObjectId('5fae1e92ffaa7d52304bcde8'), ObjectId('5f769ffd087161005148ea94'), ObjectId('5fae225affaa7d52304bcdfe'), ObjectId('5fae19e2ffaa7d52304bcdd2'), ObjectId('5f7b3f4e999b5546e9a889b1'), ObjectId('5fae215effaa7d52304bcdf6'), ObjectId('5fae228fffaa7d52304bce00'), ObjectId('5fae23f7ffaa7d52304bce08'), ObjectId('5fae25edffaa7d52304bce15'), ObjectId('5fae1dbfffaa7d52304bcde3'), ObjectId('5fae24d4ffaa7d52304bce0d'), ObjectId('5f7c8d77536aa6fa3903918b')]
tt = [ObjectId('5fd350da6a3da8afb04a94d1'), ObjectId('5f7b1412c0092b71a2c6daf1'), ObjectId('5fd34de66a3da8afb04a94c3'), ObjectId('5fd34f946a3da8afb04a94cb'), ObjectId('5fd34a026a3da8afb04a94b2'), ObjectId('5fd359796a3da8afb04a9501'), ObjectId('5f769b49087161005148ea7d'), ObjectId('5fd34e696a3da8afb04a94c6'), ObjectId('5fd3508d6a3da8afb04a94cf'), ObjectId('5fd355756a3da8afb04a94eb'), ObjectId('5fd34be86a3da8afb04a94ba'), ObjectId('5fd354126a3da8afb04a94e4'), ObjectId('5f7a8390b01f5030d514b304'), ObjectId('5f7c8a1d536aa6fa3903916a'), ObjectId('5fd358ac6a3da8afb04a94fd'), ObjectId('5fd34b536a3da8afb04a94b7'), ObjectId('5fd355ce6a3da8afb04a94ee'), ObjectId('5fd357fd6a3da8afb04a94f8'), ObjectId('5fd358746a3da8afb04a94fb')]

# repair_wanted_parts(tt)
# repair_profiles(tt)

def repair_projects_wanted_parts(project_id_list):
    for each_id in project_id_list:
        out_dict = get_entries_project(each_id)
        problematic_profiles = out_dict['problems']
        repair_wanted_parts_updated(problematic_profiles)

# 6094f13f09f4bbe84fdec9c2
# repair_projects_wanted_parts([ObjectId('60e5272db2a8cfb5818ad0d7')])
# get_entries_project(ObjectId('60795ce143d20d5336c52abe'))
# repair_wanted_parts_updated([ObjectId('607b594e74b7ff6a8cea112a'), ObjectId('607c2cd974b7ff6a8cea1976'), ObjectId('607c2d2e74b7ff6a8cea197a'), ObjectId('607c2f1974b7ff6a8cea1990'), ObjectId('607c310774b7ff6a8cea19a1'), ObjectId('607bf1aa74b7ff6a8cea1766'), ObjectId('607c2a3e74b7ff6a8cea1960'),ObjectId('607b56e274b7ff6a8cea110d'), ObjectId('607b286374b7ff6a8cea0ebe'), ObjectId('60421339a63926c1684515b4'), ObjectId('602f9b2c7ba8308c59e0f519'), ObjectId('607aafe38158085fe9be350f'), ObjectId('604332fcdbc71f46487e3c4e'), ObjectId('607afdee74b7ff6a8cea0ccc')])
# repair_wanted_parts_updated([ObjectId('60b9b7341626f0a10618cd7b')])
# 60e5272db2a8cfb5818ad0d7