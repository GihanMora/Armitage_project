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
    entry_id_list = search_a_query(query,20, mycol,record_entry.inserted_id)
    if(entry_id_list==None):
        for i in range(3):
            print("Initial crawling incomplete..retrying",i)
            entry_id_list = search_a_query(query, 20, mycol, record_entry.inserted_id)
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

queries = ['In-home care software and services for NDIS / CDC Australia OR New Zealandk'
,'Risk and Compliance management software Australia New Zealandk'
,'Enterprise asset management software Australia OR New Zealandk'
,'Asset and fleet management software Australia OR New Zealandk'
,'Education software and services Australia OR New Zealandk'
,'Specialist educators for video games developers software, animation, education, developers, game design, training provider Australia OR New Zealandk'
,'Specialist content and material B2B specialist content Australia OR New Zealandk'
,'Software to manage relief teachers Australia OR New Zealandk'
,'Service/consumables provider for stable/legacy equipment Australia OR New Zealandk'
,'Digital advertisement and marketing analytics Australia OR New Zealandk'
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
retry_for_query([[ObjectId('5eb807ec55584ed5ddbe68f1'), ObjectId('5eb8080355584ed5ddbe68f2'), ObjectId('5eb8081955584ed5ddbe68f3'), ObjectId('5eb8082f55584ed5ddbe68f4'), ObjectId('5eb8084555584ed5ddbe68f5'), ObjectId('5eb8085b55584ed5ddbe68f6'), ObjectId('5eb808a355584ed5ddbe68f7'), ObjectId('5eb808d955584ed5ddbe68f8'), ObjectId('5eb808f055584ed5ddbe68f9'), ObjectId('5eb8090655584ed5ddbe68fa'), ObjectId('5eb8091c55584ed5ddbe68fb'), ObjectId('5eb8093255584ed5ddbe68fc'), ObjectId('5eb8094955584ed5ddbe68fd')], ObjectId('5eb807c755584ed5ddbe68f0'), 1589118921.9288456])
# for i,k in enumerate(queries):
#     if i<249:continue
#     if i>260:break
# #     else:print(k)



from multiprocessing import Process
# if __name__ == '__main__':
#     for i,k in enumerate(queries[10:11]):
#         print("iteration",i,k)
#         p = Process(target=execute_for_a_query, args=(k, ))
#         p.start()
#         p.join() # this blocks until the process terminates

# execute_for_a_company('Caltex Australia Ltd')
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
