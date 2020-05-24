import sys
import threading
import time

from bson import ObjectId
#fix this path variable when using in another machine
sys.path.insert(0, 'F:\Armitage_project\crawl_n_depth\\')
from fake_useragent import UserAgent
from selenium import webdriver
from datetime import datetime
from Simplified_System.Initial_Crawling.main import search_a_company,search_a_query,search_a_company_alpha
from Simplified_System.Deep_Crawling.main import deep_crawl
from Simplified_System.Database.db_connect import refer_collection,export_profiles,refer_query_col
from Simplified_System.Feature_Extraction.main import extract_features
from Simplified_System.Extract_contact_persons.main import extract_contact_persons
from Classification.predict_class import predict_class_tags
from Simplified_System.web_profile_data_crawler.scrape_dnb import get_dnb_data
from Simplified_System.web_profile_data_crawler.scrape_oc import get_oc_data
from Simplified_System.linkedin_data_crawler.linkedin_crawling import get_li_data
from Simplified_System.address_extraction.address_from_google import get_ad_from_google
from Simplified_System.contacts_from_google.get_contacts_google import get_cp_from_google
from Simplified_System.phone_number_extraction.get_tp_num import get_tp_from_google
# # from crawl_n_depth.Simplified_System.Deep_Crawling.main import deep_crawl

# from Feature_Extraction.main import extract_features

# from crawl_n_depth.spiders.n_crawler import run_crawlers_m
# sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
# from crawl_n_depth.crawl_n_depth.spiders.n_crawler import run_crawlers_m
# from crawl_n_depth.spiders.n_crawler import run_crawlers_m


# sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
# from crawl_n_depth.spiders.n_crawler import run_crawlers_m
#
mycol = refer_collection()
#
def execute_for_a_company(comp_name):
    print("Searching a company")
    dateTimeObj = datetime.now()
    query_collection = refer_query_col()
    data_q = {'started_time_stamp': dateTimeObj, 'search_query': comp_name}
    record_entry = query_collection.insert_one(data_q)
    print("Started on", dateTimeObj)
    started = time.time()
    print("***Initial Crawling Phrase***")
    entry_id = search_a_company(comp_name,mycol,record_entry.inserted_id)
    if(entry_id==None):
        print("Initial crawling incomple..pipeline exits.try again")
    else:
        print("entry id received ",entry_id)
        print("***Deep Crawling Phrase***")
        deep_crawl([entry_id],3,100)
        print("Deep crawling completed and record extended with crawled_links,header_text,paragraph_text,social_media_links,telephone numbers,emails,addresses")
        print("***Feature Extraction Phrase***")
        extract_features([entry_id])
        print("***Contact Person Extraction Phrase***")
        extract_contact_persons([entry_id],'comp')
        print(("***Predict the company type***"))
        predict_class_tags([entry_id])
        print(("***Extract linkedin profile data***"))
        get_li_data([entry_id])
        print(("***Extract opencorporates profile data***"))
        get_oc_data([entry_id])
        print(("***Extract dnb profile data***"))
        get_dnb_data([entry_id])
        print(("***Dumping the results***"))
        export_profiles([entry_id],record_entry.inserted_id)
        ended = time.time()
        duration = ended - started
        dateTimeObj_e = datetime.now()
        completion_data = {'completed_time_stamp': dateTimeObj_e,'elapsed_time': duration}
        print(completion_data)
        query_collection.update_one({'_id': record_entry.inserted_id},
                         {'$set': completion_data})
        print("Pipeline execution completed, elapsed time:", duration)

    # entry_id = search_a_company(comp_name, mycol)
    # print("entry id received ", entry_id)

def execute_for_a_company_alpha(comp_name,c_name):
    print("Searching a company")
    dateTimeObj = datetime.now()
    query_collection = refer_query_col()
    data_q = {'started_time_stamp': dateTimeObj, 'search_query': comp_name}
    record_entry = query_collection.insert_one(data_q)
    print("Started on", dateTimeObj)
    started = time.time()
    print("***Initial Crawling Phrase***")
    entry_id = search_a_company_alpha(comp_name,mycol,record_entry.inserted_id,c_name)
    if(entry_id==None):
        for i in range(3):
            print("Initial crawling incomple..retrying",i)
            entry_id = search_a_company_alpha(comp_name, mycol, record_entry.inserted_id, c_name)
            time.sleep(5)
            if (entry_id != None):break
    if (entry_id == None):
        print("Initial crawling incomple..retrying unsuccessful")
    else:
        print("entry id received ",entry_id)
        print("***Deep Crawling Phrase***")
        deep_crawl([entry_id],3,70)
        print("Deep crawling completed and record extended with crawled_links,header_text,paragraph_text,social_media_links,telephone numbers,emails,addresses")
        print("***Feature Extraction Phrase***")
        extract_features([entry_id])
        print("***Contact Person Extraction Phrase***")
        extract_contact_persons([entry_id],'query')
        print(("***Predict the company type***"))
        predict_class_tags([entry_id])
        print(("***Extract linkedin profile data***"))
        get_li_data([entry_id])
        print(("***Extract opencorporates profile data***"))
        get_oc_data([entry_id])
        print(("***Extract dnb profile data***"))
        get_dnb_data([entry_id])
        print(("***Dumping the results***"))
        export_profiles([entry_id],record_entry.inserted_id)
        ended = time.time()
        duration = ended - started
        dateTimeObj_e = datetime.now()
        completion_data = {'completed_time_stamp': dateTimeObj_e,'elapsed_time': duration}
        print(completion_data)
        query_collection.update_one({'_id': record_entry.inserted_id},
                         {'$set': completion_data})
        print("Pipeline execution completed, elapsed time:", duration)

    # entry_id = search_a_company(comp_name, mycol)
    # print("entry id received ", entry_id)


def execute_for_a_query(query):
    print("Searching a query")
    dateTimeObj = datetime.now()
    query_collection = refer_query_col()
    data_q = {'started_time_stamp':dateTimeObj, 'search_query':query}
    record_entry = query_collection.insert_one(data_q)
    print("Started on",dateTimeObj)
    started = time.time()
    print("***Initial Crawling Phrase***")
    entry_id_list = search_a_query(query,10, mycol,record_entry.inserted_id)
    if(entry_id_list==None):
        for i in range(3):
            print("Initial crawling incomplete..retrying",i)
            entry_id_list = search_a_query(query, 10, mycol, record_entry.inserted_id)
            time.sleep(5)
            if(entry_id_list!=None):break
    if (entry_id_list == None):
        print("Initial crawling incomplete..retrying unsuccessful")

    else:
        print("entry ids received ", entry_id_list)
        print("***Deep Crawling Phrase***")
        deep_crawl(entry_id_list, 3, 70)
        print(
            "Deep crawling completed and record extended with crawled_links,header_text,paragraph_text,social_media_links,telephone numbers,emails,addresses")
        print("***Feature Extraction Phrase***")
        print("details for retrying,entry_id_list,query_id,started_time",[entry_id_list,record_entry.inserted_id,started])
        extract_features(entry_id_list)
        print("***Contact Person Extraction Phrase***")
        print("details for retrying,entry_id_list,query_id,started_time",
              [entry_id_list, record_entry.inserted_id, started])
        extract_contact_persons(entry_id_list, 'query')
        print(("***Predicting the company type***"))
        print("details for retrying,entry_id_list,query_id,started_time",
              [entry_id_list, record_entry.inserted_id, started])

        predict_class_tags(entry_id_list)
        print(("***Extract linkedin profile data***"))
        print("details for retrying,entry_id_list,query_id,started_time",
              [entry_id_list, record_entry.inserted_id, started])

        get_li_data(entry_id_list)
        print(("***Extract opencorporates profile data***"))
        print("details for retrying,entry_id_list,query_id,started_time",
              [entry_id_list, record_entry.inserted_id, started])

        get_oc_data(entry_id_list)
        print(("***Extract dnb profile data***"))
        print("details for retrying,entry_id_list,query_id,started_time",
              [entry_id_list, record_entry.inserted_id, started])

        get_dnb_data(entry_id_list)
        print(("***Dumping the results***"))
        print("details for retrying,entry_id_list,query_id,started_time",
              [entry_id_list, record_entry.inserted_id, started])

        export_profiles(entry_id_list,record_entry.inserted_id)
        ended = time.time()
        dateTimeObj_e = datetime.now()
        duration = ended - started
        completion_data = {'completed_time_stamp': dateTimeObj_e, 'elapsed_time': duration}
        query_collection.update_one({'_id': record_entry.inserted_id},
                         {'$set': completion_data})
        print("Pipeline execution completed, elapsed time:",duration)

def retry_for_query(details):
    entry_id_list = details[0]
    query_id = details[1]
    started = details[2]
    query_collection = refer_query_col()
    print("entry ids received ", entry_id_list)
    # print("***Deep Crawling Phrase***")
    # deep_crawl(entry_id_list, 3, 70)
    # print(
    #     "Deep crawling completed and record extended with crawled_links,header_text,paragraph_text,social_media_links,telephone numbers,emails,addresses")
    # print("***Feature Extraction Phrase***")
    # print("details for retrying,entry_id_list,query_id,started_time",
    #       [entry_id_list, query_id, started])
    # extract_features(entry_id_list)
    # print("***Contact Person Extraction Phrase***")
    # print("details for retrying,entry_id_list,query_id,started_time",
    #       [entry_id_list, query_id, started])
    # extract_contact_persons(entry_id_list, 'query')
    # print(("***Predicting the company type***"))
    # print("details for retrying,entry_id_list,query_id,started_time",
    #       [entry_id_list, query_id, started])

    # predict_class_tags(entry_id_list)
    # print(("***Extract linkedin profile data***"))
    # print("details for retrying,entry_id_list,query_id,started_time",
    #       [entry_id_list, query_id, started])
    #
    # # get_li_data(entry_id_list)
    # print(("***Extract opencorporates profile data***"))
    # print("details for retrying,entry_id_list,query_id,started_time",
    #       [entry_id_list, query_id, started])

    # get_oc_data(entry_id_list)
    # print(("***Extract dnb profile data***"))
    # print("details for retrying,entry_id_list,query_id,started_time",
    #       [entry_id_list, query_id, started])

    # get_dnb_data(entry_id_list)
    print(("***Dumping the results***"))
    print("details for retrying,entry_id_list,query_id,started_time",
          [entry_id_list, query_id, started])

    export_profiles(entry_id_list, query_id)
    ended = time.time()
    dateTimeObj_e = datetime.now()
    duration = ended - started
    completion_data = {'completed_time_stamp': dateTimeObj_e, 'elapsed_time': duration}
    query_collection.update_one({'_id': query_id},
                                {'$set': completion_data})
    print("Pipeline execution completed, elapsed time:", duration)
# queries = ['Medical equipment repair','Digital advertisement and marketing analytics services company',
#            'In-home care software and services for NDIS / CDC',
#            'Risk and Compliance management software','Enterprise asset management software',
#             'Asset & fleet management software','Education software and services',
#             'specialist educators for video games developers','Software to manage relief teachers',
#             'Veterinary diagnostics','Medical equipment repair']

queries = ['In-home care software and services for NDIS / CDC Australia OR New Zealand cr:au'
,'Risk and Compliance management software Australia New Zealand'
,'Enterprise asset management software Australia OR New Zealand'
,'Asset and fleet management software Australia OR New Zealand'
,'Education software and services Australia OR New Zealand'
,'Specialist educators for video games developers software, animation, education, developers, game design, training provider Australia OR New Zealand'
,'Specialist content and material B2B specialist content Australia OR New Zealand'
,'Software to manage relief teachers Australia OR New Zealand'
,'Service/consumables provider for stable/legacy equipment Australia OR New Zealand'
,'Digital advertisement and marketing analytics Australia OR New Zealand'
,'Veterinary diagnostics supplier into veterinary hospitals Australia OR New Zealand'
,'Medical equipment repair and maintenance service providers high-use surgical equipment Australia OR New Zealand']

# queries = []
# import csv
# with open('green.csv', 'r') as file:
#     reader = csv.reader(file)
#     for row in reader:
#         queries.append([row[0],row[1]])
        # print(row[0],row[5])
# print(queries)
# queries = [['2and2', 'www.2and2.com.au'], ['Answers Portals', 'https://www.answersportals.com/'], ['arludo', 'https://arludo.com/'], ['Assignment Help Services', 'www.assignmenthelpservices.com/'], ['Atomi', 'https://getatomi.com/gb'], ['School App Solution', 'www.schoolappsolution.com.au'], ['Australian assignments help', 'www.australianassignmentshelp.com/'], ['Australian Help', 'australianhelp.com/'], ['Beauty Courses Online', 'www.beautycoursesonline.com/'], ['Brain Pump', 'brainpump.net/'], ['Careercake', 'www.careercake.com/'], ['Central Innovation Pty Ltd.', 'centralinnovation.com.au/'], ['C-Learning Pty', 'www.c-learning.com.au/'], ['Complier Enterprise', 'www.complierenterprise.com/'], ['Computers Now', 'www.compnow.com.au'], ['Convincely', 'www.convincely.com'], ['CourseLink', 'www.courselink.com.au'], ['Courses Direct', 'www.coursesdirect.com.au'], ['Cuberider', 'www.cuberider.com/'], ['Currency Select', 'www.currencyselect.com'], ['Devika', 'devika.com/'], ['Dienst Consulting', 'dienstconsulting.com/'], ['Digiskool', 'digiskool.co.ke/'], ['Digistorm', 'www.digistorm.com.au/'], ['Dynamic Web Training Pty Ltd.', 'www.dynamicwebtraining.com.au/'], ['EDflix', 'edflix.com.au/'], ['EdPotential', 'edpotential.com/'], ['edQuire', 'edquire.com'], ['Edval Timetables', 'www.edval.education'], ['eMarking Assistant', 'emarkingassistant.com/'], ['Equilibrium', 'www.equ.com.au/'], ['Essay Assignment Help', 'essayassignmenthelp.com.au/'], ['Fitzroy Academy', 'fitzroyacademy.com/'], ['Fluid Learning Courses Brisbane', 'www.fluidlearning.com.au'], ['Foundr Magazine', 'foundr.com/'], ['Funnelback', 'www.funnelback.com'], ['Navitas', 'www.navitas.com/'], ['gotoassignmenthelp', 'www.gotoassignmenthelp.com/assignment-help/mana...'], ['Governance Institute of Australia', 'www.governanceinstitute.com.au'], ['Gradchat', 'www.gradchat.com'], ['Gradconnection', 'www.gradconnection.com/'], ['Growing Up in New Zealand', 'www.growingup.co.nz/'], ['Guiix', 'www.guiix.com'], ['Heropa', 'www.heropa.com'], ['Human Edge Software Corp', 'www.humanedge.biz/'], ['Ignia', 'www.ignia.com.au/'], ['Inkerz', 'www.inkerz.com/'], ['JR Academy', 'jiangren.com.au'], ['Kindersay', 'www.kindersay.com'], ['LabTech Training', 'www.ltt.com.au'], ['Learnable', 'learnable.com/'], ['Literatu', 'www.literatu.com/'], ['LiveWebTutors', 'www.livewebtutors.com/'], ['Logitrain', 'www.logitrain.com.au'], ['Management Tutors', 'www.managementtutors.com/'], ['MathsRepublic', 'www.mathsrepublic.com.au'], ['Me3D', 'me3d.com.au/'], ['Medis Media', 'www.3dorganon.com/'], ['Milliped', 'millipede.com.au'], ['Minded', 'www.minded.co.nz'], ['Modern Star', 'www.modernstar.com/'], ['Motivational Speaker Adelaide', 'www.motivationalspeakeradelaide.com.au/'], ['My Assignment Services', 'www.myassignmentservices.com'], ['My Focusbook', 'myfocusbook.com.au'], ['My Genius Mind', 'www.mygeniusmind.com/'], ['MyAssignmentHelp.net', 'www.myassignmenthelp.net/'], ['myassignmenthelpaustralia', 'myassignmenthelpaustralia.com.au/'], ['MyndLyte', 'myndlyte.com/'], ['National Music Academy', 'nationalmusicacademy.com.au/'], ['Native Tongue', 'nativetongue.com'], ['NetSpot', 'www.netspot.com.au'], ['Newcomb Digital', 'www.newcomb.co.nz/'], ['Omnium', 'www.omnium.net.au'], ['OpenLearning', 'openlearning.com'], ['OpenSTEM Pty Ltd', 'openstem.com.au/'], ['Paddl Co.', 'www.paddl.com'], ['Pallas ALS', 'pallasals.com/'], ['ProgrammingHomeworkTutors', 'programminghomeworktutors.com/index.php'], ['Prosper Education', 'www.prospereducation.com/'], ['Real First Aid', 'www.realfirstaid.com.au'], ['Rockmelon', 'rockmelon.com/'], ['School of Music Online', 'schoolofmusiconline.com/'], ['Schoolzine', 'www.schoolzine.com/'], ['Secure Assignment Help', 'www.secureassignmenthelp.com/'], ['Skills Oz', 'www.skillsoz.com.au/'], ['Smart Kids Video', 'activebabiessmartkids.com.au'], ['SoccerBrain', 'www.soccerbrain.com/'], ['Code Like a Girl', 'codelikeagirl.org/'], ['Startup Melbourne', 'startupmelbourne.com'], ['Student Assignment Help', 'www.studentassignmenthelp.com/'], ['Supply Chain Sustainability School', 'www.supplychainschool.org.au'], ['Switch Inc.', 'www.switchinc.com.au'], ['TalkiPlay', 'www.talkiplay.com/'], ['TeacherTime', 'www.teachertime.com.au'], ['Negotiation Experts', 'www.negotiations.com'], ['The ICEHOUSE', 'www.theicehouse.co.nz/'], ['THE PULSE IQ', 'www.thepulseiq.com/'], ['Totara Learning Solutions', 'www.totaralms.com/'], ['Training Advisor', 'www.trainingadvisor.com.au'], ['Tutor On Demand', 'tutorondemand.com.au/'], ['Vericus', 'www.cadmus.io/'], ['Vidversity', 'vidversity.com/'], ['Workstar', 'www.workstar.com.au'], ['Compass Education', 'www.compass.education'], ['SEQTA', 'seqta.com.au'], ['Synergetic', 'www.synergetic.net.au'], ['Axcelerate', 'www.axcelerate.com.au'], ['Timetabling Solutions', 'www.timetabling.com.au'], ['Passtab', 'passtab.com'], ['Sentral', 'www.sentral.com.au'], ['Classe365', 'www.classe365.com'], ['Schoolbox', 'schoolbox.com.au'], ['Bibliotech', 'www.bibliotech.com.au'], ['Edumate', 'www.edumate.com.au'], ['Simon Schools', 'www.simonschools.net'], ['PC School', 'www.pcschool.net'], ['Specialist educators for video games developers\xa0 ', 'www.aie.edu.au/'], ['Specialist educators for video games developers\xa0 ', 'https://www.zenimax.com/'], ['Specialist content and material development ', 'www.joybusinessacademy.com'], ['Software to manage relief teachers ', 'Examples: https://www.classcover.com.au/'], ['Service/consumables provider for stable/legacy equipment ', 'http://www.smartech.com/'], ['Service/consumables provider for stable/legacy equipment ', 'http://www.pavt.com.au/'], ['Digital advertisement and marketing analytics ', 'https://integralads.com/\xa0'], ['Digital advertisement and marketing analytics ', 'https://www.quantium.com/'], ['Veterinary diagnostics', 'https://www.alvedia.com/'], ['Medical equipment repair and maintenance service providers ', 'www.flukebiomedical.com']]
# retried= time.time()
# retry_for_query([[ ObjectId('5eb8094955584ed5ddbe68fd')], ObjectId('5eb807c755584ed5ddbe68f0'), 1589118921.9288456])
#
# retry_for_query([[ObjectId('5eb807ec55584ed5ddbe68f1'), ObjectId('5eb8080355584ed5ddbe68f2'), ObjectId('5eb8081955584ed5ddbe68f3'), ObjectId('5eb8082f55584ed5ddbe68f4'), ObjectId('5eb8084555584ed5ddbe68f5'), ObjectId('5eb8085b55584ed5ddbe68f6'), ObjectId('5eb808a355584ed5ddbe68f7'), ObjectId('5eb808d955584ed5ddbe68f8'), ObjectId('5eb808f055584ed5ddbe68f9'), ObjectId('5eb8090655584ed5ddbe68fa'), ObjectId('5eb8091c55584ed5ddbe68fb'), ObjectId('5eb8093255584ed5ddbe68fc'), ObjectId('5eb8094955584ed5ddbe68fd')], ObjectId('5eb807c755584ed5ddbe68f0'), 1589118921.9288456])
# for i,k in enumerate(queries):
#     if i<249:continue
#     if i>260:break
# #     else:print(k)
ids_list = [ObjectId('5eb62e2a134cc6fb9536e93d'), ObjectId('5eb630147afe26eca4ba7bfa'), ObjectId('5eb6311c86662885174692de'), ObjectId('5eb631f1fac479799dedd1f8'), ObjectId('5eb6331597c8f5512179c4f1'), ObjectId('5eb634492802acb8c48e02aa'), ObjectId('5eb63539be65b70e5af0c7a9'), ObjectId('5eb6363894bd0b097f9c2734'), ObjectId('5eb6378b772150870b5c8d27'), ObjectId('5eb639ee2c60aae411d1ae8b'), ObjectId('5eb63aff81de1c4846fd91ab'), ObjectId('5eb63c1e9c69232f6ed6edd8'), ObjectId('5eb63d1b9d2ec0b892c42dd5'), ObjectId('5eb63e1ee805d1cff3d80a25'), ObjectId('5eb63ee743b668cb27ef8137'), ObjectId('5eb640560732058562a400b3'), ObjectId('5eb646ce3b4442b4da91c057'), ObjectId('5eb6479687b6932b9e6de098'), ObjectId('5eb648bf6bc924ef46ab60da'), ObjectId('5eb64a8e96bdd2bbbb3287e5'), ObjectId('5eb64bc810a22fecd4eca987'), ObjectId('5eb64cfc8c94747a21f39855'), ObjectId('5eb64e13158973dfa9982019'), ObjectId('5eb64f4ea0549166c51ca057'), ObjectId('5eb650acab06d680d6990351'), ObjectId('5eb651bc5fa088c453991725'), ObjectId('5eb652de55de509b4a9efaf4'), ObjectId('5eb65433af5bcc3efe32c504'), ObjectId('5eb6556c29c37695bc97bec4'), ObjectId('5eb6567909d0de1b6b708cf8'), ObjectId('5eb657e754ee9cbe1a7388c8'), ObjectId('5eb65942b46918d079adebe9'), ObjectId('5eb65a927cb5b3a1ff4ae362'), ObjectId('5eb65b645417d406270e7e63'), ObjectId('5eb65d83728ad01002b3a5f6'), ObjectId('5eb65f2cde8cab37cd68dffd'), ObjectId('5eb6603b6e69c6f2e1092cf8'), ObjectId('5eb661a6796445df9bfd756d'), ObjectId('5eb6631b245b7e033d0f92ed'), ObjectId('5eb66401b0e60a643fae0467'), ObjectId('5eb6651284c93e9e1b685024'), ObjectId('5eb66682dc99a524418da337'), ObjectId('5eb667a554cc6bc47dbfea44'), ObjectId('5eb6688cf9acda3a876322e4'), ObjectId('5eb669883e6dc49bd6f1540f'), ObjectId('5eb66a9b90f9dd06f1107866'), ObjectId('5eb66bb449a0728d932475bc'), ObjectId('5eb66ce4535d821544a14dee'), ObjectId('5eb66dabf3d5b58ef16a4c74'), ObjectId('5eb66e99e95b7d86f2518828'), ObjectId('5eb66fa738555190120005d2'), ObjectId('5eb670c2382a70cea3c90149'), ObjectId('5eb672382cf60f5b673dc845'), ObjectId('5eb6734f61272a1489607d7c'), ObjectId('5eb6746b3f8078c646a32068'), ObjectId('5eb675384beae11731a0ce35'), ObjectId('5eb676209d0d155a1c6530f3'), ObjectId('5eb6777b140e783b3524f4d9'), ObjectId('5eb6783b3dd775bea489b02d'), ObjectId('5eb67952c38498d75c86627f'), ObjectId('5eb67a4c109ddab70aec7b2d'), ObjectId('5eb67bc12373d9a910e8750f'), ObjectId('5eb67d3dd9818bcd44884d39'), ObjectId('5eb67e66b7921dcf1c2e6805'), ObjectId('5eb67fa821374c1c36ea76bb'), ObjectId('5eb680d98c70c48229cd26b6'), ObjectId('5eb6820dcc1fecfea5009f48'), ObjectId('5eb682ecd810c81378eb806d'), ObjectId('5eb68405b8f3f1e1b3084a52'), ObjectId('5eb6853a626f824ef428e315'), ObjectId('5eb688a782ee2ac4699515f2'), ObjectId('5eb689814e048265dd507dbc'), ObjectId('5eb68a771a268ae85ef97960'), ObjectId('5eb68b52298db2bd4cebdd0e'), ObjectId('5eb68c65501e64174bede873'), ObjectId('5eb68d458e708541f4671189'), ObjectId('5eb68e2fab2ce0451e2b4056'), ObjectId('5eb68edce0b5b75b05fba1e6'), ObjectId('5eb690038f7f6e26b6253fd5'), ObjectId('5eb690bd8d99ac316303ffb6'), ObjectId('5eb6918fa2e66438837c2d83'), ObjectId('5eb6925a31a5f94e1207b916'), ObjectId('5eb6944565d7b2466379f198'), ObjectId('5eb694f59c10ae1d407b7c2a'), ObjectId('5eb695e1ffe996bbe09292fe'), ObjectId('5eb696f6ef36438bec383b7e'), ObjectId('5eb697cac579ca076779cb0f'), ObjectId('5eb698a46de98c90f95a497d'), ObjectId('5eb699a671806057e76f0141'), ObjectId('5eb69a7d5587c492135fd56c'), ObjectId('5eb69b6fc6cad85bd913e12a'), ObjectId('5eb69c52d1ecab806f2beead'), ObjectId('5eb69cefc81bdf1aac4bf6a1'), ObjectId('5eb69e087e9ea4385e20beed'), ObjectId('5eb69f48a04ce33b509b4895'), ObjectId('5eb6a058cd265d6ef2ee766f'), ObjectId('5eb6a12f7ef80a97c531cc67'), ObjectId('5eb6a21fe632eaf0b1d593db'), ObjectId('5eb6a63fc0820e4534126e94'), ObjectId('5eb6a72dfc5d1c47d4ca9cd1'), ObjectId('5eb6a8462d272649f7b4df95'), ObjectId('5eb6a930b440ebf60d42d6c2'), ObjectId('5eb6aa15b5b4db2c7393254c'), ObjectId('5eb6ab260aef4a583d77118f'), ObjectId('5eb6ac1bfff106a6f58c42e7'), ObjectId('5eb6ad1662db4e6c180a378b'), ObjectId('5eb6ae390bdb0b194f41f9b3'), ObjectId('5eb6af2a6012ca09c1728130'), ObjectId('5eb6afc4e15b344d1a3aafa0'), ObjectId('5eb6b19b1c6e630676c62445'), ObjectId('5eb6b2a5a9211572420260e9'), ObjectId('5eb6b38eeb5e21b75a0d7cdb'), ObjectId('5eb6b45f4dab807be8d7a28a'), ObjectId('5eb6b53fd8471918b43146b7'), ObjectId('5eb6b61fabf00d5fdb2d05a3'), ObjectId('5eb6b71e5cd9b7b54c7d9961'), ObjectId('5eb6b9158f232307ce0bdc13'), ObjectId('5eb6b9dbb8b6b03010c4dcc6'), ObjectId('5eb6bad32c05d6f34cf32652'), ObjectId('5eb6bbbee2f17c3f3238cec8'), ObjectId('5eb6bca1b68e7672cd0ef210'), ObjectId('5eb6bdb1e7b6cc4614eb0edb'), ObjectId('5eb6beca47492aa1e0553de4'), ObjectId('5eb6bfc707fd60d7d77844de'), ObjectId('5eb7023ba86cec7b42163608'), ObjectId('5eb70254a86cec7b42163609'), ObjectId('5eb7026aa86cec7b4216360a'), ObjectId('5eb70280a86cec7b4216360b'), ObjectId('5eb70296a86cec7b4216360c'), ObjectId('5eb702aca86cec7b4216360d'), ObjectId('5eb702c2a86cec7b4216360e'), ObjectId('5eb702d9a86cec7b4216360f'), ObjectId('5eb702efa86cec7b42163610'), ObjectId('5eb70305a86cec7b42163611'), ObjectId('5eb7031ca86cec7b42163612'), ObjectId('5eb70333a86cec7b42163613'), ObjectId('5eb70349a86cec7b42163614'), ObjectId('5eb70360a86cec7b42163615'), ObjectId('5eb70376a86cec7b42163616'), ObjectId('5eb7038ca86cec7b42163617'), ObjectId('5eb703a2a86cec7b42163618'), ObjectId('5eb703b9a86cec7b42163619'), ObjectId('5eb714beb7411bc8fe5ec27b'), ObjectId('5eb714d5b7411bc8fe5ec27c'), ObjectId('5eb714ebb7411bc8fe5ec27d'), ObjectId('5eb71501b7411bc8fe5ec27e'), ObjectId('5eb71518b7411bc8fe5ec27f'), ObjectId('5eb71538b7411bc8fe5ec280'), ObjectId('5eb7154eb7411bc8fe5ec281'), ObjectId('5eb71564b7411bc8fe5ec282'), ObjectId('5eb7157ab7411bc8fe5ec283'), ObjectId('5eb71591b7411bc8fe5ec284'), ObjectId('5eb715a7b7411bc8fe5ec285'), ObjectId('5eb715bdb7411bc8fe5ec286'), ObjectId('5eb71606b7411bc8fe5ec287'), ObjectId('5eb7161db7411bc8fe5ec288'), ObjectId('5eb726fb2d11eabb9aa47f7f'), ObjectId('5eb7273c2d11eabb9aa47f81'), ObjectId('5eb727522d11eabb9aa47f82'), ObjectId('5eb727682d11eabb9aa47f83'), ObjectId('5eb7277f2d11eabb9aa47f84'), ObjectId('5eb76205646627514dad7813'), ObjectId('5eb7621e646627514dad7814'), ObjectId('5eb7624b646627514dad7816'), ObjectId('5eb76261646627514dad7817'), ObjectId('5eb76278646627514dad7818'), ObjectId('5eb7628f646627514dad7819'), ObjectId('5eb762a5646627514dad781a'), ObjectId('5eb762e6646627514dad781b'), ObjectId('5eb762fd646627514dad781c'), ObjectId('5eb76342646627514dad781f'), ObjectId('5eb7636f646627514dad7820'), ObjectId('5eb76385646627514dad7821'), ObjectId('5eb7639d646627514dad7822'), ObjectId('5eb7c4a49a65a3d7609e4fce'), ObjectId('5eb7c4bb9a65a3d7609e4fcf'), ObjectId('5eb7c4d29a65a3d7609e4fd0'), ObjectId('5eb7c4fd9a65a3d7609e4fd1'), ObjectId('5eb7c5149a65a3d7609e4fd2'), ObjectId('5eb7c55d9a65a3d7609e4fd3'), ObjectId('5eb7c5bb9a65a3d7609e4fd4'), ObjectId('5eb7c5d19a65a3d7609e4fd5'), ObjectId('5eb7c5e89a65a3d7609e4fd6'), ObjectId('5eb7d5d6f75273c9af329f72'), ObjectId('5eb7d5eef75273c9af329f73'), ObjectId('5eb7d604f75273c9af329f74'), ObjectId('5eb7d61bf75273c9af329f75'), ObjectId('5eb7d631f75273c9af329f76'), ObjectId('5eb7d652f75273c9af329f77'), ObjectId('5eb7d669f75273c9af329f78'), ObjectId('5eb7d689f75273c9af329f79'), ObjectId('5eb7d6a0f75273c9af329f7a'), ObjectId('5eb7d6b7f75273c9af329f7b'), ObjectId('5eb7d6cef75273c9af329f7c'), ObjectId('5eb7d6e4f75273c9af329f7d'), ObjectId('5eb7d6fbf75273c9af329f7e'), ObjectId('5eb7d72bf75273c9af329f7f'), ObjectId('5eb7d742f75273c9af329f80'), ObjectId('5eb7f2e0a97054c1c28ae403'), ObjectId('5eb7f2f8a97054c1c28ae404'), ObjectId('5eb7f323a97054c1c28ae405'), ObjectId('5eb7f338a97054c1c28ae406'), ObjectId('5eb7f34ea97054c1c28ae407'), ObjectId('5eb7f364a97054c1c28ae408'), ObjectId('5eb7f37aa97054c1c28ae409'), ObjectId('5eb7f3a7a97054c1c28ae40a'), ObjectId('5eb7f3bda97054c1c28ae40b'), ObjectId('5eb7f3d3a97054c1c28ae40c'), ObjectId('5eb7f3e9a97054c1c28ae40d'), ObjectId('5eb7f3ffa97054c1c28ae40e'), ObjectId('5eb7f415a97054c1c28ae40f'), ObjectId('5eb7f42aa97054c1c28ae410'), ObjectId('5eb7f441a97054c1c28ae411'), ObjectId('5eb7f461a97054c1c28ae412'), ObjectId('5eb807ec55584ed5ddbe68f1'), ObjectId('5eb8080355584ed5ddbe68f2'), ObjectId('5eb8081955584ed5ddbe68f3'), ObjectId('5eb8082f55584ed5ddbe68f4'), ObjectId('5eb8084555584ed5ddbe68f5'), ObjectId('5eb8085b55584ed5ddbe68f6'), ObjectId('5eb808a355584ed5ddbe68f7'), ObjectId('5eb808d955584ed5ddbe68f8'), ObjectId('5eb808f055584ed5ddbe68f9'), ObjectId('5eb8090655584ed5ddbe68fa'), ObjectId('5eb8091c55584ed5ddbe68fb'), ObjectId('5eb8093255584ed5ddbe68fc'), ObjectId('5eb8094955584ed5ddbe68fd'), ObjectId('5eb6644657dfd2c0b8ad6f9c'), ObjectId('5eb66630e46c2996611e7cc5'), ObjectId('5eb6670c8f3766d3901e7cc5'), ObjectId('5eb667a2f46d5b17e51e7cc5'), ObjectId('5eb66860dab176b3721e7cc5'), ObjectId('5eb6694f13214ceb901e7cc5'), ObjectId('5eb66a1c57d33385281e7cc5'), ObjectId('5eb66b0449715b12861e7cc5'), ObjectId('5eb66bf5c1cd3d67511e7cc5'), ObjectId('5eb66c7efae3969f0e1e7cc5'), ObjectId('5eb66d66b19f4175d41e7cc5'), ObjectId('5eb66e13afcaca79e81e7cc5'), ObjectId('5eb66f73241434c0231e7cc5'), ObjectId('5eb670975ce27f20651e7cc5'), ObjectId('5eb671403fb856baf01e7cc5'), ObjectId('5eb67202016c9eb49e1e7cc5'), ObjectId('5eb672855afc1f3bff1e7cc5'), ObjectId('5eb6732dc2f2cb21251e7cc5'), ObjectId('5eb674640480c494e21e7cc5'), ObjectId('5eb6753ed2085581291e7cc5'), ObjectId('5eb675ac19586b800c1e7cc5'), ObjectId('5eb6763b038d799aef1e7cc5'), ObjectId('5eb6776343946ae8fd1e7cc5'), ObjectId('5eb677f187e92c00051e7cc5'), ObjectId('5eb678eca5ef5a63181e7cc5'), ObjectId('5eb67989fc5079ac861e7cc5'), ObjectId('5eb67aa9307135b7481e7cc5'), ObjectId('5eb67c33c565dca3e61e7cc5'), ObjectId('5eb67d0c36a91550ff1e7cc5'), ObjectId('5eb67ddb4336d384b01e7cc5'), ObjectId('5eb67e90ae420cabcb1e7cc5'), ObjectId('5eb67f5ca8076cfd0a1e7cc5'), ObjectId('5eb68003bb68bcb7741e7cc5'), ObjectId('5eb6810f033af4b22b1e7cc5'), ObjectId('5eb681edb0a260b22a1e7cc5'), ObjectId('5eb682821dc3ebab081e7cc5'), ObjectId('5eb68355a25586c25d1e7cc5'), ObjectId('5eb6846e050a0737611e7cc5'), ObjectId('5eb6856e4c8a5b802f1e7cc5'), ObjectId('5eb6864268930af1f51e7cc5'), ObjectId('5eb686de941ea6f14b1e7cc5'), ObjectId('5eb688c6e8ba899a231e7cc5'), ObjectId('5eb689bf25abe779da1e7cc5'), ObjectId('5eb68afe1af2ab98d31e7cc5'), ObjectId('5eb68bf65c40e7d0d71e7cc5'), ObjectId('5eb68f5da4fd71f5821e7cc5'), ObjectId('5eb690478934691bf01e7cc5'), ObjectId('5eb6913eabf312822a1e7cc5'), ObjectId('5eb691e4f27c5211d21e7cc5'), ObjectId('5eb692b5bb6685adac1e7cc5'), ObjectId('5eb693d2d045d59f3b1e7cc5'), ObjectId('5eb6950c33fb947c391e7cc5'), ObjectId('5eb695e258473bd2511e7cc5'), ObjectId('5eb6968b400af16b271e7cc5'), ObjectId('5eb69733109de20b7e1e7cc5'), ObjectId('5eb697d1fb1caa3d7c1e7cc5'), ObjectId('5eb6988dc9615b33321e7cc5'), ObjectId('5eb69968d9785183931e7cc5'), ObjectId('5eb69a96a657bfc8991e7cc5'), ObjectId('5eb69c9f160e789d7e1e7cc5'), ObjectId('5eb69d5dd8d4ba89261e7cc5'), ObjectId('5eb69e1a46e5e5f33b1e7cc5'), ObjectId('5eb69f2843ef874fb81e7cc5'), ObjectId('5eb6a18ae6c27a5e961e7cc5'), ObjectId('5eb6a230795dc98ebd1e7cc5'), ObjectId('5eb6a2ee6c39588d0c1e7cc5'), ObjectId('5eb6a3d924946bdefc1e7cc5'), ObjectId('5eb6a504d1511c119a1e7cc5'), ObjectId('5eb6a5c37baf5cbfaa1e7cc5'), ObjectId('5eb6a670bc98e2e1471e7cc5'), ObjectId('5eb6a7b02266f527831e7cc5'), ObjectId('5eb6a895c2e3166bcc1e7cc5'), ObjectId('5eb6a9f32ea14a40531e7cc5'), ObjectId('5eb6aa92ee8178abc81e7cc5'), ObjectId('5eb6ab66c0c668b01d1e7cc5'), ObjectId('5eb6b0e61efe4c8c1f1e7cc5'), ObjectId('5eb6b168313d3030621e7cc5'), ObjectId('5eb6b201a201f790431e7cc5'), ObjectId('5eb6b361ce454282431e7cc5'), ObjectId('5eb6b3e04b08fc11b61e7cc5'), ObjectId('5eb6b49ef2b0c3149b1e7cc5'), ObjectId('5eb6b59f9ea7d290471e7cc5'), ObjectId('5eb6b675d1df7e04541e7cc5'), ObjectId('5eb6b75ef05682bd561e7cc5'), ObjectId('5eb6b8a9b0bfa077aa1e7cc5'), ObjectId('5eb6b928dd96b98b8b1e7cc5'), ObjectId('5eb6ba00d479014c311e7cc5'), ObjectId('5eb6bafd19a91c6bc11e7cc5'), ObjectId('5eb6bbe2c4e683d6001e7cc5'), ObjectId('5eb6bd08754af87d741e7cc5'), ObjectId('5eb6bd6f88582ed22e1e7cc5'), ObjectId('5eb6be6b9a04c870951e7cc5'), ObjectId('5eb6bf9531912db86d1e7cc5'), ObjectId('5eb6c13482dff544b31e7cc5'), ObjectId('5eb6c2265a296856911e7cc5'), ObjectId('5eb6c4f7fc8c7e73f71e7cc5'), ObjectId('5eb6c70a75e27bc9f01e7cc5'), ObjectId('5eb6c8e8f1c972d9d11e7cc5'), ObjectId('5eb6c9a73c6af847871e7cc5'), ObjectId('5eb6cad795a02f54c11e7cc5'), ObjectId('5eb6cbbb8e1ea19f721e7cc5'), ObjectId('5eb6cd0b76b872aac31e7cc5'), ObjectId('5eb6cf8d2afda4b75b1e7cc5'), ObjectId('5eb6d0b930966bc45d1e7cc5'), ObjectId('5eb6d180d6c5e588bc1e7cc5'), ObjectId('5eb6d2f157712c0e6b1e7cc5'), ObjectId('5eb6d3e51fd67335b41e7cc5'), ObjectId('5eb6d4b11fa223ec991e7cc5'), ObjectId('5eb6d573eeef09f4631e7cc5'), ObjectId('5eb6d5ed1ea282b3c71e7cc5'), ObjectId('5eb6d80ebb52c48b521e7cc5'), ObjectId('5eb6d92a12a10caf0b1e7cc5'), ObjectId('5eb6d9b2ad56eddd801e7cc5'), ObjectId('5eb6da581aea51c4141e7cc5'), ObjectId('5eb6db02d64b5ffaf01e7cc5'), ObjectId('5eb6dbee173c3e60211e7cc5'), ObjectId('5eb6dd0a8975e79a311e7cc5'), ObjectId('5eb6ddce3b3856712c1e7cc5'), ObjectId('5eb6de8bef8013ae3a1e7cc5'), ObjectId('5eb6dfa18548b41f1e1e7cc5'), ObjectId('5eb6e025a38f0a5bd51e7cc5'), ObjectId('5eb6e1bdc3b80c65f01e7cc5'), ObjectId('5eb6e2e985f544c0f31e7cc5'), ObjectId('5eb6e46fe2a11439211e7cc5'), ObjectId('5eb6e4e68944fb51261e7cc5'), ObjectId('5eb6e5f72810e4528c1e7cc5'), ObjectId('5eb6e71e229726a60d1e7cc5'), ObjectId('5eb6e833e6819157ab1e7cc5'), ObjectId('5eb6e92a73b223baa71e7cc5'), ObjectId('5eb6eb8eddadc0791a1e7cc5'), ObjectId('5eb6ecdfb8eac020ef1e7cc5'), ObjectId('5eb6ef069fd3d2700e1e7cc5'), ObjectId('5eb6f05e6cccb4ec201e7cc5'), ObjectId('5eb6f1abab044238231e7cc5'), ObjectId('5eb6f2785c17eeee301e7cc5'), ObjectId('5eb6f33f610110f7811e7cc5'), ObjectId('5eb6f5f338500f639d1e7cc5'), ObjectId('5eb6f75c547b2dc8a81e7cc5'), ObjectId('5eb6f86fa74f3f01391e7cc5'), ObjectId('5eb6faac13ef4ea5f11e7cc5'), ObjectId('5eb6fdc8c9af34d4321e7cc5'), ObjectId('5eb7015b64a4225c3e1e7cc5'), ObjectId('5eb701c9fd7dd6f0f81e7cc5'), ObjectId('5eb70303b9bd62c2d81e7cc5'), ObjectId('5eb707e40b3d32a9441e7cc5'), ObjectId('5eb70a317191684f471e7cc5'), ObjectId('5eb70b32d76dd257a81e7cc5'), ObjectId('5eb70c4eec6b83a56c1e7cc5'), ObjectId('5eb70d32fe79fe7ae11e7cc5'), ObjectId('5eb70dfc9b8c5669f61e7cc5'), ObjectId('5eb70e8d034df06da41e7cc5'), ObjectId('5eb70fe65ae110a83f1e7cc5'), ObjectId('5eb7108f8c31b21e521e7cc5'), ObjectId('5eb711cbd9698d895c1e7cc5'), ObjectId('5eb712ea41a21fd6dc1e7cc5'), ObjectId('5eb714466deb9085851e7cc5'), ObjectId('5eb714c5156d39e56e1e7cc5'), ObjectId('5eb7167ff888e8df4c1e7cc5'), ObjectId('5eb7172ad0c81b0d771e7cc5'), ObjectId('5eb718151826d970d21e7cc5'), ObjectId('5eb71938ccab1717f01e7cc5'), ObjectId('5eb71a2f30b005afe41e7cc5'), ObjectId('5eb71ad877b13eddbe1e7cc5'), ObjectId('5eb71ce921e8f2861f1e7cc5'), ObjectId('5eb71dca81f016c91a1e7cc5'), ObjectId('5eb71f0a7683d7d4101e7cc5'), ObjectId('5eb7203f4f2f7c0af81e7cc5'), ObjectId('5eb7213113ccf498df1e7cc5'), ObjectId('5eb7220bcc166c7e981e7cc5'), ObjectId('5eb72366ce65662b761e7cc5'), ObjectId('5eb7244a3dd3a2d7cc1e7cc5'), ObjectId('5eb72642b228878d531e7cc5'), ObjectId('5eb727cdaecb81e9bf1e7cc5'), ObjectId('5eb728f7fc797b3e091e7cc5'), ObjectId('5eb72aac0a755be3db1e7cc5'), ObjectId('5eb72bb61eabe2ed531e7cc5'), ObjectId('5eb72cf9e1fce67eae1e7cc5'), ObjectId('5eb730746bb3b692581e7cc5'), ObjectId('5eb730f0b6bdb8bbfc1e7cc5'), ObjectId('5eb731a0a3a39894761e7cc5'), ObjectId('5eb732a744e4da73881e7cc5'), ObjectId('5eb733f0abb68d26771e7cc5'), ObjectId('5eb734c35daa087a711e7cc5'), ObjectId('5eb735c8092b0431131e7cc5'), ObjectId('5eb73fde13df6f7b301e7cc5'), ObjectId('5eb7412226ae5213cf1e7cc5'), ObjectId('5eb7438bfa589ddb521e7cc5'), ObjectId('5eb74470a02a1a69941e7cc5'), ObjectId('5eb746a1e8e7f7509f1e7cc5'), ObjectId('5eb748526f5ea73b621e7cc5'), ObjectId('5eb74998ba43f388011e7cc5'), ObjectId('5eb74b1ffa73ce5db21e7cc5'), ObjectId('5eb74c79daf84fbe7c1e7cc5'), ObjectId('5eb74daa8e571dfa141e7cc5'), ObjectId('5eb7896b081724025f640206'), ObjectId('5eb7897f081724025f640207'), ObjectId('5eb78992081724025f640208'), ObjectId('5eb789a4081724025f640209'), ObjectId('5eb789b6081724025f64020a'), ObjectId('5eb789c9081724025f64020b'), ObjectId('5eb789dc081724025f64020c'), ObjectId('5eb789ee081724025f64020d'), ObjectId('5eb78a01081724025f64020e'), ObjectId('5eb78a13081724025f64020f'), ObjectId('5eb78a25081724025f640210'), ObjectId('5eb78a38081724025f640211'), ObjectId('5eb78a4a081724025f640212'), ObjectId('5eb78a5d081724025f640213'), ObjectId('5eb78a6f081724025f640214'), ObjectId('5eb78a82081724025f640215'), ObjectId('5eb78a95081724025f640216'), ObjectId('5eb78aa7081724025f640217'), ObjectId('5eb78aba081724025f640218'), ObjectId('5eb7aadc52f1054848f5583f'), ObjectId('5eb7ab0452f1054848f55840'), ObjectId('5eb7ab3552f1054848f55841'), ObjectId('5eb7ab4752f1054848f55842'), ObjectId('5eb7ab5a52f1054848f55843'), ObjectId('5eb7ab6d52f1054848f55844'), ObjectId('5eb7ab8052f1054848f55845'), ObjectId('5eb7ab9252f1054848f55846'), ObjectId('5eb7abc752f1054848f55847'), ObjectId('5eb7abda52f1054848f55848'), ObjectId('5eb7abec52f1054848f55849'), ObjectId('5eb7bf7b11ad0e77a8454c20'), ObjectId('5eb7bf9a11ad0e77a8454c21'), ObjectId('5eb7bfac11ad0e77a8454c22'), ObjectId('5eb7bfe611ad0e77a8454c23'), ObjectId('5eb7c00211ad0e77a8454c24'), ObjectId('5eb7c01411ad0e77a8454c25'), ObjectId('5eb7c02811ad0e77a8454c26'), ObjectId('5eb7c03b11ad0e77a8454c27'), ObjectId('5eb7c04d11ad0e77a8454c28'), ObjectId('5eb7c05f11ad0e77a8454c29'), ObjectId('5eb7c07c11ad0e77a8454c2a'), ObjectId('5eb7c08e11ad0e77a8454c2b'), ObjectId('5eb7c0a011ad0e77a8454c2c'), ObjectId('5eb808d148c8d5b70d0551c6'), ObjectId('5eb808e648c8d5b70d0551c7'), ObjectId('5eb8090248c8d5b70d0551c8'), ObjectId('5eb8091548c8d5b70d0551c9'), ObjectId('5eb8093b48c8d5b70d0551ca'), ObjectId('5eb8094d48c8d5b70d0551cb'), ObjectId('5eb8098248c8d5b70d0551cc'), ObjectId('5eb8099448c8d5b70d0551cd'), ObjectId('5eb809a648c8d5b70d0551ce'), ObjectId('5eb81d4d312f24e51eaa1661'), ObjectId('5eb81d6b312f24e51eaa1662'), ObjectId('5eb81d7d312f24e51eaa1663'), ObjectId('5eb81da1312f24e51eaa1664'), ObjectId('5eb81db3312f24e51eaa1665'), ObjectId('5eb81dc6312f24e51eaa1666'), ObjectId('5eb81dd8312f24e51eaa1667'), ObjectId('5eb81dea312f24e51eaa1668'), ObjectId('5eb81dfd312f24e51eaa1669'), ObjectId('5eb81e2a312f24e51eaa166a'), ObjectId('5eb81e3d312f24e51eaa166b'), ObjectId('5eb81e4f312f24e51eaa166c')]

print(ids_list.index(ObjectId('5eb69a7d5587c492135fd56c')))
def update_data(id_list):
    print("entry ids received ", id_list)
    # print("***Deep Crawling Phrase***")
    # #db collection changed in n_crawler.py
    # deep_crawl(id_list, 3, 70)
    # print(
    #     "Deep crawling completed and record extended with crawled_links,header_text,paragraph_text,social_media_links,telephone numbers,emails,addresses")
    # print("***Addresses from google***")
    # get_ad_from_google(id_list)
    # print("***Addresses extraction completed***")
    print("***cp from google***")
    get_cp_from_google(id_list)
    print("***cp extraction completed***")
    # print("***phone numbers from google***")
    # get_tp_from_google(id_list)
    # print("***tp extraction completed***")
update_data(ids_list[89:])
from multiprocessing import Process
# if __name__ == '__main__':
#     for i,k in enumerate(queries[0:1]):
#         print("iteration",i,k)
#         p = Process(target=execute_for_a_query, args=(k, ))
#         p.start()
#         p.join() # this blocks until the process terminates
# execute_for_a_company_alpha('2and2', 'www.2and2.com.au')
# execute_for_a_company('www.aie.edu.au')
# execute_for_a_company('Prime Q')
# execute_for_a_query('Digital advertisement and marketing analytics services company')
# execute_for_a_query('In-home care software and services for NDIS / CDC')
# execute_for_a_query('Risk and Compliance management software')
# execute_for_a_query('Enterprise asset management software')
# execute_for_a_query('Asset & fleet management software')
# execute_for_a_query('Education software and services')
# execute_for_a_query('pecialist educators for video games developers')
# execute_for_a_query('Specialist content and material development')
# execute_for_a_query('Software to manage relief teachers')
# execute_for_a_query('Veterinary diagnostics')
# execute_for_a_query('Medical equipment repair Australia')
