#check mongo client string
#dump csv path
import ast
import os
import sys
import time
import urllib.parse
from datetime import datetime, timedelta
import gensim

import spacy

import pymongo
from azure.storage.queue import QueueClient
from bson import ObjectId
import csv

from os.path import dirname as up
three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)

from Simplified_System.evaluate_results.address_confidence import get_address_confidence,get_every_address_confidence
from Simplified_System.evaluate_results.cp_confidence import get_cp_confidence,get_every_cp_confidence
from Simplified_System.evaluate_results.hq_confidence import get_hq_confidence,get_every_hq_confidence
from Simplified_System.evaluate_results.tp_confidence import get_tp_confidence,get_every_tp_confidence
from Simplified_System.evaluate_results.row_accuracy import moderate_confidence

nz_prefixes = ['0320','0321','0322','0323','0324','0326','0327','0328','0330','0331','0332','0333','0334','0335','0336','0337','0338','03409','0341','0343','0344','0345','0346','0347','0348','0352','0354','0357','0361','0368','0369','0373','0375','0376','0378','0390','03927','0394','0395','0396','0397','0398','0423','0429','043','044','045','0480','0490','049','0627','0630','0632','0634','0635','0636','0637','0638','0675','0676','0683','0684','0685','0686','0687','0694','0695','0696','0697','0698','0730','0731','0732','0733','0734','0735','0736','0737','0738','0754','0757','0756','0782','0783','0784','0785','0786','0787','0788','0789','0790','0792','0793','0795','0796','0923','092','093','0940','0941','0942','0943','0944','0947','0948','095','096','098','0990','0998','099','0201','0202','0203','0204','0205','0206','0207','0208','0209','021','022','023','024','025','026','027','0280','028','0284','02885','02886','02889','02896','029']
au_prefixes = ['0233','0237','0238','0239','0240','0241','0242','0243','0244','0245','0246','0247','0248','0249','0250','0251','0252','0253','0254','0255','0256','0257','0258','0259','0260','0261','0262','0263','0264','0265','0266','0267','0268','0269','027','028','029','0332','0333','0334','0340','0341','0342','0343','0344','0345','0346','0347','0348','0349','0350','0351','0352','0353','0354','0355','0356','0357','0358','0359','0361','0362','0363','0364','0365','0367','037','038','039','072','073','0740','0741','0742','0743','0744','0745','0746','0747','0748','0749','0752','0753','0754','0755','0756','0757','0770','0775','0776','0777','0779','0825','0826','0851','0852','0853','0854','0855','0858','0860','0861','0862','0863','0864','0865','0866','0867','0868','0869','0870','0871','0872','0873','0874','0875','0876','0877','0878','0879','0880','0880','0881','0882','0883','0884','0885','0886','0887','0888','0889','0890','0891','0892','0893','0894','0895','0896','0897','0898','0899','040','041','042','043','044','045','046','047','048','049']
def restructure_tp(old_tp):
    ll = ''.join(filter(str.isdigit, old_tp))
    if (old_tp == 'None'):
        tp_num = old_tp
    elif (old_tp[0] == '+'):
        tp_num = old_tp
    elif (old_tp[0] == '6'):
        tp_num = '+' + old_tp
    elif (ll[:4] in ['1300', '1800', '0800']):
        tp_num = old_tp
    elif ((ll[:3] in au_prefixes) or (ll[:4] in au_prefixes) or (ll[:5] in au_prefixes)):
        tp_num = '+61' + old_tp[1:]
    elif ((ll[:3] in nz_prefixes) or (ll[:4] in nz_prefixes) or (ll[:5] in nz_prefixes)):
        tp_num = '+64' + old_tp[1:]
    else:
        print('cannot restructure')
        tp_num = 'None'
    return tp_num

def refer_collection():
  # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  myclient = pymongo.MongoClient(
      "mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
  # mydb = myclient["CompanyDatabase"]  # creates a database
  mydb = myclient["miner"]  # creates a database

  mycol = mydb["comp_data_cleaned"]  # creates a collection
  return mycol

def refer_simplified_dump_col_min():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient(
        "mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["simplified_dump_min"]  # creates a collection
    return mycol

def refer_projects_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient("mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["projects"]  # creates a collection
    return mycol

def refer_query_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient(
        "mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["search_queries"]  # creates a collection
    return mycol


def is_valid_tp(tp):
    ll = ''.join(filter(str.isdigit, tp))
    if(len(tp)>20):
        return False
    if('.' in tp):
        return False
    if ('12345678' in tp):
        return False
    elif (len(ll) == 10 and ((ll[:4] in ['1300','1800','0800']) or (ll[:3] in au_prefixes+nz_prefixes) or (ll[:4] in au_prefixes+nz_prefixes) or (ll[:5] in au_prefixes+nz_prefixes))):
        return True
    elif (len(ll) == 11 and ll[0:2] == '61'):
        return True
    elif (len(ll) == 12 and ll[0:2] == '61'):
        return True
    elif ((len(ll) == 10 or len(ll) == 9) and ((ll[:3] in au_prefixes+nz_prefixes) or (ll[:4] in au_prefixes+nz_prefixes) or (ll[:5] in au_prefixes+nz_prefixes))):
        return True
    elif ((len(ll) == 10 or len(ll) == 11 or len(ll) == 12) and (ll[0:2] == '64')):
        return True
    else:return False

# print(is_valid_tp('0317151814'))
# def refer_cleaned_collection():
#   # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#   myclient = pymongo.MongoClient(
#       "mongodb+srv://gatekeeper:oMBipAi6zLkme3e9@armitage-i0o8u.mongodb.net/test?retryWrites=true&w=majority")
#   # mydb = myclient["CompanyDatabase"]  # creates a database
#   mydb = myclient["miner"]  # creates a database
#
#   mycol = mydb["comp_data_cleaned"]  # creates a collection
#   return mycol
# mycol = refer_cleaned_collection()
# comp_data_entry = mycol.find({"_id": ObjectId('5eb6363894bd0b097f9c2734')})
# data = [i for i in comp_data_entry]
# print(data)
def refer_simplified_dump_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient(
        "mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["simplified_dump"]  # creates a collection
    return mycol






def refer_simplified_s_c_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient(
        "mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["simplified_s_c_dump_min"]  # creates a collection
    return mycol


# mycol = refer_query_col()
# mycol.delete_many({})

#display all existing records
def display_all_records():
  mycol = refer_collection()
  y=mycol.find()
  for k in y:
      try:
        print(k['google_cp'])
      except KeyError:
        print(None)
# display_all_records()

def get_all_ids():
    mycol = refer_collection()
    lst = []
    y = mycol.find()
    for k in y:
        lst.append(k['_id'])
        # print(k['_id'])
    print(lst)
# get_all_ids()
def clear_the_collection():
  mycol = refer_query_col()
  mycol.delete_many({'state':'incomplete'})
  print("collection is cleared!")
# clear_the_collection()




def isvalid_hq(loc):
    is_valid = False
    check_list_a = ['VIC', 'NSW', 'ACT', 'QLD', 'NT', 'SA', 'TAS', 'WA', 'AU', 'NZ', 'AUS']
    check_list_b = ['new south wales', 'victoria', 'queensland', 'western australia', 'south australia', 'tasmania',
                    'northland', 'auckland', 'waikato', 'bay of plenty', 'gisborne', "hawkes bay", 'taranaki',
                    'manawatu-whanganui', 'wellington', 'tasman', 'nelson', 'marlborough', 'west coast', 'canterbury',
                    'otago', 'southland', 'australia',
                    'new zealand', 'newzealand']
    for c_c in check_list_a:
        if c_c == 'SA':
            if (((c_c in loc) and ('USA' not in loc))):
                # print(((c_c in hq_li) and ('USA' not in hq_li)),((c_c in j_oc) and ('USA' not in j_oc)),((c_c in hq_g) and ('USA' not in hq_g)))
                is_valid = True
        else:
            if ((c_c in loc)):
                is_valid = True

    for c_i in check_list_b:
        if ((c_i in loc.lower())):
            is_valid = True
    return is_valid

def csv_exp_s_c(id_list,output_path):
    print('simplified export with sources and confidence')
    mycol = refer_collection()
    csv_dump_col = refer_simplified_s_c_col()
    # store data in a csv file
    # dump_name = 'F:\\from git\\Armitage_project\\crawl_n_depth\\Simplified_System\\dumps\\' + 'new_companies_with_sources.csv'
    dump_name = output_path
    print("check", output_path)
    with open(dump_name, mode='w', encoding='utf8',
              newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        attributes_a = ['title', 'link', 'description', 'comp_name',
                        'address', 'email', 'telephone_number', 'keywords', 'contact_person', 'type_or_sector',
                        'founded_year',
                        'revenue', 'funding', 'headquarters', 'No_of_employees', 'company_status']
        confs = ['address_confidence', 'tp_confidence', 'headquarters_confidence', 'contact_confidence',
                 'Total_confidence']
        results_writer.writerow(attributes_a + confs)

        for entry_id in id_list:
            print('id_l', entry_id)
            comp_data_entry_min = csv_dump_col.find({"_id": entry_id})
            data_min = [i for i in comp_data_entry_min]
            data_list = []
            for each_a in attributes_a+confs:
                data_list.append(data_min[0][each_a])
            results_writer.writerow(data_list)

    results_file.close()
    print("CSV export completed!")
    return dump_name


def simplified_export_with_sources_and_confidence(id_list,output_path):
    print('simplified export with sources and confidence')
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    # store data in a csv file
    # dump_name = 'F:\\from git\\Armitage_project\\crawl_n_depth\\Simplified_System\\dumps\\' + 'new_companies_with_sources.csv'
    dump_name = output_path
    print("check",output_path)
    with open(dump_name, mode='w', encoding='utf8',
              newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        attributes_a = [ 'title', 'link', 'description', 'comp_name',
                        'address', 'email','telephone_number', 'keywords','contact_person', 'type_or_sector', 'founded_year',
                        'revenue','funding','headquarters','No_of_employees','company_status']
        confs = ['address_confidence', 'tp_confidence', 'headquarters_confidence', 'contact_confidence',
                 'Total_confidence']
        results_writer.writerow(attributes_a + confs)

        for entry_id in id_list:
            print('id_l',entry_id)

            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            comp_data_entry_min = csv_dump_col.find({"_id": entry_id})
            data_min = [i for i in comp_data_entry_min]


            my_link = data[0]['link']
            # for k in data[0].keys():
            #     print(k)
            # print(data)
            data_list = []
            # print('title',data[0]['title'])
            # print('link', data[0]['link'])
            # print('description', data[0]['description'])
            # print('comp_name', data[0]['comp_name'])
            # print(data_list)
            data_list.extend([data[0]['title'],data[0]['link'],data_min[0]['description'],data[0]['comp_name']])
            print(data_list)
            attribute_keys = list(data[0].keys())

            if ('google_tp_source' in attribute_keys):google_tp_source = data[0]['google_tp_source']
            else:google_tp_source = 'None'

            if ('google_cp_source' in attribute_keys):google_cp_source = data[0]['google_cp_source']
            else:google_cp_source = 'None'

            if ('google_address_source' in attribute_keys):google_address_source = data[0]['google_address_source']
            else:google_address_source = 'None'

            if ('link_dnb' in attribute_keys):link_dnb = data[0]['link_dnb']
            else:link_dnb = 'None'

            if ('link_cb' in attribute_keys):link_cb = data[0]['link_cb']
            else:link_cb = 'None'

            if ('li_url' in attribute_keys):link_li = data[0]['li_url']
            else:link_li = 'None'

            if ('site_url_oc' in attribute_keys):site_url_oc = data[0]['site_url_oc']
            else:site_url_oc = 'None'

            if ('link_owler' in attribute_keys):link_owler = data[0]['link_owler']
            else:link_owler = 'None'

            if('comp_url_aven' in attribute_keys):
                if('https://app.avention.com' not in data[0]['comp_url_aven']):
                    link_aven = 'https://app.avention.com'+data[0]['comp_url_aven']
                else:
                    link_aven =data[0]['comp_url_aven']
            else:link_aven = 'None'
            a_conf = tp_conf = cp_conf = hq_conf = None
            # print(attribute_keys)
            for each_a in attributes_a:
                try:
                    if(each_a == 'address'):
                        #address_fix
                        try:
                            g_add, w_ad, dnb_add, oc_add = '', '', '', ''
                            if ('google_address' in attribute_keys):
                                if (len(data[0]['google_address'])):
                                    g_add = data[0]['google_address']
                            if (len(data[0]['website_addresses_with_sources'])):
                                for each in data[0]['website_addresses_with_sources']:
                                    if (isvalid_hq(each[0])):
                                        w_ad = each
                                        break
                            if ('company_address_dnb' in attribute_keys):
                                if (len(data[0]['company_address_dnb'])):
                                    dnb_add = data[0]['company_address_dnb'][0]
                            if ('registered_address_adr_oc' in attribute_keys):
                                oc_add = data[0]['registered_address_adr_oc']
                            aven_add = ''
                            if ('address_aven' in attribute_keys):
                                aven_add = data[0]['address_aven']

                            if (len(w_ad) != 0):
                                # print('w')
                                data_list.append([w_ad[0],w_ad[1]])
                            elif (isvalid_hq(g_add)):
                                # print('g')
                                data_list.append([g_add,google_address_source])  # from google
                            elif (isvalid_hq(aven_add)):
                                # print('d')
                                data_list.append([aven_add,link_aven])
                            elif (isvalid_hq(dnb_add)):
                                # print('d')
                                data_list.append([dnb_add,link_dnb])
                            elif (isvalid_hq(oc_add.lower())):
                                # print('o')
                                data_list.append([oc_add,site_url_oc])
                            else:
                                data_list.append('None')

                            print("selected_address", data_list[-1])
                            if (data_list[-1] != 'None'):
                                a_conf = get_address_confidence(data_list[-1][0], entry_id)
                                print('confidence of selected address', a_conf)
                                if (a_conf != None):
                                    if (a_conf > 0):
                                        continue
                                    else:
                                        all_ads_with_conf = get_every_address_confidence(entry_id)
                                        print('confidence of all addresses', all_ads_with_conf)
                                        if (all_ads_with_conf != None):
                                            highest_ads_with_conf = all_ads_with_conf[-1:]
                                            print('highest', highest_ads_with_conf)
                                            if (highest_ads_with_conf[0][2] > 0):
                                                if(highest_ads_with_conf[0][1]=='google'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0],google_address_source]
                                                if (highest_ads_with_conf[0][1] =='website'):
                                                    for each in data[0]['website_addresses_with_sources']:
                                                        if (each[0]==highest_ads_with_conf[0][0]):
                                                            w_ad = each
                                                            break
                                                    data_list[-1] = w_ad
                                                if (highest_ads_with_conf[0][1] == 'dnb'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], link_dnb]
                                                if (highest_ads_with_conf[0][1] == 'oc'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], site_url_oc]
                                                if (highest_ads_with_conf[0][1] == 'avention'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], link_aven]


                                                print('updated with highest confidence')

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'email'):
                        # print("***********eml")
                        #email_fix
                        try:
                            if ('Contact_Email_cb' in attribute_keys):
                                data_list.append([data[0]['Contact_Email_cb'],link_cb])
                            elif (len(data[0]['emails_with_sources'])):
                                data_list.append([data[0]['emails_with_sources'][0][0],data[0]['emails_with_sources'][0][1]])  # from website
                            else:
                                data_list.append("None")
                            # else:
                            #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'telephone_number'):
                        # print("***********tp")
                        #tp_fix
                        try:
                            tp_cb_valid = False
                            if ('Phone_Number_cb' in attribute_keys):
                                # print('cb',data[0]['Phone_Number_cb'])
                                if (is_valid_tp(data[0]['Phone_Number_cb'])):
                                    tp_cb_valid = True
                            tp_google_valid = False
                            if ('google_tp' in attribute_keys):
                                # print('cb',data[0]['Phone_Number_cb'])
                                if (is_valid_tp(data[0]['google_tp'])):
                                    tp_google_valid = True
                            dnb_tp = []
                            if ('company_tp_dnb' in attribute_keys):
                                dnb_tp = data[0]['company_tp_dnb']  # from dnb
                                # print(data_list,type(data_list))
                            w_tp = []
                            if (len(data[0]['telephone_numbers_with_sources'])):
                                plus_t = []
                                s_six = []
                                other_t = []
                                for each_tl in data[0]['telephone_numbers_with_sources']:
                                    each_t = each_tl[0]
                                    if (each_t[:3] in ['+61', '+64']):
                                        if (is_valid_tp(each_t)):
                                            plus_t.append(each_tl)
                                    if (each_t[:2] in ['61', '64']):
                                        if (is_valid_tp(each_t)):
                                            s_six.append(each_tl)
                                    if ((each_t[0] in ['0']) or (each_t[:4] in ['1300', '1800', '0800'])):
                                        if (is_valid_tp(each_t)):
                                            other_t.append(each_tl)
                                w_tp = plus_t + s_six + other_t

                            if (len(w_tp)):
                                data_list.append([w_tp[0][0], w_tp[0][1]])
                            elif (tp_google_valid):
                                data_list.append([data[0]['google_tp'],google_tp_source])  # from google
                            elif (tp_cb_valid):
                                data_list.append([data[0]['Phone_Number_cb'],link_cb])
                            elif ('Tel:_aven' in attribute_keys):
                                # print(data[0]['Tel:_aven'])
                                data_list.append([data[0]['Tel:_aven'],link_aven])
                            elif ('phone_li' in attribute_keys):
                                # print(data[0]['phone_li'].split("\n")[0])
                                data_list.append([data[0]['phone_li'].split("\n")[0],link_li])
                            elif (len(dnb_tp)):
                                if(len(dnb_tp)==1):dnb_tp=dnb_tp[0]
                                data_list.append([dnb_tp,link_dnb])  # from dnb
                            else:
                                data_list.append("None")

                            if(len(data_list[-1])==2):
                                # print('before all',data_list[-1])
                                # print('before',data_list[-1][0])
                                data_list[-1][0] = restructure_tp(data_list[-1][0])
                                # print('after', data_list[-1][0])
                            # print(data_list[-1])

                            # else:
                            #     data_list.append("None")
                            print("selected_tp", data_list[-1])
                            if (data_list[-1] != 'None'):
                                a_conf = get_tp_confidence(data_list[-1][0], entry_id)
                                print('confidence of selected tp', a_conf)
                                if (a_conf != None):
                                    if (a_conf > 0):
                                        continue
                                    else:
                                        all_ads_with_conf = get_every_tp_confidence(entry_id)
                                        print('confidence of all tps', all_ads_with_conf)
                                        if (all_ads_with_conf != None):
                                            highest_ads_with_conf = all_ads_with_conf[-1:]
                                            print('highest', highest_ads_with_conf)
                                            if (highest_ads_with_conf[0][2] > 0):
                                                if (highest_ads_with_conf[0][1] == 'google'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], google_tp_source]
                                                if (highest_ads_with_conf[0][1] == 'website'):
                                                    for each in data[0]['telephone_numbers_with_sources']:
                                                        if (each[0] == highest_ads_with_conf[0][0]):
                                                            w_ad = each
                                                            break
                                                    data_list[-1] = w_ad
                                                if (highest_ads_with_conf[0][1] == 'crunchbase'):
                                                    data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_cb]
                                                if (highest_ads_with_conf[0][1] == 'dnb'):
                                                    data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_dnb]
                                                if (highest_ads_with_conf[0][1] == 'linkein'):
                                                    data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_li]
                                                if (highest_ads_with_conf[0][1] == 'avention'):
                                                    data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_aven]



                                                print('updated with highest confidence')
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'keywords'):
                        # print("***********kw")
                        if (len(data[0]['textrank_results'])):data_list.append(data[0]['textrank_results'][:10])  # from website
                        else:data_list.append("None")

                    if (each_a == 'contact_person'):
                        # print("***********cp")
                        #contact_person_fix
                        #fix thissssssssssssssssssss********************************************************************************
                        try:
                            wb_list = []
                            if ('important_person_company' in attribute_keys):
                                det_wb = data[0]['important_person_company']

                                # print(det_wb)
                                if (det_wb != 'No important persons found'):
                                    # wb_list = [det_wb[0]['name'], det_wb[0]['job_title']]
                                    wb_list = det_wb[0]

                            li_list = []
                            if (len(data[0]['linkedin_cp_info'])):
                                for each in data[0]['linkedin_cp_info']:
                                    data_li = (each[0].split('|')[0]).split('-')
                                    if (len(data_li) > 2):
                                        # print('li cp',[data_li[0],data_li[1].strip()+'_'+data_li[2].strip()])
                                        li_list.append([data_li[0], data_li[1].strip() + '_' + data_li[2].strip()])

                            if (len(wb_list)):
                                # print('g')
                                data_list.append([wb_list,'from_website'])  # from google

                            elif ('google_cp' in attribute_keys):
                                # print('g')
                                det_gcp = data[0]['google_cp']
                                # print('gog',det_gcp)
                                data_list.append([det_gcp,google_cp_source])  # from google
                            # crunchbase
                            elif ('Founders_cb' in attribute_keys):
                                det_cb = data[0]['Founders_cb']
                                det_cb = [cb.strip() for cb in det_cb.split(',')][0]
                                data_list.append([det_cb, 'founder(s)',link_cb])

                            elif ('contacts_aven' in attribute_keys):
                                det_aven = data[0]['contacts_aven'][0]
                                data_list.append([det_aven,link_aven])

                            elif ('company_contacts_dnb' in attribute_keys):
                                # print('dnb',data[0]['dnb_cp_info'])
                                # print('dnb',dnb_list[0])
                                det_dnb = data[0]['company_contacts_dnb']
                                data_list.append([det_dnb[0],link_dnb])  # from dnb

                            elif ('directors_or_officers_oc' in attribute_keys):
                                # print('oc')

                                # print('oc',data[0]['oc_cp_info'])
                                oc_cps = []
                                # print(data[0]['directors_or_officers_oc'])
                                for each_oc in [data[0]['directors_or_officers_oc']]:
                                    # print(each_oc)
                                    oc_det = each_oc.split(',')
                                    # print(oc_det)
                                    if (len(oc_det) > 1):
                                        oc_name = oc_det[0]
                                        # print(oc_name)
                                        if (len(oc_name) > 1):
                                            oc_post = oc_det[1]
                                            oc_cps.append([oc_name, oc_post])
                                    else:
                                        oc_cps.append([oc_det, 'agent_' + each_oc[1]])

                                # print('oc',oc_cps[0])
                                data_list.append([oc_cps[0],site_url_oc])  # from oc
                            elif ('CEO_g' in attribute_keys):
                                # print('gc')
                                # print('gogq',[data[0]['CEO_g'],'CEO'])
                                data_list.append([data[0]['CEO_g'], 'CEO',link_owler])  # from google qa
                            elif ('agent_name_oc' in attribute_keys):
                                # print('oca')
                                # print('oc_ag',[data[0]['agent_name_oc'],'agent'])
                                data_list.append([data[0]['agent_name_oc'][0], 'agent',site_url_oc])  # from oc_agent
                            elif (len(li_list)):

                                data_list.append([li_list[0],'from linkedin search google'])  # from linkedin
                                # print('*****')
                            else:
                                # print('None')
                                data_list.append("None")

                            print("selected_contact_person", data_list[-1])
                            if (data_list[-1] != 'None'):
                                if(len(data_list[-1][0])==2):
                                    a_conf = get_cp_confidence(data_list[-1][0][0], entry_id)
                                else:
                                    a_conf = get_cp_confidence(data_list[-1][0], entry_id)
                                print('confidence of selected cp', a_conf)
                                if (a_conf != None):
                                    if (a_conf > 0):
                                        continue
                                    else:
                                        all_ads_with_conf = get_every_cp_confidence(entry_id)
                                        print('confidence of all cps', all_ads_with_conf)
                                        if (all_ads_with_conf != None):
                                            highest_ads_with_conf = all_ads_with_conf[-1:]
                                            print('highest', highest_ads_with_conf)
                                            if (highest_ads_with_conf[0][3] > 0):
                                                if (highest_ads_with_conf[0][2] == 'google'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], google_cp_source]
                                                if (highest_ads_with_conf[0][2] == 'website'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], 'website']
                                                if (highest_ads_with_conf[0][2] == 'crunchbase'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], link_cb]
                                                if (highest_ads_with_conf[0][2] == 'dnb'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], link_dnb]
                                                if (highest_ads_with_conf[0][2] == 'oc'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], site_url_oc]
                                                if (highest_ads_with_conf[0][2] == 'owler'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], link_owler]
                                                if (highest_ads_with_conf[0][2] == 'linkedin'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], link_li]
                                                if (highest_ads_with_conf[0][2] == 'avention'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], link_aven]

                                                print('updated with highest confidence')

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'type_or_sector'):
                        #sector_fix
                        # print("***********ty")
                        try:
                            if ('Industries_cb' in attribute_keys):
                                # print('cb', data[0]['Industries_cb'].split(', ')[:2])
                                data_list.append([data[0]['Industries_cb'].split(', ')[:2],link_cb])
                            elif ('Industry:_aven' in attribute_keys):
                                # print('aven', data[0]['Industry:_aven'])
                                data_list.append([data[0]['Industry:_aven'],link_aven])
                            elif ('industry_li' in attribute_keys):
                                # print('li', data[0]['industry_li'])
                                data_list.append([data[0]['industry_li'],link_li])  # from linkedin
                            elif ('comp_type_pred' in attribute_keys):
                                # print('clas', data[0]['comp_type_pred'][0])
                                data_list.append([data[0]['comp_type_pred'][0][0] + ', ' + data[0]['comp_type_pred'][1][
                                    0],'from_classification_model'])  # from classification
                            else:
                                data_list.append("None")

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'founded_year'):
                        #fy_fix
                        # print("***********fy")
                        try:
                            if ('Founded_Date_cb' in attribute_keys):
                                # print('cb',data[0]['Founded Date_cb'])
                                data_list.append([data[0]['Founded_Date_cb'],link_cb])  # from linkedin
                            elif ('founded_li' in attribute_keys):
                                # print('li',data[0]['founded_li'])
                                data_list.append([data[0]['founded_li'],link_li])  # from linkedin
                            elif ('incorporation_date_oc' in attribute_keys):
                                # print('oc', data[0]['incorporation_date_oc'].split(' (')[0])
                                data_list.append([data[0]['incorporation_date_oc'].split(' (')[0],site_url_oc])  # from oc
                            elif ('founded_year_g' in attribute_keys):
                                # print('g', data[0]['founded_year_g'])
                                data_list.append([data[0]['founded_year_g'],link_owler])  # from google
                            else:
                                data_list.append("None")
                            # if ('Industries_cb' in attribute_keys):
                            #     print('cb',data[0]['Industries_cb'].split(', ')[:2])
                            #     data_list.extend(data[0]['Industries_cb'].split(', ')[:2])
                            # elif ('industry_li' in attribute_keys):
                            #     print('li',data[0]['industry_li'])
                            #     data_list.extend([data[0]['industry_li']])  # from linkedin
                            # elif ('comp_type_pred' in attribute_keys):
                            #     print('clas',data[0]['comp_type_pred'][0])
                            #     data_list.extend([data[0]['comp_type_pred'][0][0]+', '+ data[0]['comp_type_pred'][1][0]])  # from classification
                            # else:
                            #     data_list.append("None")

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'revenue'):
                        #rev_fix
                        # print("***********rv")
                        try:
                            rev_d = []
                            if ('company_revenue_dnb' in attribute_keys):
                                if (len(data[0]['company_revenue_dnb'])):
                                    rev_d = data[0]['company_revenue_dnb']
                            if ('Annual_Sales:_aven' in attribute_keys):
                                # print('g')
                                data_list.append([data[0]['Annual_Sales:_aven'],link_aven])  # from google
                            elif ('revenue_g' in attribute_keys):
                                # print('g')
                                data_list.append([data[0]['revenue_g'],link_owler])  # from google
                            elif (len(rev_d)):
                                # print('d')
                                a_rev = rev_d[0].split('|')[1]
                                print(a_rev)
                                data_list.append([a_rev,link_dnb])  # from dnb
                            else:
                                data_list.append("None")
                            # if ('Contact Email_cb' in attribute_keys):
                            #     data_list = data[0]['Contact Email_cb']
                            # elif (len(data[0]['emails'])):
                            #     data_list.append(data[0]['emails'][0])  # from website
                            # else:
                            #     data_list.append("None")
                            # # else:
                            # #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'funding'):
                        # print("***********f")
                        if ('funding_g' in attribute_keys):data_list.append([data[0]['funding_g'],link_owler])  # from google
                        else:data_list.append("None")

                    if (each_a == 'headquarters'):
                        #hq_fix
                        # print("***********hq")
                        try:
                            hq_cb, hq_g, hq_li, j_oc = '', '', '', ''
                            if ('comp_headquaters_cb' in attribute_keys):
                                hq_cb = data[0]['comp_headquaters_cb']

                            if ('headquarters_li' in attribute_keys):
                                hq_li = data[0]['headquarters_li']

                            if ('jurisdiction_oc' in attribute_keys):
                                j_oc = data[0]['jurisdiction_oc']

                            if ('headquarters_g' in attribute_keys):
                                hq_g = data[0]['headquarters_g']

                            if (isvalid_hq(hq_cb)):
                                data_list.append([hq_cb,link_cb])
                            elif (isvalid_hq(hq_li)):
                                data_list.append([hq_li,link_li])
                            elif (isvalid_hq(hq_g)):
                                data_list.append([hq_g,link_owler])
                            elif (isvalid_hq(j_oc)):
                                data_list.append([j_oc,site_url_oc])
                            else:
                                data_list.append("None")
                            # else:
                            #     data_list.append("None")

                            if (data_list[-1] != 'None'):
                                a_conf = get_hq_confidence(data_list[-1][0], entry_id)
                                print('confidence of selected hq', a_conf)
                                if (a_conf != None):
                                    if (a_conf > 0):
                                        continue
                                    else:
                                        all_ads_with_conf = get_every_hq_confidence(entry_id)
                                        print('confidence of all hqs', all_ads_with_conf)
                                        if (all_ads_with_conf != None):
                                            highest_ads_with_conf = all_ads_with_conf[-1:]
                                            print('highest', highest_ads_with_conf)
                                            if (highest_ads_with_conf[0][2] > 0):
                                                if (highest_ads_with_conf[0][1] == 'crunchbase'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], link_cb]
                                                if (highest_ads_with_conf[0][1] == 'oc'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], site_url_oc]
                                                if (highest_ads_with_conf[0][1] == 'owler'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], link_owler]
                                                if (highest_ads_with_conf[0][1] == 'linkedin'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], link_li]

                                                print('updated with highest confidence')


                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'No_of_employees'):
                        #fix_ne
                        # print("***********ne")
                        try:
                            data_lil = None
                            if ('company_size_li' in attribute_keys):
                                if (data[0]['company_size_li'] != None):
                                    if (' employees' in data[0]['company_size_li']):
                                        data_lil = data[0]['company_size_li'].replace(' employees', '')
                            if ('Number_of_Employees_cb' in attribute_keys):
                                # print('cb')
                                data_list.append([data[0]['Number_of_Employees_cb'],link_cb])  # from company_size_li
                            elif ('Employees_(All_Sites):_aven' in attribute_keys):
                                data_list.append([data[0]['Employees_(All_Sites):_aven'],link_aven])
                            elif (data_lil != None):
                                data_list.append([data_lil,link_li])  # from company_size_li

                            elif ('num_employees_li' in attribute_keys):
                                # print('li')
                                data_list.append([str(data[0]['num_employees_li']).split("\n")[0],link_li])  # from linkedin
                            elif ('no_of_employees_g' in attribute_keys):
                                # print('g')
                                data_list.append([data[0]['no_of_employees_g'],link_owler])  # from googlecompany_size_li
                            else:
                                data_list.append("None")
                            # else:
                            #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'company_status'):
                        # fix_cs

                        try:
                            if ('IPO_Status_cb' in attribute_keys):
                                # print('cb', data[0]['IPO_Status_cb'])
                                data_list.append([data[0]['IPO_Status_cb'],link_cb])
                            elif ('Company_Type:_aven' in attribute_keys):
                                # print('aven', data[0]['Company_Type:_aven'])
                                data_list.append([data[0]['Company_Type:_aven'],link_aven])
                            elif ('company_type_dnb' in attribute_keys):
                                # print('dnb', data[0]['company_type_dnb'][0].split(': ')[1])
                                data_list.append([data[0]['company_type_dnb'][0].split(': ')[1],link_dnb])
                            elif ('company_type_oc' in attribute_keys):
                                # print('oc', data[0]['company_type_oc'])
                                data_list.append([data[0]['company_type_oc'],site_url_oc])
                            else:
                                data_list.append("None")
                            # else:
                            #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                except KeyError:
                    data_list.append('None')

                except Exception as e:
                    data_list.append('None')
                    print("Exception Occured during dumping ", e)
            # print('keys',data_min[0].keys())
            try:
                if (data_min[0]['address'] != 'None'):
                    # print('recevied',data_min[0]['address'])
                    a_conf = get_address_confidence(data_min[0]['address'], entry_id)
                    a_conf = moderate_confidence('address', data_min[0]['address'], entry_id, a_conf)
                    print('address_conf', a_conf)

                if (data_min[0]['telephone_number'] != 'None'):
                    tp_conf = get_tp_confidence(data_min[0]['telephone_number'], entry_id)
                    tp_conf = moderate_confidence('tp', data_min[0]['telephone_number'], entry_id, tp_conf)
                    print('tp_conf', tp_conf)

                if (data_min[0]['contact_person'] != 'None'):
                    print('id', entry_id)
                    print('collected cp', data_min[0]['contact_person'][0])
                    cp_conf = get_cp_confidence(data_min[0]['contact_person'][0], entry_id)
                    cp_conf = moderate_confidence('cp', data_min[0]['contact_person'], entry_id, cp_conf)
                    print('cp_conf', cp_conf)

                if (data_min[0]['headquarters'] != 'None'):
                    hq_conf = get_hq_confidence(data_min[0]['headquarters'], entry_id)
                    hq_conf = moderate_confidence('hq', data_min[0]['headquarters'], entry_id, hq_conf)
                    print('hq_conf', hq_conf)

                if (a_conf == None): a_conf = 0.0
                if (tp_conf == None): tp_conf = 0.0
                if (cp_conf == None): cp_conf = 0.0
                if (hq_conf == None): hq_conf = 0.0

                total_conf = (a_conf + tp_conf + cp_conf + hq_conf) / 4

                data_list.extend([a_conf])
                data_list.extend([tp_conf])
                data_list.extend([cp_conf])
                data_list.extend([hq_conf])
                data_list.extend([total_conf])
            except Exception as e:
                # simplified_update([entry_id])
                data_list.extend(['error'])
                data_list.extend(['error'])
                data_list.extend(['error'])
                data_list.extend(['error'])
                data_list.extend(['error'])

            results_writer.writerow(data_list)
            # dict_to_dump = {}
            # for i in range(len(attributes_a)):
            #     dict_to_dump[attributes_a[i]] = data_list[i]
            # print(dict_to_dump)
            #
            # # record_entry = csv_dump_col.insert_one(dict_to_dump)
            # csv_dump_col.update_one({'_id': entry_id}, {'$set': dict_to_dump})
            print("comp profile record stored")
        results_file.close()
    print("CSV export completed!")
    return dump_name


def simplified_export_with_sources_and_confidence_via_queue():
    print('simplified export with sources and confidence queue is live')
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    csv_s_c_col = refer_simplified_s_c_col()
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    simplified_s_c_dump_client = QueueClient.from_connection_string(connect_str, "simplified-s-c-queue")
    attributes_a = ['_id','title', 'link', 'description', 'comp_name',
                    'address', 'email', 'telephone_number', 'keywords', 'contact_person', 'type_or_sector',
                    'founded_year',
                    'revenue', 'funding', 'headquarters',
                    'No_of_employees', 'company_status',
                    'address_confidence', 'tp_confidence',
                    'headquarters_confidence', 'contact_confidence',
             'Total_confidence']

    while (True):
        time.sleep(10)
        rows = simplified_s_c_dump_client.receive_messages()
        for msg in rows:
            time.sleep(10)
            row = msg.content
            row = ast.literal_eval(row)
            print('profile dumping',row[0])
            entry_id = ObjectId(row[0])

            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            comp_data_entry_min = csv_dump_col.find({"_id": entry_id})
            data_min = [i for i in comp_data_entry_min]
            try:
                if(data[0]['simplified_dump_state']=='Completed'):

                    my_link = data[0]['link']

                    data_list = []

                    data_list.extend([data[0]['_id'],data[0]['title'],data[0]['link'],data_min[0]['description'],data[0]['comp_name']])
                    print(data_list)
                    attribute_keys = list(data[0].keys())

                    if ('google_tp_source' in attribute_keys):google_tp_source = data[0]['google_tp_source']
                    else:google_tp_source = 'None'

                    if ('google_cp_source' in attribute_keys):google_cp_source = data[0]['google_cp_source']
                    else:google_cp_source = 'None'

                    if ('google_address_source' in attribute_keys):google_address_source = data[0]['google_address_source']
                    else:google_address_source = 'None'

                    if ('link_dnb' in attribute_keys):link_dnb = data[0]['link_dnb']
                    else:link_dnb = 'None'

                    if ('link_cb' in attribute_keys):link_cb = data[0]['link_cb']
                    else:link_cb = 'None'

                    if ('li_url' in attribute_keys):link_li = data[0]['li_url']
                    else:link_li = 'None'

                    if ('site_url_oc' in attribute_keys):site_url_oc = data[0]['site_url_oc']
                    else:site_url_oc = 'None'

                    if ('link_owler' in attribute_keys):link_owler = data[0]['link_owler']
                    else:link_owler = 'None'

                    if('comp_url_aven' in attribute_keys):
                        if('https://app.avention.com' not in data[0]['comp_url_aven']):
                            link_aven = 'https://app.avention.com'+data[0]['comp_url_aven']
                        else:
                            link_aven =data[0]['comp_url_aven']
                    else:link_aven = 'None'
                    a_conf = tp_conf = cp_conf = hq_conf = None
                    # print(attribute_keys)
                    for each_a in attributes_a:
                        try:
                            if(each_a == 'address'):
                                #address_fix
                                try:
                                    g_add, w_ad, dnb_add, oc_add = '', '', '', ''
                                    if ('google_address' in attribute_keys):
                                        if (len(data[0]['google_address'])):
                                            g_add = data[0]['google_address']
                                    if (len(data[0]['website_addresses_with_sources'])):
                                        for each in data[0]['website_addresses_with_sources']:
                                            if (isvalid_hq(each[0])):
                                                w_ad = each
                                                break
                                    if ('company_address_dnb' in attribute_keys):
                                        if (len(data[0]['company_address_dnb'])):
                                            dnb_add = data[0]['company_address_dnb'][0]
                                    if ('registered_address_adr_oc' in attribute_keys):
                                        oc_add = data[0]['registered_address_adr_oc']
                                    aven_add = ''
                                    if ('address_aven' in attribute_keys):
                                        aven_add = data[0]['address_aven']

                                    if (len(w_ad) != 0):
                                        # print('w')
                                        data_list.append([w_ad[0],w_ad[1]])
                                    elif (isvalid_hq(g_add)):
                                        # print('g')
                                        data_list.append([g_add,google_address_source])  # from google
                                    elif (isvalid_hq(aven_add)):
                                        # print('d')
                                        data_list.append([aven_add,link_aven])
                                    elif (isvalid_hq(dnb_add)):
                                        # print('d')
                                        data_list.append([dnb_add,link_dnb])
                                    elif (isvalid_hq(oc_add.lower())):
                                        # print('o')
                                        data_list.append([oc_add,site_url_oc])
                                    else:
                                        data_list.append('None')

                                    print("selected_address", data_list[-1])
                                    if (data_list[-1] != 'None'):
                                        a_conf = get_address_confidence(data_list[-1][0], entry_id)
                                        print('confidence of selected address', a_conf)
                                        if (a_conf != None):
                                            if (a_conf > 0):
                                                continue
                                            else:
                                                all_ads_with_conf = get_every_address_confidence(entry_id)
                                                print('confidence of all addresses', all_ads_with_conf)
                                                if (all_ads_with_conf != None):
                                                    highest_ads_with_conf = all_ads_with_conf[-1:]
                                                    print('highest', highest_ads_with_conf)
                                                    if (highest_ads_with_conf[0][2] > 0):
                                                        if(highest_ads_with_conf[0][1]=='google'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0],google_address_source]
                                                        if (highest_ads_with_conf[0][1] =='website'):
                                                            for each in data[0]['website_addresses_with_sources']:
                                                                if (each[0]==highest_ads_with_conf[0][0]):
                                                                    w_ad = each
                                                                    break
                                                            data_list[-1] = w_ad
                                                        if (highest_ads_with_conf[0][1] == 'dnb'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0], link_dnb]
                                                        if (highest_ads_with_conf[0][1] == 'oc'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0], site_url_oc]
                                                        if (highest_ads_with_conf[0][1] == 'avention'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0], link_aven]


                                                        print('updated with highest confidence')

                                except KeyError:
                                    data_list.append('None')

                            if (each_a == 'email'):
                                # print("***********eml")
                                #email_fix
                                try:
                                    if ('Contact_Email_cb' in attribute_keys):
                                        data_list.append([data[0]['Contact_Email_cb'],link_cb])
                                    elif (len(data[0]['emails_with_sources'])):
                                        data_list.append([data[0]['emails_with_sources'][0][0],data[0]['emails_with_sources'][0][1]])  # from website
                                    else:
                                        data_list.append("None")
                                    # else:
                                    #     data_list.append("None")
                                except KeyError:
                                    data_list.append('None')

                            if (each_a == 'telephone_number'):
                                # print("***********tp")
                                #tp_fix
                                try:
                                    tp_cb_valid = False
                                    if ('Phone_Number_cb' in attribute_keys):
                                        # print('cb',data[0]['Phone_Number_cb'])
                                        if (is_valid_tp(data[0]['Phone_Number_cb'])):
                                            tp_cb_valid = True
                                    tp_google_valid = False
                                    if ('google_tp' in attribute_keys):
                                        # print('cb',data[0]['Phone_Number_cb'])
                                        if (is_valid_tp(data[0]['google_tp'])):
                                            tp_google_valid = True
                                    dnb_tp = []
                                    if ('company_tp_dnb' in attribute_keys):
                                        dnb_tp = data[0]['company_tp_dnb']  # from dnb
                                        # print(data_list,type(data_list))
                                    w_tp = []
                                    if (len(data[0]['telephone_numbers_with_sources'])):
                                        plus_t = []
                                        s_six = []
                                        other_t = []
                                        for each_tl in data[0]['telephone_numbers_with_sources']:
                                            each_t = each_tl[0]
                                            if (each_t[:3] in ['+61', '+64']):
                                                if (is_valid_tp(each_t)):
                                                    plus_t.append(each_tl)
                                            if (each_t[:2] in ['61', '64']):
                                                if (is_valid_tp(each_t)):
                                                    s_six.append(each_tl)
                                            if ((each_t[0] in ['0']) or (each_t[:4] in ['1300', '1800', '0800'])):
                                                if (is_valid_tp(each_t)):
                                                    other_t.append(each_tl)
                                        w_tp = plus_t + s_six + other_t

                                    if (len(w_tp)):
                                        data_list.append([w_tp[0][0], w_tp[0][1]])
                                    elif (tp_google_valid):
                                        data_list.append([data[0]['google_tp'],google_tp_source])  # from google
                                    elif (tp_cb_valid):
                                        data_list.append([data[0]['Phone_Number_cb'],link_cb])
                                    elif ('Tel:_aven' in attribute_keys):
                                        # print(data[0]['Tel:_aven'])
                                        data_list.append([data[0]['Tel:_aven'],link_aven])
                                    elif ('phone_li' in attribute_keys):
                                        # print(data[0]['phone_li'].split("\n")[0])
                                        data_list.append([data[0]['phone_li'].split("\n")[0],link_li])
                                    elif (len(dnb_tp)):
                                        if(len(dnb_tp)==1):dnb_tp=dnb_tp[0]
                                        data_list.append([dnb_tp,link_dnb])  # from dnb
                                    else:
                                        data_list.append("None")

                                    if(len(data_list[-1])==2):
                                        # print('before all',data_list[-1])
                                        # print('before',data_list[-1][0])
                                        data_list[-1][0] = restructure_tp(data_list[-1][0])
                                        # print('after', data_list[-1][0])
                                    # print(data_list[-1])

                                    # else:
                                    #     data_list.append("None")
                                    print("selected_tp", data_list[-1])
                                    if (data_list[-1] != 'None'):
                                        a_conf = get_tp_confidence(data_list[-1][0], entry_id)
                                        print('confidence of selected tp', a_conf)
                                        if (a_conf != None):
                                            if (a_conf > 0):
                                                continue
                                            else:
                                                all_ads_with_conf = get_every_tp_confidence(entry_id)
                                                print('confidence of all tps', all_ads_with_conf)
                                                if (all_ads_with_conf != None):
                                                    highest_ads_with_conf = all_ads_with_conf[-1:]
                                                    print('highest', highest_ads_with_conf)
                                                    if (highest_ads_with_conf[0][2] > 0):
                                                        if (highest_ads_with_conf[0][1] == 'google'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0], google_tp_source]
                                                        if (highest_ads_with_conf[0][1] == 'website'):
                                                            for each in data[0]['telephone_numbers_with_sources']:
                                                                if (each[0] == highest_ads_with_conf[0][0]):
                                                                    w_ad = each
                                                                    break
                                                            data_list[-1] = w_ad
                                                        if (highest_ads_with_conf[0][1] == 'crunchbase'):
                                                            data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_cb]
                                                        if (highest_ads_with_conf[0][1] == 'dnb'):
                                                            data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_dnb]
                                                        if (highest_ads_with_conf[0][1] == 'linkein'):
                                                            data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_li]
                                                        if (highest_ads_with_conf[0][1] == 'avention'):
                                                            data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_aven]



                                                        print('updated with highest confidence')
                                except KeyError:
                                    data_list.append('None')

                            if (each_a == 'keywords'):
                                # print("***********kw")
                                if (len(data[0]['textrank_results'])):data_list.append(data[0]['textrank_results'][:10])  # from website
                                else:data_list.append("None")

                            if (each_a == 'contact_person'):
                                # print("***********cp")
                                #contact_person_fix
                                #fix thissssssssssssssssssss********************************************************************************
                                try:
                                    wb_list = []
                                    if ('important_person_company' in attribute_keys):
                                        det_wb = data[0]['important_person_company']

                                        # print(det_wb)
                                        if (det_wb != 'No important persons found'):
                                            # wb_list = [det_wb[0]['name'], det_wb[0]['job_title']]
                                            wb_list = det_wb[0]

                                    li_list = []
                                    if (len(data[0]['linkedin_cp_info'])):
                                        for each in data[0]['linkedin_cp_info']:
                                            data_li = (each[0].split('|')[0]).split('-')
                                            if (len(data_li) > 2):
                                                # print('li cp',[data_li[0],data_li[1].strip()+'_'+data_li[2].strip()])
                                                li_list.append([data_li[0], data_li[1].strip() + '_' + data_li[2].strip()])

                                    if (len(wb_list)):
                                        # print('g')
                                        data_list.append([wb_list,'from_website'])  # from google

                                    elif ('google_cp' in attribute_keys):
                                        # print('g')
                                        det_gcp = data[0]['google_cp']
                                        # print('gog',det_gcp)
                                        data_list.append([det_gcp,google_cp_source])  # from google
                                    # crunchbase
                                    elif ('Founders_cb' in attribute_keys):
                                        det_cb = data[0]['Founders_cb']
                                        det_cb = [cb.strip() for cb in det_cb.split(',')][0]
                                        data_list.append([det_cb, 'founder(s)',link_cb])

                                    elif ('contacts_aven' in attribute_keys):
                                        det_aven = data[0]['contacts_aven'][0]
                                        data_list.append([det_aven,link_aven])

                                    elif ('company_contacts_dnb' in attribute_keys):
                                        # print('dnb',data[0]['dnb_cp_info'])
                                        # print('dnb',dnb_list[0])
                                        det_dnb = data[0]['company_contacts_dnb']
                                        data_list.append([det_dnb[0],link_dnb])  # from dnb

                                    elif ('directors_or_officers_oc' in attribute_keys):
                                        # print('oc')

                                        # print('oc',data[0]['oc_cp_info'])
                                        oc_cps = []
                                        # print(data[0]['directors_or_officers_oc'])
                                        for each_oc in [data[0]['directors_or_officers_oc']]:
                                            # print(each_oc)
                                            oc_det = each_oc.split(',')
                                            # print(oc_det)
                                            if (len(oc_det) > 1):
                                                oc_name = oc_det[0]
                                                # print(oc_name)
                                                if (len(oc_name) > 1):
                                                    oc_post = oc_det[1]
                                                    oc_cps.append([oc_name, oc_post])
                                            else:
                                                oc_cps.append([oc_det, 'agent_' + each_oc[1]])

                                        # print('oc',oc_cps[0])
                                        data_list.append([oc_cps[0],site_url_oc])  # from oc
                                    elif ('CEO_g' in attribute_keys):
                                        # print('gc')
                                        # print('gogq',[data[0]['CEO_g'],'CEO'])
                                        data_list.append([data[0]['CEO_g'], 'CEO',link_owler])  # from google qa
                                    elif ('agent_name_oc' in attribute_keys):
                                        # print('oca')
                                        # print('oc_ag',[data[0]['agent_name_oc'],'agent'])
                                        data_list.append([data[0]['agent_name_oc'][0], 'agent',site_url_oc])  # from oc_agent
                                    elif (len(li_list)):

                                        data_list.append([li_list[0],'from linkedin search google'])  # from linkedin
                                        # print('*****')
                                    else:
                                        # print('None')
                                        data_list.append("None")

                                    print("selected_contact_person", data_list[-1])
                                    if (data_list[-1] != 'None'):
                                        if(len(data_list[-1][0])==2):
                                            a_conf = get_cp_confidence(data_list[-1][0][0], entry_id)
                                        else:
                                            a_conf = get_cp_confidence(data_list[-1][0], entry_id)
                                        print('confidence of selected cp', a_conf)
                                        if (a_conf != None):
                                            if (a_conf > 0):
                                                continue
                                            else:
                                                all_ads_with_conf = get_every_cp_confidence(entry_id)
                                                print('confidence of all cps', all_ads_with_conf)
                                                if (all_ads_with_conf != None):
                                                    highest_ads_with_conf = all_ads_with_conf[-1:]
                                                    print('highest', highest_ads_with_conf)
                                                    if (highest_ads_with_conf[0][3] > 0):
                                                        if (highest_ads_with_conf[0][2] == 'google'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0:2], google_cp_source]
                                                        if (highest_ads_with_conf[0][2] == 'website'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0:2], 'website']
                                                        if (highest_ads_with_conf[0][2] == 'crunchbase'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0:2], link_cb]
                                                        if (highest_ads_with_conf[0][2] == 'dnb'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0:2], link_dnb]
                                                        if (highest_ads_with_conf[0][2] == 'oc'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0:2], site_url_oc]
                                                        if (highest_ads_with_conf[0][2] == 'owler'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0:2], link_owler]
                                                        if (highest_ads_with_conf[0][2] == 'linkedin'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0:2], link_li]
                                                        if (highest_ads_with_conf[0][2] == 'avention'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0:2], link_aven]

                                                        print('updated with highest confidence')

                                except KeyError:
                                    data_list.append('None')

                            if (each_a == 'type_or_sector'):
                                #sector_fix
                                # print("***********ty")
                                try:
                                    if ('Industries_cb' in attribute_keys):
                                        # print('cb', data[0]['Industries_cb'].split(', ')[:2])
                                        data_list.append([data[0]['Industries_cb'].split(', ')[:2],link_cb])
                                    elif ('Industry:_aven' in attribute_keys):
                                        # print('aven', data[0]['Industry:_aven'])
                                        data_list.append([data[0]['Industry:_aven'],link_aven])
                                    elif ('industry_li' in attribute_keys):
                                        # print('li', data[0]['industry_li'])
                                        data_list.append([data[0]['industry_li'],link_li])  # from linkedin
                                    elif ('comp_type_pred' in attribute_keys):
                                        # print('clas', data[0]['comp_type_pred'][0])
                                        data_list.append([data[0]['comp_type_pred'][0][0] + ', ' + data[0]['comp_type_pred'][1][
                                            0],'from_classification_model'])  # from classification
                                    else:
                                        data_list.append("None")

                                except KeyError:
                                    data_list.append('None')

                            if (each_a == 'founded_year'):
                                #fy_fix
                                # print("***********fy")
                                try:
                                    if ('Founded_Date_cb' in attribute_keys):
                                        # print('cb',data[0]['Founded Date_cb'])
                                        data_list.append([data[0]['Founded_Date_cb'],link_cb])  # from linkedin
                                    elif ('founded_li' in attribute_keys):
                                        # print('li',data[0]['founded_li'])
                                        data_list.append([data[0]['founded_li'],link_li])  # from linkedin
                                    elif ('incorporation_date_oc' in attribute_keys):
                                        # print('oc', data[0]['incorporation_date_oc'].split(' (')[0])
                                        data_list.append([data[0]['incorporation_date_oc'].split(' (')[0],site_url_oc])  # from oc
                                    elif ('founded_year_g' in attribute_keys):
                                        # print('g', data[0]['founded_year_g'])
                                        data_list.append([data[0]['founded_year_g'],link_owler])  # from google
                                    else:
                                        data_list.append("None")
                                    # if ('Industries_cb' in attribute_keys):
                                    #     print('cb',data[0]['Industries_cb'].split(', ')[:2])
                                    #     data_list.extend(data[0]['Industries_cb'].split(', ')[:2])
                                    # elif ('industry_li' in attribute_keys):
                                    #     print('li',data[0]['industry_li'])
                                    #     data_list.extend([data[0]['industry_li']])  # from linkedin
                                    # elif ('comp_type_pred' in attribute_keys):
                                    #     print('clas',data[0]['comp_type_pred'][0])
                                    #     data_list.extend([data[0]['comp_type_pred'][0][0]+', '+ data[0]['comp_type_pred'][1][0]])  # from classification
                                    # else:
                                    #     data_list.append("None")

                                except KeyError:
                                    data_list.append('None')

                            if (each_a == 'revenue'):
                                #rev_fix
                                # print("***********rv")
                                try:
                                    rev_d = []
                                    if ('company_revenue_dnb' in attribute_keys):
                                        if (len(data[0]['company_revenue_dnb'])):
                                            rev_d = data[0]['company_revenue_dnb']
                                    if ('Annual_Sales:_aven' in attribute_keys):
                                        # print('g')
                                        data_list.append([data[0]['Annual_Sales:_aven'],link_aven])  # from google
                                    elif ('revenue_g' in attribute_keys):
                                        # print('g')
                                        data_list.append([data[0]['revenue_g'],link_owler])  # from google
                                    elif (len(rev_d)):
                                        # print('d')
                                        a_rev = rev_d[0].split('|')[1]
                                        print(a_rev)
                                        data_list.append([a_rev,link_dnb])  # from dnb
                                    else:
                                        data_list.append("None")
                                    # if ('Contact Email_cb' in attribute_keys):
                                    #     data_list = data[0]['Contact Email_cb']
                                    # elif (len(data[0]['emails'])):
                                    #     data_list.append(data[0]['emails'][0])  # from website
                                    # else:
                                    #     data_list.append("None")
                                    # # else:
                                    # #     data_list.append("None")
                                except KeyError:
                                    data_list.append('None')

                            if (each_a == 'funding'):
                                # print("***********f")
                                if ('funding_g' in attribute_keys):data_list.append([data[0]['funding_g'],link_owler])  # from google
                                else:data_list.append("None")

                            if (each_a == 'headquarters'):
                                #hq_fix
                                # print("***********hq")
                                try:
                                    hq_cb, hq_g, hq_li, j_oc = '', '', '', ''
                                    if ('comp_headquaters_cb' in attribute_keys):
                                        hq_cb = data[0]['comp_headquaters_cb']

                                    if ('headquarters_li' in attribute_keys):
                                        hq_li = data[0]['headquarters_li']

                                    if ('jurisdiction_oc' in attribute_keys):
                                        j_oc = data[0]['jurisdiction_oc']

                                    if ('headquarters_g' in attribute_keys):
                                        hq_g = data[0]['headquarters_g']

                                    if (isvalid_hq(hq_cb)):
                                        data_list.append([hq_cb,link_cb])
                                    elif (isvalid_hq(hq_li)):
                                        data_list.append([hq_li,link_li])
                                    elif (isvalid_hq(hq_g)):
                                        data_list.append([hq_g,link_owler])
                                    elif (isvalid_hq(j_oc)):
                                        data_list.append([j_oc,site_url_oc])
                                    else:
                                        data_list.append("None")
                                    # else:
                                    #     data_list.append("None")

                                    if (data_list[-1] != 'None'):
                                        a_conf = get_hq_confidence(data_list[-1][0], entry_id)
                                        print('confidence of selected hq', a_conf)
                                        if (a_conf != None):
                                            if (a_conf > 0):
                                                continue
                                            else:
                                                all_ads_with_conf = get_every_hq_confidence(entry_id)
                                                print('confidence of all hqs', all_ads_with_conf)
                                                if (all_ads_with_conf != None):
                                                    highest_ads_with_conf = all_ads_with_conf[-1:]
                                                    print('highest', highest_ads_with_conf)
                                                    if (highest_ads_with_conf[0][2] > 0):
                                                        if (highest_ads_with_conf[0][1] == 'crunchbase'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0], link_cb]
                                                        if (highest_ads_with_conf[0][1] == 'oc'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0], site_url_oc]
                                                        if (highest_ads_with_conf[0][1] == 'owler'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0], link_owler]
                                                        if (highest_ads_with_conf[0][1] == 'linkedin'):
                                                            data_list[-1] = [highest_ads_with_conf[0][0], link_li]

                                                        print('updated with highest confidence')


                                except KeyError:
                                    data_list.append('None')

                            if (each_a == 'No_of_employees'):
                                #fix_ne
                                # print("***********ne")
                                try:
                                    data_lil = None
                                    if ('company_size_li' in attribute_keys):
                                        if (data[0]['company_size_li'] != None):
                                            if (' employees' in data[0]['company_size_li']):
                                                data_lil = data[0]['company_size_li'].replace(' employees', '')
                                    if ('Number_of_Employees_cb' in attribute_keys):
                                        # print('cb')
                                        data_list.append([data[0]['Number_of_Employees_cb'],link_cb])  # from company_size_li
                                    elif ('Employees_(All_Sites):_aven' in attribute_keys):
                                        data_list.append([data[0]['Employees_(All_Sites):_aven'],link_aven])
                                    elif (data_lil != None):
                                        data_list.append([data_lil,link_li])  # from company_size_li

                                    elif ('num_employees_li' in attribute_keys):
                                        # print('li')
                                        data_list.append([str(data[0]['num_employees_li']).split("\n")[0],link_li])  # from linkedin
                                    elif ('no_of_employees_g' in attribute_keys):
                                        # print('g')
                                        data_list.append([data[0]['no_of_employees_g'],link_owler])  # from googlecompany_size_li
                                    else:
                                        data_list.append("None")
                                    # else:
                                    #     data_list.append("None")
                                except KeyError:
                                    data_list.append('None')

                            if (each_a == 'company_status'):
                                # fix_cs

                                try:
                                    if ('IPO_Status_cb' in attribute_keys):
                                        # print('cb', data[0]['IPO_Status_cb'])
                                        data_list.append([data[0]['IPO_Status_cb'],link_cb])
                                    elif ('Company_Type:_aven' in attribute_keys):
                                        # print('aven', data[0]['Company_Type:_aven'])
                                        data_list.append([data[0]['Company_Type:_aven'],link_aven])
                                    elif ('company_type_dnb' in attribute_keys):
                                        # print('dnb', data[0]['company_type_dnb'][0].split(': ')[1])
                                        data_list.append([data[0]['company_type_dnb'][0].split(': ')[1],link_dnb])
                                    elif ('company_type_oc' in attribute_keys):
                                        # print('oc', data[0]['company_type_oc'])
                                        data_list.append([data[0]['company_type_oc'],site_url_oc])
                                    else:
                                        data_list.append("None")
                                    # else:
                                    #     data_list.append("None")
                                except KeyError:
                                    data_list.append('None')

                        except KeyError:
                            data_list.append('None')

                        except Exception as e:
                            data_list.append('None')
                            print("Exception Occured during dumping ", e)
                    # print('keys',data_min[0].keys())
                    try:
                        if (data_min[0]['address'] != 'None'):
                            # print('recevied',data_min[0]['address'])
                            a_conf = get_address_confidence(data_min[0]['address'], entry_id)
                            a_conf = moderate_confidence('address', data_min[0]['address'], entry_id, a_conf)
                            print('address_conf', a_conf)

                        if (data_min[0]['telephone_number'] != 'None'):
                            tp_conf = get_tp_confidence(data_min[0]['telephone_number'], entry_id)
                            tp_conf = moderate_confidence('tp', data_min[0]['telephone_number'], entry_id, tp_conf)
                            print('tp_conf', tp_conf)

                        if (data_min[0]['contact_person'] != 'None'):
                            print('id', entry_id)
                            print('collected cp', data_min[0]['contact_person'][0])
                            cp_conf = get_cp_confidence(data_min[0]['contact_person'][0], entry_id)
                            cp_conf = moderate_confidence('cp', data_min[0]['contact_person'], entry_id, cp_conf)
                            print('cp_conf', cp_conf)

                        if (data_min[0]['headquarters'] != 'None'):
                            hq_conf = get_hq_confidence(data_min[0]['headquarters'], entry_id)
                            hq_conf = moderate_confidence('hq', data_min[0]['headquarters'], entry_id, hq_conf)
                            print('hq_conf', hq_conf)

                        if (a_conf == None): a_conf = 0.0
                        if (tp_conf == None): tp_conf = 0.0
                        if (cp_conf == None): cp_conf = 0.0
                        if (hq_conf == None): hq_conf = 0.0

                        total_conf = (a_conf + tp_conf + cp_conf + hq_conf) / 4

                        data_list.extend([a_conf])
                        data_list.extend([tp_conf])
                        data_list.extend([cp_conf])
                        data_list.extend([hq_conf])
                        data_list.extend([total_conf])
                    except Exception as e:
                        # simplified_update([entry_id])
                        data_list.extend(['error'])
                        data_list.extend(['error'])
                        data_list.extend(['error'])
                        data_list.extend(['error'])
                        data_list.extend(['error'])


                    dict_to_dump = {}
                    for i in range(len(attributes_a)):
                        # print([i,attributes_a[i],data_list[i]])
                        dict_to_dump[attributes_a[i]] = data_list[i]
                    print(dict_to_dump)
                    record_entry = csv_s_c_col.insert_one(dict_to_dump)
                    print("simplified dump with sources and confidences completed", record_entry.inserted_id)
                    simplified_s_c_dump_client.delete_message(msg)
                    mycol.update_one({'_id': entry_id},
                                     {'$set': {'simplified_dump_s_c_state': 'Completed'}})

                    # record_entry = csv_dump_col.insert_one(dict_to_dump)

            except pymongo.errors.DuplicateKeyError:
                print('Already Existing')
                csv_s_c_col.update_one({'_id': entry_id},
                                        {'$set': dict_to_dump})
                simplified_s_c_dump_client.delete_message(msg)
                mycol.update_one({'_id': entry_id},
                                 {'$set': {'simplified_dump_s_c_state': 'Completed'}})
            except KeyError as e:
                print('key not found', e)
            except IndexError as e:
                print('yet raw entry not available')
            except Exception as e:
                print("Exception Occured during dumping ", e)

def get_data_for_simplified_dump_based_on_source_order(entry_id):
    data_list = []
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    attributes_a = ['_id', 'search_text', 'title', 'link', 'description', 'comp_name',
                    'address', 'email', 'telephone_number', 'keywords', 'contact_person', 'type_or_sector',
                    'founded_year',
                    'revenue', 'funding', 'headquarters', 'No_of_employees','company_status']
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    attribute_keys = list(data[0].keys())
    for each_a in attributes_a:
        try:
            if (each_a == 'address'):
                # address_fix
                try:
                    g_add, w_ad, dnb_add, oc_add = '', '', '', ''
                    if ('google_address' in attribute_keys):
                        if (len(data[0]['google_address'])):
                            g_add = data[0]['google_address']
                    if (len(data[0]['addresses'])):
                        for each in data[0]['addresses']:
                            if (isvalid_hq(each)):
                                w_ad = each
                                break
                    if ('company_address_dnb' in attribute_keys):
                        if (len(data[0]['company_address_dnb'])):
                            dnb_add = data[0]['company_address_dnb'][0]
                    if ('registered_address_adr_oc' in attribute_keys):
                        oc_add = data[0]['registered_address_adr_oc']
                    aven_add = ''
                    if ('address_aven' in attribute_keys):
                        aven_add = data[0]['address_aven']

                    if (len(w_ad) != 0):
                        # print('w')
                        data_list.append(w_ad)
                    elif (isvalid_hq(g_add)):
                        # print('g')
                        data_list.append(g_add)  # from google
                    elif (isvalid_hq(aven_add)):
                        # print('d')
                        data_list.append(aven_add)
                    elif (isvalid_hq(dnb_add)):
                        # print('d')
                        data_list.append(dnb_add)
                    elif (isvalid_hq(oc_add.lower())):
                        # print('o')
                        data_list.append(oc_add)
                    else:
                        data_list.append('None')

                    print("selected_address", data_list[-1])
                    if (data_list[-1] != 'None'):

                        a_conf = get_address_confidence(data_list[-1], entry_id)
                        # print('ok')
                        print('confidence of selected address', a_conf)
                        if (a_conf != None):
                            if (a_conf > 0):
                                continue
                            else:
                                all_ads_with_conf = get_every_address_confidence(entry_id)
                                print('confidence of all addresses', all_ads_with_conf)
                                if (all_ads_with_conf != None):
                                    highest_ads_with_conf = all_ads_with_conf[-1:]
                                    print('highest', highest_ads_with_conf)
                                    if (highest_ads_with_conf[0][2] > 0):
                                        data_list[-1] = highest_ads_with_conf[0][0]
                                        print('updated with highest confidence')

                except KeyError:
                    data_list.append('None')

            if (each_a == 'email'):
                # print("***********eml")
                # email_fix
                try:
                    if ('Contact_Email_cb' in attribute_keys):
                        data_list.append(data[0]['Contact_Email_cb'])
                    elif (len(data[0]['emails'])):
                        data_list.append(data[0]['emails'][0])  # from website
                    else:
                        data_list.append("None")
                    # else:
                    #     data_list.append("None")
                except KeyError:
                    data_list.append('None')

            if (each_a == 'telephone_number'):
                # print("***********tp")
                # tp_fix
                try:
                    tp_cb_valid = False
                    if ('Phone_Number_cb' in attribute_keys):
                        # print('cb',data[0]['Phone_Number_cb'])
                        if (is_valid_tp(data[0]['Phone_Number_cb'])):
                            tp_cb_valid = True
                    tp_google_valid = False
                    if ('google_tp' in attribute_keys):
                        # print('cb',data[0]['Phone_Number_cb'])
                        if (is_valid_tp(data[0]['google_tp'])):
                            tp_google_valid = True
                    dnb_tp = []
                    if ('company_tp_dnb' in attribute_keys):
                        dnb_tp = data[0]['company_tp_dnb']  # from dnb

                    w_tp = []
                    if (len(data[0]['telephone_numbers'])):
                        plus_t = []
                        s_six = []
                        other_t = []
                        for each_t in data[0]['telephone_numbers']:
                            if (each_t[:3] in ['+61', '+64']):
                                if (is_valid_tp(each_t)):
                                    plus_t.append(each_t)
                            if (each_t[:2] in ['61', '64']):
                                if (is_valid_tp(each_t)):
                                    s_six.append(each_t)
                            if ((each_t[0] in ['0']) or (each_t[:4] in ['1300', '1800', '0800'])):
                                if (is_valid_tp(each_t)):
                                    other_t.append(each_t)
                        w_tp = plus_t + s_six + other_t

                    if (len(w_tp)):
                        data_list.append(w_tp[0])
                    elif (tp_google_valid):
                        data_list.append(data[0]['google_tp'])  # from google
                    elif (tp_cb_valid):
                        data_list.append(data[0]['Phone_Number_cb'])
                    elif ('Tel:_aven' in attribute_keys):
                        print(data[0]['Tel:_aven'])
                        data_list.append(data[0]['Tel:_aven'])
                    elif ('phone_li' in attribute_keys):
                        print(data[0]['phone_li'].split("\n")[0])
                        data_list.append(data[0]['phone_li'].split("\n")[0])
                    elif (len(dnb_tp)):
                        data_list.append(dnb_tp)  # from dnb
                    else:
                        data_list.append("None")
                    data_list[-1] = restructure_tp(data_list[-1])

                    print("selected_tp", data_list[-1])
                    if (data_list[-1] != 'None'):
                        a_conf = get_tp_confidence(data_list[-1], entry_id)
                        print('confidence of selected tp', a_conf)
                        if (a_conf != None):
                            if (a_conf > 0):
                                continue
                            else:
                                all_ads_with_conf = get_every_tp_confidence(entry_id)
                                print('confidence of all tps', all_ads_with_conf)
                                if (all_ads_with_conf != None):
                                    highest_ads_with_conf = all_ads_with_conf[-1:]
                                    print('highest', highest_ads_with_conf)
                                    if (highest_ads_with_conf[0][2] > 0):
                                        data_list[-1] = restructure_tp(highest_ads_with_conf[0][0])
                                        print('updated with highest confidence')
                    # else:
                    #     data_list.append("None")
                except KeyError:
                    data_list.append('None')

            if (each_a == 'keywords'):
                # print("***********kw")
                if (len(data[0]['textrank_results'])):
                    data_list.append(data[0]['textrank_results'][:10])  # from website
                else:
                    data_list.append("None")

            if (each_a == 'contact_person'):
                # print("***********cp")
                # contact_person_fix
                # fix thissssssssssssssssssss********************************************************************************
                try:
                    wb_list = []
                    if ('important_person_company' in attribute_keys):
                        det_wb = data[0]['important_person_company']

                        # print(det_wb)
                        if (det_wb != 'No important persons found'):
                            # wb_list = [det_wb[0]['name'], det_wb[0]['job_title']]
                            wb_list = det_wb[0]

                    li_list = []
                    if (len(data[0]['linkedin_cp_info'])):
                        for each in data[0]['linkedin_cp_info']:
                            data_li = (each[0].split('|')[0]).split('-')
                            if (len(data_li) > 2):
                                # print('li cp',[data_li[0],data_li[1].strip()+'_'+data_li[2].strip()])
                                li_list.append(
                                    [data_li[0], data_li[1].strip() + '_' + data_li[2].strip()])

                    if (len(wb_list)):
                        # print('web')
                        data_list.append(wb_list)  # from google

                    elif ('google_cp' in attribute_keys):
                        # print('g')
                        det_gcp = data[0]['google_cp']
                        # print('gog',det_gcp)
                        data_list.append(det_gcp)  # from google
                    # crunchbase
                    elif ('Founders_cb' in attribute_keys):
                        # print('cb')
                        det_cb = data[0]['Founders_cb']
                        det_cb = [cb.strip() for cb in det_cb.split(',')][0]
                        data_list.append([det_cb, 'founder(s)'])

                    elif ('contacts_aven' in attribute_keys):
                        # print('aven')
                        det_aven = data[0]['contacts_aven'][0]
                        data_list.append(det_aven)

                    elif ('company_contacts_dnb' in attribute_keys):
                        # print('dnb')
                        # print('dnb',data[0]['dnb_cp_info'])
                        # print('dnb',dnb_list[0])
                        det_dnb = data[0]['company_contacts_dnb']
                        data_list.append(det_dnb[0])  # from dnb

                    elif ('directors_or_officers_oc' in attribute_keys):
                        # print('oc')

                        # print('oc',data[0]['oc_cp_info'])
                        oc_cps = []
                        # print(data[0]['directors_or_officers_oc'])
                        for each_oc in [data[0]['directors_or_officers_oc']]:
                            # print(each_oc)
                            oc_det = each_oc.split(',')
                            # print(oc_det)
                            if (len(oc_det) > 1):
                                oc_name = oc_det[0]
                                # print(oc_name)
                                if (len(oc_name) > 1):
                                    oc_post = oc_det[1]
                                    oc_cps.append([oc_name, oc_post])
                            else:
                                oc_cps.append([oc_det, 'agent_' + each_oc[1]])

                        # print('oc',oc_cps[0])
                        data_list.append(oc_cps[0])  # from oc
                    elif ('CEO_g' in attribute_keys):
                        # print('gc')
                        # print('gogq',[data[0]['CEO_g'],'CEO'])
                        data_list.append([data[0]['CEO_g'], 'CEO'])  # from google qa
                    elif ('agent_name_oc' in attribute_keys):
                        # print('oca')
                        # print('oc_ag',[data[0]['agent_name_oc'],'agent'])
                        data_list.append([data[0]['agent_name_oc'][0], 'agent'])  # from oc_agent
                    elif (len(li_list)):

                        data_list.append(li_list[0])  # from linkedin
                        # print('li')
                    else:
                        # print('None')
                        data_list.append("None")

                    print("selected_contact_person", data_list[-1])
                    print('data_list', data_list)
                    if (data_list[-1] != 'None'):
                        a_conf = get_cp_confidence(data_list[-1][0], entry_id)
                        print('confidence of selected cp', a_conf)
                        if (a_conf != None):
                            if (a_conf > 0):
                                continue
                            else:
                                all_ads_with_conf = get_every_cp_confidence(entry_id)
                                print('confidence of all cps', all_ads_with_conf)
                                if (all_ads_with_conf != None):
                                    highest_ads_with_conf = all_ads_with_conf[-1:]
                                    print('highest', highest_ads_with_conf)
                                    if (highest_ads_with_conf[0][3] > 0):
                                        data_list[-1] = [highest_ads_with_conf[0][0],
                                                         highest_ads_with_conf[0][1]]
                                        print('updated with highest confidence')

                except KeyError:
                    data_list.append('None')

            if (each_a == 'type_or_sector'):
                # sector_fix
                # print("***********ty")
                try:
                    if ('Industries_cb' in attribute_keys):
                        print('cb', data[0]['Industries_cb'].split(', ')[:2])
                        data_list.append(data[0]['Industries_cb'].split(', ')[:2])
                    elif ('Industry:_aven' in attribute_keys):
                        print('aven', data[0]['Industry:_aven'])
                        data_list.append([data[0]['Industry:_aven']])
                    elif ('industry_li' in attribute_keys):
                        print('li', data[0]['industry_li'])
                        data_list.append([data[0]['industry_li']])  # from linkedin
                    elif ('comp_type_pred' in attribute_keys):
                        print('clas', data[0]['comp_type_pred'][0])
                        data_list.append(
                            [data[0]['comp_type_pred'][0][0] + ', ' + data[0]['comp_type_pred'][1][
                                0]])  # from classification
                    else:
                        data_list.append("None")

                except KeyError:
                    data_list.append('None')

            if (each_a == 'founded_year'):
                # fy_fix
                # print("***********fy")
                try:
                    if ('Founded_Date_cb' in attribute_keys):
                        # print('cb',data[0]['Founded Date_cb'])
                        data_list.append(data[0]['Founded_Date_cb'])  # from linkedin
                    elif ('founded_li' in attribute_keys):
                        # print('li',data[0]['founded_li'])
                        data_list.append(data[0]['founded_li'])  # from linkedin
                    elif ('incorporation_date_oc' in attribute_keys):
                        # print('oc', data[0]['incorporation_date_oc'].split(' (')[0])
                        data_list.append(data[0]['incorporation_date_oc'].split(' (')[0])  # from oc
                    elif ('founded_year_g' in attribute_keys):
                        # print('g', data[0]['founded_year_g'])
                        data_list.append(data[0]['founded_year_g'])  # from google
                    else:
                        data_list.append("None")

                    # if ('Industries_cb' in attribute_keys):
                    #     print('cb',data[0]['Industries_cb'].split(', ')[:2])
                    #     data_list.extend(data[0]['Industries_cb'].split(', ')[:2])
                    # elif ('industry_li' in attribute_keys):
                    #     print('li',data[0]['industry_li'])
                    #     data_list.extend([data[0]['industry_li']])  # from linkedin
                    # elif ('comp_type_pred' in attribute_keys):
                    #     print('clas',data[0]['comp_type_pred'][0])
                    #     data_list.extend([data[0]['comp_type_pred'][0][0]+', '+ data[0]['comp_type_pred'][1][0]])  # from classification
                    # else:
                    #     data_list.append("None")

                except KeyError:
                    data_list.append('None')

            if (each_a == 'revenue'):
                # rev_fix
                # print("***********rv")
                try:
                    rev_d = []
                    if ('company_revenue_dnb' in attribute_keys):
                        if (len(data[0]['company_revenue_dnb'])):
                            rev_d = data[0]['company_revenue_dnb']
                    if ('Annual_Sales:_aven' in attribute_keys):
                        # print('g')
                        data_list.append(data[0]['Annual_Sales:_aven'])  # from google
                    elif ('revenue_g' in attribute_keys):
                        # print('g')
                        data_list.append(data[0]['revenue_g'])  # from google
                    elif (len(rev_d)):
                        # print('d')
                        a_rev = rev_d[0].split('|')[1]
                        print(a_rev)
                        data_list.append(a_rev)  # from dnb
                    else:
                        data_list.append("None")
                    # if ('Contact Email_cb' in attribute_keys):
                    #     data_list = data[0]['Contact Email_cb']
                    # elif (len(data[0]['emails'])):
                    #     data_list.append(data[0]['emails'][0])  # from website
                    # else:
                    #     data_list.append("None")
                    # # else:
                    # #     data_list.append("None")
                except KeyError:
                    data_list.append('None')

            if (each_a == 'funding'):
                # print("***********f")
                if ('funding_g' in attribute_keys):
                    data_list.append(data[0]['funding_g'])  # from google
                else:
                    data_list.append("None")

            if (each_a == 'headquarters'):
                # hq_fix
                # print("***********hq")
                try:
                    hq_cb, hq_g, hq_li, j_oc = '', '', '', ''
                    if ('comp_headquaters_cb' in attribute_keys):
                        hq_cb = data[0]['comp_headquaters_cb']

                    if ('headquarters_li' in attribute_keys):
                        hq_li = data[0]['headquarters_li']

                    if ('jurisdiction_oc' in attribute_keys):
                        j_oc = data[0]['jurisdiction_oc']

                    if ('headquarters_g' in attribute_keys):
                        hq_g = data[0]['headquarters_g']

                    if (isvalid_hq(hq_cb)):
                        data_list.append(hq_cb)
                    elif (isvalid_hq(hq_li)):
                        data_list.append(hq_li)
                    elif (isvalid_hq(hq_g)):
                        data_list.append(hq_g)
                    elif (isvalid_hq(j_oc)):
                        data_list.append(j_oc)
                    else:
                        data_list.append("None")
                    # else:
                    #     data_list.append("None")

                    if (data_list[-1] != 'None'):
                        a_conf = get_hq_confidence(data_list[-1], entry_id)
                        print('confidence of selected hq', a_conf)
                        if (a_conf != None):
                            if (a_conf > 0):
                                continue
                            else:
                                all_ads_with_conf = get_every_hq_confidence(entry_id)
                                print('confidence of all hqs', all_ads_with_conf)
                                if (all_ads_with_conf != None):
                                    highest_ads_with_conf = all_ads_with_conf[-1:]
                                    print('highest', highest_ads_with_conf)
                                    if (highest_ads_with_conf[0][2] > 0):
                                        data_list[-1] = highest_ads_with_conf[0][0]
                                        print('updated with highest confidence')
                except KeyError:
                    data_list.append('None')

            if (each_a == 'No_of_employees'):
                # fix_ne
                # print("***********ne")
                try:
                    data_lil = None
                    if ('company_size_li' in attribute_keys):
                        if (data[0]['company_size_li'] != None):
                            if (' employees' in data[0]['company_size_li']):
                                data_lil = data[0]['company_size_li'].replace(' employees', '')
                    if ('Number_of_Employees_cb' in attribute_keys):
                        # print('cb')
                        data_list.append(data[0]['Number_of_Employees_cb'])  # from company_size_li
                    elif ('Employees_(All_Sites):_aven' in attribute_keys):
                        data_list.append(data[0]['Employees_(All_Sites):_aven'])
                    elif (data_lil != None):
                        data_list.append(data_lil)  # from company_size_li

                    elif ('num_employees_li' in attribute_keys):
                        # print('li')
                        data_list.append(
                            str(data[0]['num_employees_li']).split("\n")[0])  # from linkedin
                    elif ('no_of_employees_g' in attribute_keys):
                        # print('g')
                        data_list.append(data[0]['no_of_employees_g'])  # from googlecompany_size_li
                    else:
                        data_list.append("None")
                    # else:
                    #     data_list.append("None")
                except KeyError:
                    data_list.append('None')



            if (each_a == 'company_status'):
                # fix_cs

                try:
                    if ('IPO_Status_cb' in attribute_keys):
                        # print('cb', data[0]['IPO_Status_cb'])
                        data_list.append(data[0]['IPO_Status_cb'])
                    elif ('Company_Type:_aven' in attribute_keys):
                        # print('aven', data[0]['Company_Type:_aven'])
                        data_list.append(data[0]['Company_Type:_aven'])
                    elif ('company_type_dnb' in attribute_keys):
                        # print('dnb', data[0]['company_type_dnb'][0].split(': ')[1])
                        data_list.append(data[0]['company_type_dnb'][0].split(': ')[1])
                    elif ('company_type_oc' in attribute_keys):
                        # print('oc', data[0]['company_type_oc'])
                        data_list.append(data[0]['company_type_oc'])
                    else:
                        data_list.append("None")
                    # else:
                    #     data_list.append("None")
                except KeyError:
                    data_list.append('None')

        except KeyError:
            data_list.append('None')
        except Exception as e:
            data_list.append('None')
            print("Exception Occured during dumping ", e)

    return data_list


# clear_the_collection()
def simplified_export_via_queue():
    print("Simplified export queue is live")
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    query_collection = refer_query_col()
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    simplified_dump_client = QueueClient.from_connection_string(connect_str, "simplified-dump-queue")
    simplified_s_c_dump_client = QueueClient.from_connection_string(connect_str, "simplified-s-c-queue")

    attributes_a = ['_id', 'search_text', 'title', 'link', 'description', 'comp_name',
                    'address', 'email','telephone_number', 'keywords','contact_person', 'type_or_sector', 'founded_year',
                    'revenue','funding','headquarters','No_of_employees','company_status']

    # results_writer.writerow(attributes_a)
    while (True):
        time.sleep(10)
        rows = simplified_dump_client.receive_messages()
        for msg in rows:
            time.sleep(10)
            row = msg.content
            row = ast.literal_eval(row)
            print('profile dumping',row[0])
            entry_id = ObjectId(row[0])
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            #check_for_the_completion_of_components
            # print(data[0]['deep_crawling_state'],data[0]['feature_extraction_state'],data[0]['classification_state'],data[0]['owler_qa_state'],data[0]['li_cp_state'],data[0]['google_cp_state'],data[0]['oc_extraction_state'],data[0]['google_address_state'],data[0]['dnb_extraction_state'],data[0]['google_tp_state'])
            try:
                # if (data[0]['deep_crawling_state'] == data[0]['feature_extraction_state'] == data[0][
                #     'classification_state'] == data[0]['owler_qa_state'] == data[0]['li_cp_state'] == data[0][
                #     'google_cp_state'] == data[0]['oc_extraction_state'] == data[0]['google_address_state'] == data[0][
                #     'dnb_extraction_state'] == data[0]['google_tp_state'] ==  data[0]['crunchbase_extraction_state'] == 'Completed'):

                if(data[0]['deep_crawling_state']==data[0]['feature_extraction_state']==data[0]['classification_state']==data[0]['owler_qa_state']==data[0]['li_cp_state']==data[0]['google_cp_state']==data[0]['oc_extraction_state']==data[0]['google_address_state']==data[0]['dnb_extraction_state']==data[0]['google_tp_state']=='Completed'):
                    data_list = []
                    data_list.extend([data[0]['_id'], data[0]['search_text'], data[0]['title'], data[0]['link'],
                                      data[0]['description'], data[0]['comp_name']])

                    # print(attribute_keys)
                    data_list.extend(get_data_for_simplified_dump_based_on_source_order(entry_id))

                    dict_to_dump = {}
                    for i in range(len(attributes_a)):
                        dict_to_dump[attributes_a[i]] = data_list[i]

                    print('dumping dict',dict_to_dump)
                    if('public' in dict_to_dump['company_status'].lower()):
                        print('This is public company so adding to ignore list')
                        adding_ig([dict_to_dump['_id']])

                    record_entry = csv_dump_col.insert_one(dict_to_dump)
                    print("simplified dump completed", record_entry.inserted_id)
                    simplified_dump_client.delete_message(msg)
                    mycol.update_one({'_id': entry_id},
                                     {'$set': {'simplified_dump_state': 'Completed'}})
                    print("Adding message to type prediction queue")
                    simplified_s_c_dump_client.send_message([str(entry_id)], time_to_live=-1)
                    mycol.update_one({'_id': entry_id},
                                      {'$set': {'simplified_dump_s_c_state': 'Incomplete'}})
                    query_id = data[0]['query_id']
                    q_data_entry = query_collection.find({"_id": query_id})
                    q_data = [i for i in q_data_entry]
                    started = q_data[0]['started_time_stamp']
                    ended = datetime.now()

                    duration = ended - started
                    time_difference_in_minutes = duration / timedelta(minutes=1)

                    completion_data = {'completed_time_stamp': ended, 'elapsed_time': time_difference_in_minutes}
                    print(completion_data)
                    query_collection.update_one({'_id': query_id},
                                                {'$set': completion_data})
                    print("Pipeline execution completed, elapsed time(minutes):", time_difference_in_minutes)
            except pymongo.errors.DuplicateKeyError:
                print('Already Existing')
                csv_dump_col.update_one({'_id': entry_id},
                                 {'$set': dict_to_dump})
                simplified_dump_client.delete_message(msg)
            except KeyError as e:
                print('key not found',e)
            except IndexError as e:
                print('yet raw entry not available')
            except Exception as e:
                print("Exception Occured during dumping ",e)


            # for k in data[0].keys():
            #     print(k)
            # print(data)



def add_to_simplified_export_queue(id_list):
    mycol = refer_collection()
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    simplified_dump_client = QueueClient.from_connection_string(connect_str, "simplified-dump-queue")
    for each_id in id_list:
        print(each_id)
        mycol.update_one({'_id': each_id},
                         {'$set': {'simplified_dump_state': 'Incomplete'}})
        simplified_dump_client.send_message([str(each_id)], time_to_live=-1)

def add_to_s_c_export_queue(id_list):
    mycol = refer_collection()
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    simplified_s_c_dump_client = QueueClient.from_connection_string(connect_str, "simplified-s-c-queue")

    for each_id in id_list:
        print(each_id)
        mycol.update_one({'_id': each_id},
                         {'$set': {'simplified_dump_s_c_state': 'Incomplete'}})
        simplified_s_c_dump_client.send_message([str(each_id)], time_to_live=-1)



def simplified_export(id_list,output_path):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    # store data in a csv file
    # dump_name = 'F:\Armitage_project\crawl_n_depth\Simplified_System\end_to_end\data_dump\\' + str(
    #     id_list[0]) + '_company_dump_simplified.csv'
    dump_name = output_path
    with open(dump_name, mode='w', encoding='utf8',
              newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        attributes_a = ['_id', 'search_text', 'title', 'link', 'description', 'comp_name',
                        'address', 'email','telephone_number', 'keywords','contact_person', 'type_or_sector', 'founded_year',
                        'revenue','funding','headquarters','No_of_employees','company_status']
        results_writer.writerow(attributes_a)
        for entry_id in id_list:
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            # for k in data[0].keys():
            #     print(k)
            # print(data)
            data_list = []
            data_list.extend([data[0]['_id'],data[0]['search_text'],data[0]['title'],data[0]['link'],data[0]['description'],data[0]['comp_name']])
            data_list.extend(get_data_for_simplified_dump_based_on_source_order(entry_id))

            results_writer.writerow(data_list)
            # dict_to_dump = {}
            # for i in range(len(attributes_a)):
            #     dict_to_dump[attributes_a[i]] = data_list[i]
            # print(dict_to_dump)
            # record_entry = csv_dump_col.insert_one(dict_to_dump)
            print("simplified dump completed")
        results_file.close()
    print("CSV export completed!")
    # return  results_file



def simplified_update(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    # store data in a csv file
    dump_name = 'C:\\Project_files\\Armitage_project\\crawl_n_depth\\Simplified_System\\dumps' + str(
        id_list[0]) + '_company_dump_simplified.csv'
    with open(dump_name, mode='w', encoding='utf8',
              newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        attributes_a = ['search_text', 'title', 'link', 'description', 'comp_name',
                        'address', 'email','telephone_number', 'keywords','contact_person', 'type_or_sector', 'founded_year',
                        'revenue','funding','headquarters','No_of_employees','company_status']
        results_writer.writerow(attributes_a)
        for entry_id in id_list:
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]

            data_list = []
            data_list.extend([data[0]['search_text'],data[0]['title'],data[0]['link'],data[0]['description'],data[0]['comp_name']])
            data_list.extend(get_data_for_simplified_dump_based_on_source_order(entry_id))

            results_writer.writerow(data_list)
            dict_to_dump = {}
            for i in range(len(attributes_a)):
                dict_to_dump[attributes_a[i]] = data_list[i]
            print(dict_to_dump)

            # record_entry = csv_dump_col.insert_one(dict_to_dump)
            csv_dump_col.update_one({'_id': entry_id}, {'$set': dict_to_dump})
            print("simplified dump updated")
        results_file.close()
    print("CSV export completed!")

def simplified_export_with_sources(id_list,output_path):
    print('simplified export with sources')
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    # store data in a csv file
    # dump_name = 'F:\\from git\\Armitage_project\\crawl_n_depth\\Simplified_System\\dumps\\' + 'new_companies_with_sources.csv'
    dump_name = output_path
    with open(dump_name, mode='w', encoding='utf8',
              newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        attributes_a = ['search_text', 'title', 'link', 'description', 'comp_name',
                        'address', 'email','telephone_number', 'keywords','contact_person', 'type_or_sector', 'founded_year',
                        'revenue','funding','headquarters','No_of_employees','company_status']
        results_writer.writerow(attributes_a)
        for entry_id in id_list:
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            my_link = data[0]['link']
            # for k in data[0].keys():
            #     print(k)
            # print(data)
            data_list = []
            data_list.extend([data[0]['search_text'],data[0]['title'],data[0]['link'],data[0]['description'],data[0]['comp_name']])
            attribute_keys = list(data[0].keys())

            if ('google_tp_source' in attribute_keys):google_tp_source = data[0]['google_tp_source']
            else:google_tp_source = 'None'

            if ('google_cp_source' in attribute_keys):google_cp_source = data[0]['google_cp_source']
            else:google_cp_source = 'None'

            if ('google_address_source' in attribute_keys):google_address_source = data[0]['google_address_source']
            else:google_address_source = 'None'

            if ('link_dnb' in attribute_keys):link_dnb = data[0]['link_dnb']
            else:link_dnb = 'None'

            if ('link_cb' in attribute_keys):link_cb = data[0]['link_cb']
            else:link_cb = 'None'

            if ('li_url' in attribute_keys):link_li = data[0]['li_url']
            else:link_li = 'None'

            if ('site_url_oc' in attribute_keys):site_url_oc = data[0]['site_url_oc']
            else:site_url_oc = 'None'

            if ('link_owler' in attribute_keys):link_owler = data[0]['link_owler']
            else:link_owler = 'None'

            if('comp_url_aven' in attribute_keys):
                if('https://app.avention.com' not in data[0]['comp_url_aven']):
                    link_aven = 'https://app.avention.com'+data[0]['comp_url_aven']
                else:
                    link_aven =data[0]['comp_url_aven']
            else:link_aven = 'None'

            # print(attribute_keys)
            for each_a in attributes_a:
                try:
                    if(each_a == 'address'):
                        #address_fix
                        try:
                            g_add, w_ad, dnb_add, oc_add = '', '', '', ''
                            if ('google_address' in attribute_keys):
                                if (len(data[0]['google_address'])):
                                    g_add = data[0]['google_address']
                            if (len(data[0]['website_addresses_with_sources'])):
                                for each in data[0]['website_addresses_with_sources']:
                                    if (isvalid_hq(each[0])):
                                        w_ad = each
                                        break
                            if ('company_address_dnb' in attribute_keys):
                                if (len(data[0]['company_address_dnb'])):
                                    dnb_add = data[0]['company_address_dnb'][0]
                            if ('registered_address_adr_oc' in attribute_keys):
                                oc_add = data[0]['registered_address_adr_oc']
                            aven_add = ''
                            if ('address_aven' in attribute_keys):
                                aven_add = data[0]['address_aven']

                            if (len(w_ad) != 0):
                                # print('w')
                                data_list.append([w_ad[0],w_ad[1]])
                            elif (isvalid_hq(g_add)):
                                # print('g')
                                data_list.append([g_add,google_address_source])  # from google
                            elif (isvalid_hq(aven_add)):
                                # print('d')
                                data_list.append([aven_add,link_aven])
                            elif (isvalid_hq(dnb_add)):
                                # print('d')
                                data_list.append([dnb_add,link_dnb])
                            elif (isvalid_hq(oc_add.lower())):
                                # print('o')
                                data_list.append([oc_add,site_url_oc])
                            else:
                                data_list.append('None')

                            print("selected_address", data_list[-1])
                            if (data_list[-1] != 'None'):
                                a_conf = get_address_confidence(data_list[-1][0], entry_id)
                                print('confidence of selected address', a_conf)
                                if (a_conf != None):
                                    if (a_conf > 0):
                                        continue
                                    else:
                                        all_ads_with_conf = get_every_address_confidence(entry_id)
                                        print('confidence of all addresses', all_ads_with_conf)
                                        if (all_ads_with_conf != None):
                                            highest_ads_with_conf = all_ads_with_conf[-1:]
                                            print('highest', highest_ads_with_conf)
                                            if (highest_ads_with_conf[0][2] > 0):
                                                if(highest_ads_with_conf[0][1]=='google'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0],google_address_source]
                                                if (highest_ads_with_conf[0][1] =='website'):
                                                    for each in data[0]['website_addresses_with_sources']:
                                                        if (each[0]==highest_ads_with_conf[0][0]):
                                                            w_ad = each
                                                            break
                                                    data_list[-1] = w_ad
                                                if (highest_ads_with_conf[0][1] == 'dnb'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], link_dnb]
                                                if (highest_ads_with_conf[0][1] == 'oc'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], site_url_oc]
                                                if (highest_ads_with_conf[0][1] == 'avention'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], link_aven]


                                                print('updated with highest confidence')

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'email'):
                        # print("***********eml")
                        #email_fix
                        try:
                            if ('Contact_Email_cb' in attribute_keys):
                                data_list.append([data[0]['Contact_Email_cb'],link_cb])
                            elif (len(data[0]['emails_with_sources'])):
                                data_list.append([data[0]['emails_with_sources'][0][0],data[0]['emails_with_sources'][0][1]])  # from website
                            else:
                                data_list.append("None")
                            # else:
                            #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'telephone_number'):
                        # print("***********tp")
                        #tp_fix
                        try:
                            tp_cb_valid = False
                            if ('Phone_Number_cb' in attribute_keys):
                                # print('cb',data[0]['Phone_Number_cb'])
                                if (is_valid_tp(data[0]['Phone_Number_cb'])):
                                    tp_cb_valid = True
                            tp_google_valid = False
                            if ('google_tp' in attribute_keys):
                                # print('cb',data[0]['Phone_Number_cb'])
                                if (is_valid_tp(data[0]['google_tp'])):
                                    tp_google_valid = True
                            dnb_tp = []
                            if ('company_tp_dnb' in attribute_keys):
                                dnb_tp = data[0]['company_tp_dnb']  # from dnb
                                # print(data_list,type(data_list))
                            w_tp = []
                            if (len(data[0]['telephone_numbers_with_sources'])):
                                plus_t = []
                                s_six = []
                                other_t = []
                                for each_tl in data[0]['telephone_numbers_with_sources']:
                                    each_t = each_tl[0]
                                    if (each_t[:3] in ['+61', '+64']):
                                        if (is_valid_tp(each_t)):
                                            plus_t.append(each_tl)
                                    if (each_t[:2] in ['61', '64']):
                                        if (is_valid_tp(each_t)):
                                            s_six.append(each_tl)
                                    if ((each_t[0] in ['0']) or (each_t[:4] in ['1300', '1800', '0800'])):
                                        if (is_valid_tp(each_t)):
                                            other_t.append(each_tl)
                                w_tp = plus_t + s_six + other_t

                            if (len(w_tp)):
                                data_list.append([w_tp[0][0], w_tp[0][1]])
                            elif (tp_google_valid):
                                data_list.append([data[0]['google_tp'],google_tp_source])  # from google
                            elif (tp_cb_valid):
                                data_list.append([data[0]['Phone_Number_cb'],link_cb])
                            elif ('Tel:_aven' in attribute_keys):
                                # print(data[0]['Tel:_aven'])
                                data_list.append([data[0]['Tel:_aven'],link_aven])
                            elif ('phone_li' in attribute_keys):
                                # print(data[0]['phone_li'].split("\n")[0])
                                data_list.append([data[0]['phone_li'].split("\n")[0],link_li])
                            elif (len(dnb_tp)):
                                data_list.append([dnb_tp,link_dnb])  # from dnb
                            else:
                                data_list.append("None")

                            if(len(data_list[-1])==2):
                                data_list[-1][0] = restructure_tp(data_list[-1][0])
                            # print(data_list[-1])

                            # else:
                            #     data_list.append("None")
                            print("selected_tp", data_list[-1])
                            if (data_list[-1] != 'None'):
                                a_conf = get_tp_confidence(data_list[-1][0], entry_id)
                                print('confidence of selected tp', a_conf)
                                if (a_conf != None):
                                    if (a_conf > 0):
                                        continue
                                    else:
                                        all_ads_with_conf = get_every_tp_confidence(entry_id)
                                        print('confidence of all tps', all_ads_with_conf)
                                        if (all_ads_with_conf != None):
                                            highest_ads_with_conf = all_ads_with_conf[-1:]
                                            print('highest', highest_ads_with_conf)
                                            if (highest_ads_with_conf[0][2] > 0):
                                                if (highest_ads_with_conf[0][1] == 'google'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], google_tp_source]
                                                if (highest_ads_with_conf[0][1] == 'website'):
                                                    for each in data[0]['telephone_numbers_with_sources']:
                                                        if (each[0] == highest_ads_with_conf[0][0]):
                                                            w_ad = each
                                                            break
                                                    data_list[-1] = w_ad
                                                if (highest_ads_with_conf[0][1] == 'crunchbase'):
                                                    data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_cb]
                                                if (highest_ads_with_conf[0][1] == 'dnb'):
                                                    data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_dnb]
                                                if (highest_ads_with_conf[0][1] == 'linkein'):
                                                    data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_li]
                                                if (highest_ads_with_conf[0][1] == 'avention'):
                                                    data_list[-1] = [restructure_tp(highest_ads_with_conf[0][0]), link_aven]



                                                print('updated with highest confidence')
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'keywords'):
                        # print("***********kw")
                        if (len(data[0]['textrank_results'])):data_list.append(data[0]['textrank_results'][:10])  # from website
                        else:data_list.append("None")

                    if (each_a == 'contact_person'):
                        # print("***********cp")
                        #contact_person_fix
                        #fix thissssssssssssssssssss********************************************************************************
                        try:
                            wb_list = []
                            if ('important_person_company' in attribute_keys):
                                det_wb = data[0]['important_person_company']

                                # print(det_wb)
                                if (det_wb != 'No important persons found'):
                                    # wb_list = [det_wb[0]['name'], det_wb[0]['job_title']]
                                    wb_list = det_wb[0]

                            li_list = []
                            if (len(data[0]['linkedin_cp_info'])):
                                for each in data[0]['linkedin_cp_info']:
                                    data_li = (each[0].split('|')[0]).split('-')
                                    if (len(data_li) > 2):
                                        # print('li cp',[data_li[0],data_li[1].strip()+'_'+data_li[2].strip()])
                                        li_list.append([data_li[0], data_li[1].strip() + '_' + data_li[2].strip()])

                            if (len(wb_list)):
                                # print('g')
                                data_list.append([wb_list,'from_website'])  # from google

                            elif ('google_cp' in attribute_keys):
                                # print('g')
                                det_gcp = data[0]['google_cp']
                                # print('gog',det_gcp)
                                data_list.append([det_gcp,google_cp_source])  # from google
                            # crunchbase
                            elif ('Founders_cb' in attribute_keys):
                                det_cb = data[0]['Founders_cb']
                                det_cb = [cb.strip() for cb in det_cb.split(',')][0]
                                data_list.append([det_cb, 'founder(s)',link_cb])

                            elif ('contacts_aven' in attribute_keys):
                                det_aven = data[0]['contacts_aven'][0]
                                data_list.append([det_aven,link_aven])

                            elif ('company_contacts_dnb' in attribute_keys):
                                # print('dnb',data[0]['dnb_cp_info'])
                                # print('dnb',dnb_list[0])
                                det_dnb = data[0]['company_contacts_dnb']
                                data_list.append([det_dnb[0],link_dnb])  # from dnb

                            elif ('directors_or_officers_oc' in attribute_keys):
                                # print('oc')

                                # print('oc',data[0]['oc_cp_info'])
                                oc_cps = []
                                # print(data[0]['directors_or_officers_oc'])
                                for each_oc in [data[0]['directors_or_officers_oc']]:
                                    # print(each_oc)
                                    oc_det = each_oc.split(',')
                                    # print(oc_det)
                                    if (len(oc_det) > 1):
                                        oc_name = oc_det[0]
                                        # print(oc_name)
                                        if (len(oc_name) > 1):
                                            oc_post = oc_det[1]
                                            oc_cps.append([oc_name, oc_post])
                                    else:
                                        oc_cps.append([oc_det, 'agent_' + each_oc[1]])

                                # print('oc',oc_cps[0])
                                data_list.append([oc_cps[0],site_url_oc])  # from oc
                            elif ('CEO_g' in attribute_keys):
                                # print('gc')
                                # print('gogq',[data[0]['CEO_g'],'CEO'])
                                data_list.append([data[0]['CEO_g'], 'CEO',link_owler])  # from google qa
                            elif ('agent_name_oc' in attribute_keys):
                                # print('oca')
                                # print('oc_ag',[data[0]['agent_name_oc'],'agent'])
                                data_list.append([data[0]['agent_name_oc'][0], 'agent',site_url_oc])  # from oc_agent
                            elif (len(li_list)):

                                data_list.append([li_list[0],'from linkedin search google'])  # from linkedin
                                # print('*****')
                            else:
                                # print('None')
                                data_list.append("None")

                            print("selected_contact_person", data_list[-1])
                            if (data_list[-1] != 'None'):
                                if(len(data_list[-1][0])==2):
                                    a_conf = get_cp_confidence(data_list[-1][0][0], entry_id)
                                else:
                                    a_conf = get_cp_confidence(data_list[-1][0], entry_id)
                                print('confidence of selected cp', a_conf)
                                if (a_conf != None):
                                    if (a_conf > 0):
                                        continue
                                    else:
                                        all_ads_with_conf = get_every_cp_confidence(entry_id)
                                        print('confidence of all cps', all_ads_with_conf)
                                        if (all_ads_with_conf != None):
                                            highest_ads_with_conf = all_ads_with_conf[-1:]
                                            print('highest', highest_ads_with_conf)
                                            if (highest_ads_with_conf[0][3] > 0):
                                                if (highest_ads_with_conf[0][2] == 'google'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], google_cp_source]
                                                if (highest_ads_with_conf[0][2] == 'website'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], 'website']
                                                if (highest_ads_with_conf[0][2] == 'crunchbase'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], link_cb]
                                                if (highest_ads_with_conf[0][2] == 'dnb'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], link_dnb]
                                                if (highest_ads_with_conf[0][2] == 'oc'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], site_url_oc]
                                                if (highest_ads_with_conf[0][2] == 'owler'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], link_owler]
                                                if (highest_ads_with_conf[0][2] == 'linkedin'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], link_li]
                                                if (highest_ads_with_conf[0][2] == 'avention'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0:2], link_aven]

                                                print('updated with highest confidence')

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'type_or_sector'):
                        #sector_fix
                        # print("***********ty")
                        try:
                            if ('Industries_cb' in attribute_keys):
                                # print('cb', data[0]['Industries_cb'].split(', ')[:2])
                                data_list.append([data[0]['Industries_cb'].split(', ')[:2],link_cb])
                            elif ('Industry:_aven' in attribute_keys):
                                # print('aven', data[0]['Industry:_aven'])
                                data_list.append([data[0]['Industry:_aven'],link_aven])
                            elif ('industry_li' in attribute_keys):
                                # print('li', data[0]['industry_li'])
                                data_list.append([data[0]['industry_li'],link_li])  # from linkedin
                            elif ('comp_type_pred' in attribute_keys):
                                # print('clas', data[0]['comp_type_pred'][0])
                                data_list.append([data[0]['comp_type_pred'][0][0] + ', ' + data[0]['comp_type_pred'][1][
                                    0],'from_classification_model'])  # from classification
                            else:
                                data_list.append("None")

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'founded_year'):
                        #fy_fix
                        # print("***********fy")
                        try:
                            if ('Founded_Date_cb' in attribute_keys):
                                # print('cb',data[0]['Founded Date_cb'])
                                data_list.append([data[0]['Founded_Date_cb'],link_cb])  # from linkedin
                            elif ('founded_li' in attribute_keys):
                                # print('li',data[0]['founded_li'])
                                data_list.append([data[0]['founded_li'],link_li])  # from linkedin
                            elif ('incorporation_date_oc' in attribute_keys):
                                # print('oc', data[0]['incorporation_date_oc'].split(' (')[0])
                                data_list.append([data[0]['incorporation_date_oc'].split(' (')[0],site_url_oc])  # from oc
                            elif ('founded_year_g' in attribute_keys):
                                # print('g', data[0]['founded_year_g'])
                                data_list.append([data[0]['founded_year_g'],link_owler])  # from google
                            else:
                                data_list.append("None")
                            # if ('Industries_cb' in attribute_keys):
                            #     print('cb',data[0]['Industries_cb'].split(', ')[:2])
                            #     data_list.extend(data[0]['Industries_cb'].split(', ')[:2])
                            # elif ('industry_li' in attribute_keys):
                            #     print('li',data[0]['industry_li'])
                            #     data_list.extend([data[0]['industry_li']])  # from linkedin
                            # elif ('comp_type_pred' in attribute_keys):
                            #     print('clas',data[0]['comp_type_pred'][0])
                            #     data_list.extend([data[0]['comp_type_pred'][0][0]+', '+ data[0]['comp_type_pred'][1][0]])  # from classification
                            # else:
                            #     data_list.append("None")

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'revenue'):
                        #rev_fix
                        # print("***********rv")
                        try:
                            rev_d = []
                            if ('company_revenue_dnb' in attribute_keys):
                                if (len(data[0]['company_revenue_dnb'])):
                                    rev_d = data[0]['company_revenue_dnb']
                            if ('Annual_Sales:_aven' in attribute_keys):
                                # print('g')
                                data_list.append([data[0]['Annual_Sales:_aven'],link_aven])  # from google
                            elif ('revenue_g' in attribute_keys):
                                # print('g')
                                data_list.append([data[0]['revenue_g'],link_owler])  # from google
                            elif (len(rev_d)):
                                # print('d')
                                a_rev = rev_d[0].split('|')[1]
                                print(a_rev)
                                data_list.append([a_rev,link_dnb])  # from dnb
                            else:
                                data_list.append("None")
                            # if ('Contact Email_cb' in attribute_keys):
                            #     data_list = data[0]['Contact Email_cb']
                            # elif (len(data[0]['emails'])):
                            #     data_list.append(data[0]['emails'][0])  # from website
                            # else:
                            #     data_list.append("None")
                            # # else:
                            # #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'funding'):
                        # print("***********f")
                        if ('funding_g' in attribute_keys):data_list.append([data[0]['funding_g'],link_owler])  # from google
                        else:data_list.append("None")

                    if (each_a == 'headquarters'):
                        #hq_fix
                        # print("***********hq")
                        try:
                            hq_cb, hq_g, hq_li, j_oc = '', '', '', ''
                            if ('comp_headquaters_cb' in attribute_keys):
                                hq_cb = data[0]['comp_headquaters_cb']

                            if ('headquarters_li' in attribute_keys):
                                hq_li = data[0]['headquarters_li']

                            if ('jurisdiction_oc' in attribute_keys):
                                j_oc = data[0]['jurisdiction_oc']

                            if ('headquarters_g' in attribute_keys):
                                hq_g = data[0]['headquarters_g']

                            if (isvalid_hq(hq_cb)):
                                data_list.append([hq_cb,link_cb])
                            elif (isvalid_hq(hq_li)):
                                data_list.append([hq_li,link_li])
                            elif (isvalid_hq(hq_g)):
                                data_list.append([hq_g,link_owler])
                            elif (isvalid_hq(j_oc)):
                                data_list.append([j_oc,site_url_oc])
                            else:
                                data_list.append("None")
                            # else:
                            #     data_list.append("None")

                            if (data_list[-1] != 'None'):
                                a_conf = get_hq_confidence(data_list[-1][0], entry_id)
                                print('confidence of selected hq', a_conf)
                                if (a_conf != None):
                                    if (a_conf > 0):
                                        continue
                                    else:
                                        all_ads_with_conf = get_every_hq_confidence(entry_id)
                                        print('confidence of all hqs', all_ads_with_conf)
                                        if (all_ads_with_conf != None):
                                            highest_ads_with_conf = all_ads_with_conf[-1:]
                                            print('highest', highest_ads_with_conf)
                                            if (highest_ads_with_conf[0][2] > 0):
                                                if (highest_ads_with_conf[0][1] == 'crunchbase'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], link_cb]
                                                if (highest_ads_with_conf[0][1] == 'oc'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], site_url_oc]
                                                if (highest_ads_with_conf[0][1] == 'owler'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], link_owler]
                                                if (highest_ads_with_conf[0][1] == 'linkedin'):
                                                    data_list[-1] = [highest_ads_with_conf[0][0], link_li]

                                                print('updated with highest confidence')


                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'No_of_employees'):
                        #fix_ne
                        # print("***********ne")
                        try:
                            data_lil = None
                            if ('company_size_li' in attribute_keys):
                                if (data[0]['company_size_li'] != None):
                                    if (' employees' in data[0]['company_size_li']):
                                        data_lil = data[0]['company_size_li'].replace(' employees', '')
                            if ('Number_of_Employees_cb' in attribute_keys):
                                # print('cb')
                                data_list.append([data[0]['Number_of_Employees_cb'],link_cb])  # from company_size_li
                            elif ('Employees_(All_Sites):_aven' in attribute_keys):
                                data_list.append([data[0]['Employees_(All_Sites):_aven'],link_aven])
                            elif (data_lil != None):
                                data_list.append([data_lil,link_li])  # from company_size_li

                            elif ('num_employees_li' in attribute_keys):
                                # print('li')
                                data_list.append([str(data[0]['num_employees_li']).split("\n")[0],link_li])  # from linkedin
                            elif ('no_of_employees_g' in attribute_keys):
                                # print('g')
                                data_list.append([data[0]['no_of_employees_g'],link_owler])  # from googlecompany_size_li
                            else:
                                data_list.append("None")
                            # else:
                            #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'company_status'):
                        # fix_cs

                        try:
                            if ('IPO_Status_cb' in attribute_keys):
                                # print('cb', data[0]['IPO_Status_cb'])
                                data_list.append([data[0]['IPO_Status_cb'],link_cb])
                            elif ('Company_Type:_aven' in attribute_keys):
                                # print('aven', data[0]['Company_Type:_aven'])
                                data_list.append([data[0]['Company_Type:_aven'],link_aven])
                            elif ('company_type_dnb' in attribute_keys):
                                # print('dnb', data[0]['company_type_dnb'][0].split(': ')[1])
                                data_list.append([data[0]['company_type_dnb'][0].split(': ')[1],link_dnb])
                            elif ('company_type_oc' in attribute_keys):
                                # print('oc', data[0]['company_type_oc'])
                                data_list.append([data[0]['company_type_oc'],site_url_oc])
                            else:
                                data_list.append("None")
                            # else:
                            #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')
                except KeyError:
                    data_list.append('None')
                except Exception as e:
                    data_list.append('None')
                    print("Exception Occured during dumping ", e)

            results_writer.writerow(data_list)
            # dict_to_dump = {}
            # for i in range(len(attributes_a)):
            #     dict_to_dump[attributes_a[i]] = data_list[i]
            # print(dict_to_dump)
            #
            # # record_entry = csv_dump_col.insert_one(dict_to_dump)
            # csv_dump_col.update_one({'_id': entry_id}, {'$set': dict_to_dump})
            print("comp profile record stored")
        results_file.close()
    print("CSV export completed!")

def flat_csv(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    # store data in a csv file
    dump_name = 'F:\Armitage_project\crawl_n_depth\Simplified_System\end_to_end\data_dump\\' + 'flat_csv.csv'
    with open(dump_name, mode='w', encoding='utf8',
              newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        attributes_a = ['search_text', 'title', 'link', 'description', 'comp_name',
                        'address', 'email', 'telephone_number', 'keywords', 'contact_person', 'type_or_sector',
                        'founded_year','revenue', 'funding', 'headquarters', 'No_of_employees']
        attributes_heads = ['search_text', 'title', 'link', 'description', 'comp_name',
                        'selected_address','address_from_website','address_from_google','address_from_avention','address_from_dnb','address_from_oc',

                        'selected_email','email_from_crunchbase','email_from_website',
                        'selected_tp','tp_from_website','tp_from_google','tp_from_crunchbase','tp_from_avention','tp_from_linkedin','tp_from_dnb',
                        'selected_keywords(text_processing)',
                        'selected_contact_person', 'cp_from_website','cp_from_google','cp_from_crunchbase','cp_from_avention','cp_from_dnb','cp_from_oc','cp_from_owler','cp_from_oc_agent','cp_from_li',
                        'selected_type_or_sector','sector_from_crunchbase','sector_from_avention','sector_from_linkedin','sector_from_classification_model',
                        'selected_founded_year','fy_from_crunchbase','fy_from_linkedin','fy_from_oc','fy_from_owler',
                        'selected_revenue','rev_from_avention','rev_from_owler','rev_from_dnb',
                        'selected_funding(owler)',
                        'selected_headquarters','hq_from_crunchbase','hq_from_linkedin','hq_from_owler','hq_from_oc',
                        'selected_No_of_employees','ne_from_crunchbase','ne_from_avention','ne_from_li(comp_size)','ne_from_li(emp_num)','ne_from_owler']
        results_writer.writerow(attributes_heads)
        for entry_id in id_list:
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            comp_data_entry_min = csv_dump_col.find({"_id": entry_id})
            data_min = [i for i in comp_data_entry_min]
            my_link = data[0]['link']
            # for k in data[0].keys():
            #     print(k)
            # print(data)
            data_list = []
            data_list.extend([data[0]['search_text'],data[0]['title'],data[0]['link'],data[0]['description'],data[0]['comp_name'],data_min[0]['address']])
            attribute_keys = list(data[0].keys())

            if ('google_tp_source' in attribute_keys):google_tp_source = data[0]['google_tp_source']
            else:google_tp_source = 'None'

            if ('google_cp_source' in attribute_keys):google_cp_source = data[0]['google_cp_source']
            else:google_cp_source = 'None'

            if ('google_address_source' in attribute_keys):google_address_source = data[0]['google_address_source']
            else:google_address_source = 'None'

            if ('link_dnb' in attribute_keys):link_dnb = data[0]['link_dnb']
            else:link_dnb = 'None'

            if ('link_cb' in attribute_keys):link_cb = data[0]['link_cb']
            else:link_cb = 'None'

            if ('li_url' in attribute_keys):link_li = data[0]['li_url']
            else:link_li = 'None'

            if ('site_url_oc' in attribute_keys):site_url_oc = data[0]['site_url_oc']
            else:site_url_oc = 'None'

            if ('link_owler' in attribute_keys):link_owler = data[0]['link_owler']
            else:link_owler = 'None'

            if('comp_url_aven' in attribute_keys):
                if('https://app.avention.com' not in data[0]['comp_url_aven']):
                    link_aven = 'https://app.avention.com'+data[0]['comp_url_aven']
                else:
                    link_aven =data[0]['comp_url_aven']
            else:link_aven = 'None'

            # print(attribute_keys)
            for each_a in attributes_a:
                try:
                    if(each_a == 'address'):
                        #address_fix
                        try:
                            g_add, w_ad, dnb_add, oc_add = '', [], '', ''
                            if ('google_address' in attribute_keys):
                                if (len(data[0]['google_address'])):
                                    g_add = data[0]['google_address']
                            if (len(data[0]['website_addresses_with_sources'])):
                                for each in data[0]['website_addresses_with_sources']:
                                    if (isvalid_hq(each[0])):
                                        w_ad.append(each)

                            if ('company_address_dnb' in attribute_keys):
                                if (len(data[0]['company_address_dnb'])):
                                    dnb_add = data[0]['company_address_dnb'][0]
                            if ('registered_address_adr_oc' in attribute_keys):
                                oc_add = data[0]['registered_address_adr_oc']
                            aven_add = ''
                            if ('address_aven' in attribute_keys):
                                aven_add = data[0]['address_aven']

                            if (len(w_ad) != 0):
                                # print('w')
                                data_list.append([w_ad])
                            else:data_list.append('None')

                            if (isvalid_hq(g_add)):
                                # print('g')
                                data_list.append([g_add,google_address_source])  # from google
                            else:data_list.append('None')
                            if (isvalid_hq(aven_add)):
                                # print('d')
                                data_list.append([aven_add,link_aven])
                            else:
                                data_list.append('None')
                            if (isvalid_hq(dnb_add)):
                                # print('d')
                                data_list.append([dnb_add,link_dnb])
                            else:
                                data_list.append('None')
                            if (isvalid_hq(oc_add.lower())):
                                # print('o')
                                data_list.append([oc_add,site_url_oc])
                            else:
                                data_list.append('None')
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'email'):
                        # print("***********eml")
                        #email_fix
                        try:
                            data_list.append(data_min[0]['email'])
                            if ('Contact_Email_cb' in attribute_keys):
                                data_list.append([data[0]['Contact_Email_cb'],link_cb])
                            else:
                                data_list.append('None')
                            if (len(data[0]['emails_with_sources'])):
                                data_list.append([data[0]['emails_with_sources']])  # from website
                            else:
                                data_list.append('None')

                            # else:
                            #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'telephone_number'):
                        # print("***********tp")
                        #tp_fix
                        try:
                            data_list.append(data_min[0]['telephone_number'])
                            tp_cb_valid = False
                            if ('Phone_Number_cb' in attribute_keys):
                                # print('cb',data[0]['Phone_Number_cb'])
                                if (is_valid_tp(data[0]['Phone_Number_cb'])):
                                    tp_cb_valid = True
                            tp_google_valid = False
                            if ('google_tp' in attribute_keys):
                                # print('cb',data[0]['Phone_Number_cb'])
                                if (is_valid_tp(data[0]['google_tp'])):
                                    tp_google_valid = True
                            dnb_tp = []
                            if ('company_tp_dnb' in attribute_keys):
                                dnb_tp = data[0]['company_tp_dnb']  # from dnb
                                # print(data_list,type(data_list))
                            w_tp = []
                            if (len(data[0]['telephone_numbers_with_sources'])):
                                plus_t = []
                                s_six = []
                                other_t = []
                                for each_tl in data[0]['telephone_numbers_with_sources']:
                                    each_t = each_tl[0]
                                    if (each_t[:3] in ['+61', '+64']):
                                        if (is_valid_tp(each_t)):
                                            plus_t.append(each_tl)
                                    if (each_t[:2] in ['61', '64']):
                                        if (is_valid_tp(each_t)):
                                            s_six.append(each_tl)
                                    if ((each_t[0] in ['0']) or (each_t[:4] in ['1300', '1800', '0800'])):
                                        if (is_valid_tp(each_t)):
                                            other_t.append(each_tl)
                                w_tp = plus_t + s_six + other_t

                            if (len(w_tp)):
                                data_list.append([w_tp])
                            else:
                                data_list.append('None')
                            if (tp_google_valid):
                                data_list.append([data[0]['google_tp'],google_tp_source])  # from google
                            else:
                                data_list.append('None')
                            if (tp_cb_valid):
                                data_list.append([data[0]['Phone_Number_cb'],link_cb])
                            else:
                                data_list.append('None')
                            if ('Tel:_aven' in attribute_keys):
                                # print(data[0]['Tel:_aven'])
                                data_list.append([data[0]['Tel:_aven'],link_aven])
                            else:
                                data_list.append('None')
                            if ('phone_li' in attribute_keys):
                                # print(data[0]['phone_li'].split("\n")[0])
                                data_list.append([data[0]['phone_li'].split("\n")[0],link_li])
                            else:
                                data_list.append('None')
                            if (len(dnb_tp)):
                                data_list.append([dnb_tp,link_dnb])  # from dnb
                            else:
                                data_list.append("None")

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'keywords'):
                        # print("***********kw")
                        if (len(data[0]['textrank_results'])):data_list.append(data[0]['textrank_results'][:10])  # from website
                        else:data_list.append("None")

                    if (each_a == 'contact_person'):
                        # print("***********cp")
                        #contact_person_fix
                        #fix thissssssssssssssssssss********************************************************************************
                        try:
                            data_list.append(data_min[0]['contact_person'])
                            wb_list = []
                            if ('important_person_company' in attribute_keys):
                                det_wb = data[0]['important_person_company']

                                # print(det_wb)
                                if (det_wb != 'No important persons found'):
                                    # wb_list = [det_wb[0]['name'], det_wb[0]['job_title']]
                                    wb_list = det_wb[0]

                            li_list = []
                            if (len(data[0]['linkedin_cp_info'])):
                                for each in data[0]['linkedin_cp_info']:
                                    data_li = (each[0].split('|')[0]).split('-')
                                    if (len(data_li) > 2):
                                        # print('li cp',[data_li[0],data_li[1].strip()+'_'+data_li[2].strip()])
                                        li_list.append([data_li[0], data_li[1].strip() + '_' + data_li[2].strip()])

                            if (len(wb_list)):
                                # print('g')
                                data_list.append([wb_list,'from_website'])  # from google
                            else: data_list.append('None')
                            if ('google_cp' in attribute_keys):
                                # print('g')
                                det_gcp = data[0]['google_cp']
                                # print('gog',det_gcp)
                                data_list.append([det_gcp,google_cp_source])  # from google
                            else:
                                data_list.append('None')
                            # crunchbase
                            if ('Founders_cb' in attribute_keys):
                                det_cb = data[0]['Founders_cb']
                                det_cb = [cb.strip() for cb in det_cb.split(',')][0]
                                data_list.append([det_cb, 'founder(s)',link_cb])
                            else:
                                data_list.append('None')
                            if ('contacts_aven' in attribute_keys):
                                det_aven = data[0]['contacts_aven'][0]
                                data_list.append([det_aven,link_aven])
                            else:
                                data_list.append('None')
                            if ('company_contacts_dnb' in attribute_keys):
                                # print('dnb',data[0]['dnb_cp_info'])
                                # print('dnb',dnb_list[0])
                                det_dnb = data[0]['company_contacts_dnb']
                                data_list.append([det_dnb[0],link_dnb])  # from dnb
                            else:
                                data_list.append('None')
                            if ('directors_or_officers_oc' in attribute_keys):
                                # print('oc')

                                # print('oc',data[0]['oc_cp_info'])
                                oc_cps = []
                                # print(data[0]['directors_or_officers_oc'])
                                for each_oc in [data[0]['directors_or_officers_oc']]:
                                    # print(each_oc)
                                    oc_det = each_oc.split(',')
                                    # print(oc_det)
                                    if (len(oc_det) > 1):
                                        oc_name = oc_det[0]
                                        # print(oc_name)
                                        if (len(oc_name) > 1):
                                            oc_post = oc_det[1]
                                            oc_cps.append([oc_name, oc_post])
                                    else:
                                        oc_cps.append([oc_det, 'agent_' + each_oc[1]])

                                # print('oc',oc_cps[0])
                                data_list.append([oc_cps[0],site_url_oc])  # from oc
                            else:
                                data_list.append('None')
                            if ('CEO_g' in attribute_keys):
                                # print('gc')
                                # print('gogq',[data[0]['CEO_g'],'CEO'])
                                data_list.append([data[0]['CEO_g'], 'CEO',link_owler])  # from google qa
                            else:
                                data_list.append('None')
                            if ('agent_name_oc' in attribute_keys):
                                # print('oca')
                                # print('oc_ag',[data[0]['agent_name_oc'],'agent'])
                                data_list.append([data[0]['agent_name_oc'][0], 'agent',site_url_oc])  # from oc_agent
                            else:
                                data_list.append('None')
                            if (len(li_list)):

                                data_list.append([li_list,'from linkedin search google'])  # from linkedin
                                # print('*****')
                            else:
                                # print('None')
                                data_list.append("None")

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'type_or_sector'):
                        #sector_fix
                        # print("***********ty")
                        try:
                            data_list.append(data_min[0]['type_or_sector'])
                            if ('Industries_cb' in attribute_keys):
                                # print('cb', data[0]['Industries_cb'].split(', ')[:2])
                                data_list.append([data[0]['Industries_cb'].split(', ')[:2],link_cb])
                            else: data_list.append('None')
                            if ('Industry:_aven' in attribute_keys):
                                # print('aven', data[0]['Industry:_aven'])
                                data_list.append([data[0]['Industry:_aven'],link_aven])
                            else:
                                data_list.append('None')
                            if ('industry_li' in attribute_keys):
                                # print('li', data[0]['industry_li'])
                                data_list.append([data[0]['industry_li'],link_li])  # from linkedin
                            else:
                                data_list.append('None')
                            if ('comp_type_pred' in attribute_keys):
                                # print('clas', data[0]['comp_type_pred'][0])
                                data_list.append([data[0]['comp_type_pred'][0][0] + ', ' + data[0]['comp_type_pred'][1][
                                    0],'from_classification_model'])  # from classification
                            else:
                                data_list.append("None")

                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'founded_year'):
                        #fy_fix
                        # print("***********fy")
                        try:
                            data_list.append(data_min[0]['founded_year'])
                            if ('Founded_Date_cb' in attribute_keys):
                                # print('cb',data[0]['Founded Date_cb'])
                                data_list.append([data[0]['Founded_Date_cb'],link_cb])  # from linkedin
                            else:
                                data_list.append('None')
                            if ('founded_li' in attribute_keys):
                                # print('li',data[0]['founded_li'])
                                data_list.append([data[0]['founded_li'],link_li])  # from linkedin
                            else:
                                data_list.append('None')
                            if ('incorporation_date_oc' in attribute_keys):
                                # print('oc', data[0]['incorporation_date_oc'].split(' (')[0])
                                data_list.append([data[0]['incorporation_date_oc'].split(' (')[0],site_url_oc])  # from oc
                            else:
                                data_list.append('None')
                            if ('founded_year_g' in attribute_keys):
                                # print('g', data[0]['founded_year_g'])
                                data_list.append([data[0]['founded_year_g'],link_owler])  # from google
                            else:
                                data_list.append("None")


                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'revenue'):
                        #rev_fix
                        # print("***********rv")
                        try:
                            data_list.append(data_min[0]['revenue'])
                            rev_d = []
                            if ('company_revenue_dnb' in attribute_keys):
                                if (len(data[0]['company_revenue_dnb'])):
                                    rev_d = data[0]['company_revenue_dnb']
                            if ('Annual_Sales:_aven' in attribute_keys):
                                # print('g')
                                data_list.append([data[0]['Annual_Sales:_aven'],link_aven])  # from google
                            else:
                                data_list.append('None')
                            if ('revenue_g' in attribute_keys):
                                # print('g')
                                data_list.append([data[0]['revenue_g'],link_owler])  # from google
                            else:
                                data_list.append('None')
                            if (len(rev_d)):
                                # print('d')
                                a_rev = rev_d[0].split('|')[1]
                                print(a_rev)
                                data_list.append([a_rev,link_dnb])  # from dnb
                            else:
                                data_list.append("None")
                            # if ('Contact Email_cb' in attribute_keys):
                            #     data_list = data[0]['Contact Email_cb']
                            # elif (len(data[0]['emails'])):
                            #     data_list.append(data[0]['emails'][0])  # from website
                            # else:
                            #     data_list.append("None")
                            # # else:
                            # #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'funding'):
                        # print("***********f")
                        if ('funding_g' in attribute_keys):data_list.append([data[0]['funding_g'],link_owler])  # from google
                        else:data_list.append("None")

                    if (each_a == 'headquarters'):
                        #hq_fix
                        # print("***********hq")
                        try:
                            data_list.append(data_min[0]['headquarters'])
                            hq_cb, hq_g, hq_li, j_oc = '', '', '', ''
                            if ('comp_headquaters_cb' in attribute_keys):
                                hq_cb = data[0]['comp_headquaters_cb']

                            if ('headquarters_li' in attribute_keys):
                                hq_li = data[0]['headquarters_li']

                            if ('jurisdiction_oc' in attribute_keys):
                                j_oc = data[0]['jurisdiction_oc']

                            if ('headquarters_g' in attribute_keys):
                                hq_g = data[0]['headquarters_g']

                            if (isvalid_hq(hq_cb)):
                                data_list.append([hq_cb,link_cb])
                            else:data_list.append('None')
                            if (isvalid_hq(hq_li)):
                                data_list.append([hq_li,link_li])
                            else:
                                data_list.append('None')
                            if (isvalid_hq(hq_g)):
                                data_list.append([hq_g,link_owler])
                            else:
                                data_list.append('None')
                            if (isvalid_hq(j_oc)):
                                data_list.append([j_oc,site_url_oc])
                            else:
                                data_list.append("None")
                            # else:
                            #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                    if (each_a == 'No_of_employees'):
                        #fix_ne
                        # print("***********ne")
                        try:
                            data_list.append(data_min[0]['No_of_employees'])
                            data_lil = None
                            if ('company_size_li' in attribute_keys):
                                if (data[0]['company_size_li'] != None):
                                    if (' employees' in data[0]['company_size_li']):
                                        data_lil = data[0]['company_size_li'].replace(' employees', '')



                            if ('Number_of_Employees_cb' in attribute_keys):
                                # print('cb')
                                data_list.append([data[0]['Number_of_Employees_cb'],link_cb])  # from company_size_li
                            else:
                                data_list.append('None')
                            if ('Employees_(All_Sites):_aven' in attribute_keys):
                                data_list.append([data[0]['Employees_(All_Sites):_aven'],link_aven])
                            else:
                                data_list.append('None')
                            if (data_lil != None):
                                data_list.append([data_lil,link_li])  # from company_size_li
                            else:
                                data_list.append('None')
                            if ('num_employees_li' in attribute_keys):
                                # print('li')
                                data_list.append([str(data[0]['num_employees_li']).split("\n")[0],link_li])  # from linkedin
                            else:
                                data_list.append('None')
                            if ('no_of_employees_g' in attribute_keys):
                                # print('g')
                                data_list.append([data[0]['no_of_employees_g'],link_owler])  # from googlecompany_size_li
                            else:
                                data_list.append("None")
                            # else:
                            #     data_list.append("None")
                        except KeyError:
                            data_list.append('None')

                except KeyError:
                    data_list.append('None')
                except Exception as e:
                    data_list.append('None')
                    print("Exception Occured during dumping ", e)
            print(data_list)
            results_writer.writerow(data_list)
            # dict_to_dump = {}
            # for i in range(len(attributes_a)):
            #     dict_to_dump[attributes_a[i]] = data_list[i]
            # print(dict_to_dump)
            #
            # # record_entry = csv_dump_col.insert_one(dict_to_dump)
            # csv_dump_col.update_one({'_id': entry_id}, {'$set': dict_to_dump})
            print("flat csv dump updated")
        results_file.close()
    print("Flat CSV export completed!")

from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
stop_words = stopwords.words('english')



def hq_fix(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        data_list = []
        attribute_keys = list(data[0].keys())
        print('***')
        try:
            hq_cb,hq_g,hq_li,j_oc = '','','',''
            if ('comp_headquaters_cb' in attribute_keys):
                hq_cb = data[0]['comp_headquaters_cb']

            if ('headquarters_li' in attribute_keys):
                hq_li = data[0]['headquarters_li']

            if ('jurisdiction_oc' in attribute_keys):
                j_oc = data[0]['jurisdiction_oc']

            if ('headquarters_g' in attribute_keys):
                hq_g = data[0]['headquarters_g']

            if (isvalid_hq(hq_cb)): data_list.append(hq_cb)
            elif(isvalid_hq(hq_li)):data_list.append(hq_li)
            elif(isvalid_hq(j_oc)):data_list.append(j_oc)
            elif (isvalid_hq(hq_g)):data_list.append(hq_g)
            else:data_list.append("None")
            # else:
            #     data_list.append("None")
        except KeyError:
            data_list.append('None')


        print(data_list,entry_id)

        csv_dump_col.update_one({'_id': entry_id}, {'$set': {'headquarters':data_list[0]}})
        # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'headquarters': 1}})
        print("hq updated")

def dump_hq_fix(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    with open('edu_hq.csv', mode='w', encoding='utf8',newline='') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(['_id','search_text','link','comp_name','headquarters','from_crunchbase','from_linkedin','from_opencorporates','from_owler'])

        for entry_id in id_list:
            data_to_write = []
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            comp_data_entry_min = csv_dump_col.find({"_id": entry_id})
            data_min = [i for i in comp_data_entry_min]
            data_to_write.extend([data_min[0]['_id'],data_min[0]['search_text'],data_min[0]['link'],data_min[0]['comp_name'],data_min[0]['headquarters']])

            attribute_keys = list(data[0].keys())
            if ('google_tp_source' in attribute_keys):google_tp_source = data[0]['google_tp_source']
            else:google_tp_source = 'None'

            if ('link_dnb' in attribute_keys):link_dnb = data[0]['link_dnb']
            else:link_dnb = 'None'

            if ('link_cb' in attribute_keys):link_cb = data[0]['link_cb']
            else:link_cb = 'None'

            if ('li_url' in attribute_keys):link_li = data[0]['li_url']
            else:link_li = 'None'

            if ('site_url_oc' in attribute_keys):site_url_oc = data[0]['site_url_oc']
            else:site_url_oc = 'None'

            if ('link_owler' in attribute_keys):link_owler = data[0]['link_owler']
            else:link_owler = 'None'

            print('***')
            try:
                hq_cb, hq_g, hq_li, j_oc = '', '', '', ''
                if ('comp_headquaters_cb' in attribute_keys):
                    hq_cb = data[0]['comp_headquaters_cb']

                if ('headquarters_li' in attribute_keys):
                    hq_li = data[0]['headquarters_li']

                if ('jurisdiction_oc' in attribute_keys):
                    j_oc = data[0]['jurisdiction_oc']

                if ('headquarters_g' in attribute_keys):
                    hq_g = data[0]['headquarters_g']

                if (isvalid_hq(hq_cb)):
                    data_to_write.append([hq_cb,link_cb])
                else:data_to_write.append('None')

                if (isvalid_hq(hq_li)):
                    data_to_write.append([hq_li, link_li])
                else:
                    data_to_write.append('None')

                if (isvalid_hq(j_oc)):
                    data_to_write.append([j_oc, site_url_oc])
                else:
                    data_to_write.append('None')

                if (isvalid_hq(hq_g)):
                    data_to_write.append([hq_g,link_owler])
                else:
                    data_to_write.append('None')



            except KeyError:
                print('error')

            print('completed')
            results_writer.writerow(data_to_write)


    results_file.close()

def email_fix(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        data_list = []
        attribute_keys = list(data[0].keys())
        print('***')
        try:
            if ('Contact Email_cb' in attribute_keys):
                data_list = data[0]['Contact Email_cb']
            elif (len(data[0]['emails'])):
                data_list.append(data[0]['emails'][0])  # from website
            else:
                data_list.append("None")
            # else:
            #     data_list.append("None")
        except KeyError:
            data_list.append('None')


        print(data_list)

        csv_dump_col.update_one({'_id': entry_id}, {'$set': {'email':data_list}})
        # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'email': 1}})
        print("email updated")

def rev_fix(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        data_list = []
        attribute_keys = list(data[0].keys())
        print('***')
        try:
            rev_d = []
            if ('company_revenue_dnb' in attribute_keys):
                if(len(data[0]['company_revenue_dnb'])):
                    rev_d = data[0]['company_revenue_dnb']

            if ('Annual_Sales:_aven' in attribute_keys):
                # print('g')
                data_list.append(data[0]['Annual_Sales:_aven'])  # from google
            elif ('revenue_g' in attribute_keys):
                # print('g')
                data_list.append(data[0]['revenue_g'])  # from google
            elif (len(rev_d)):
                # print('d')
                a_rev = rev_d[0].split('|')[1]
                print(a_rev)
                data_list.append(a_rev)  # from dnb
            else:
                data_list.append("None")
            # if ('Contact Email_cb' in attribute_keys):
            #     data_list = data[0]['Contact Email_cb']
            # elif (len(data[0]['emails'])):
            #     data_list.append(data[0]['emails'][0])  # from website
            # else:
            #     data_list.append("None")
            # # else:
            # #     data_list.append("None")
        except KeyError:
            data_list.append('None')


        print(data_list)
        # dict_to_dump = {'headquarters': data_list}
        csv_dump_col.update_one({'_id': entry_id}, {'$set': {'revenue':data_list}})
        # # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'email': 1}})
        # print("email updated")
def sector_fix(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        data_list = []
        attribute_keys = list(data[0].keys())
        print('***')
        try:
            if ('Industries_cb' in attribute_keys):
                print('cb',data[0]['Industries_cb'].split(', ')[:2])
                data_list.extend(data[0]['Industries_cb'].split(', ')[:2])
            elif('Industry:_aven' in attribute_keys):
                print('aven', data[0]['Industry:_aven'])
                data_list.extend([data[0]['Industry:_aven']])
            elif ('industry_li' in attribute_keys):
                print('li',data[0]['industry_li'])
                data_list.extend([data[0]['industry_li']])  # from linkedin
            elif ('comp_type_pred' in attribute_keys):
                print('clas',data[0]['comp_type_pred'][0])
                data_list.extend([data[0]['comp_type_pred'][0][0]+', '+ data[0]['comp_type_pred'][1][0]])  # from classification
            else:
                data_list.append("None")

        except KeyError:
            data_list.append('None')
        print(data_list)

        csv_dump_col.update_one({'_id': entry_id}, {'$set': {'type_or_sector':data_list}})
        # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'type_or_sector': 1}})
        print("sec updated")

def fy_fix(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        data_list = []
        attribute_keys = list(data[0].keys())
        print('***')
        try:
            if ('Founded Date_cb' in attribute_keys):
                # print('cb',data[0]['Founded Date_cb'])
                data_list.append(data[0]['Founded Date_cb'])  # from linkedin
            elif ('founded_li' in attribute_keys):
                # print('li',data[0]['founded_li'])
                data_list.append(data[0]['founded_li'])  # from linkedin
            elif ('incorporation_date_oc' in attribute_keys):
                # print('oc', data[0]['incorporation_date_oc'].split(' (')[0])
                data_list.append(data[0]['incorporation_date_oc'].split(' (')[0])  # from oc
            elif ('founded_year_g' in attribute_keys):
                # print('g', data[0]['founded_year_g'])
                data_list.append(data[0]['founded_year_g'])  # from google
            else:
                data_list.append("None")
            # if ('Industries_cb' in attribute_keys):
            #     print('cb',data[0]['Industries_cb'].split(', ')[:2])
            #     data_list.extend(data[0]['Industries_cb'].split(', ')[:2])
            # elif ('industry_li' in attribute_keys):
            #     print('li',data[0]['industry_li'])
            #     data_list.extend([data[0]['industry_li']])  # from linkedin
            # elif ('comp_type_pred' in attribute_keys):
            #     print('clas',data[0]['comp_type_pred'][0])
            #     data_list.extend([data[0]['comp_type_pred'][0][0]+', '+ data[0]['comp_type_pred'][1][0]])  # from classification
            # else:
            #     data_list.append("None")

        except KeyError:
            data_list.append('None')
        print(data_list)
        #
        csv_dump_col.update_one({'_id': entry_id}, {'$set': {'founded_year':data_list}})
        # # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'type_or_sector': 1}})
        print("fy updated")

def address_fix(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        data_list = []
        attribute_keys = list(data[0].keys())
        print('***')
        try:
            g_add,w_ad,dnb_add,oc_add = '','','',''
            if ('google_address' in attribute_keys):
                if(len(data[0]['google_address'])):
                    g_add = data[0]['google_address']
            if (len(data[0]['addresses'])):
                for each in data[0]['addresses']:
                    if(isvalid_hq(each)):
                        w_ad = each
                        break
            if ('company_address_dnb' in attribute_keys):
                if(len(data[0]['company_address_dnb'])):
                    dnb_add = data[0]['company_address_dnb'][0]
            if ('registered_address_adr_oc' in attribute_keys):
                oc_add = data[0]['registered_address_adr_oc']
            aven_add = ''
            if ('address_aven' in attribute_keys):
                aven_add = data[0]['address_aven']

            if (len(w_ad) != 0):
                # print('w')
                data_list.append(w_ad)
            elif(isvalid_hq(g_add)):
                # print('g')
                data_list.append(g_add)#from google
            elif (isvalid_hq(aven_add)):
                print('aven')
                data_list.append(aven_add)
            elif(isvalid_hq(dnb_add)):
                # print('d')
                data_list.append(dnb_add)
            elif(isvalid_hq(oc_add.lower())):
                # print('o')
                data_list.append(oc_add)
            else:data_list.append('None')

        except KeyError:
            data_list.append('None')


        print(data_list)

        csv_dump_col.update_one({'_id': entry_id}, {'$set': {'address':data_list}})
        # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'address': 1}})
        print("add updated")


def dump_address_fix(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    with open('edu_addresses.csv', mode='w', encoding='utf8',newline='') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(['_id','search_text','link','comp_name','address','from_google','from_website','from_dnb','from_oc','from_avention'])

        for entry_id in id_list:
            adds_with_sources = []
            data_to_write = []
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            comp_data_entry_min = csv_dump_col.find({"_id": entry_id})
            data_min = [i for i in comp_data_entry_min]
            data_to_write.extend([data_min[0]['_id'],data_min[0]['search_text'],data_min[0]['link'],data_min[0]['comp_name'],data_min[0]['address']])

            attribute_keys = list(data[0].keys())

            if ('google_address_source' in attribute_keys):google_address_source = data[0]['google_address_source']
            else:google_address_source = 'None'

            if ('link_dnb' in attribute_keys):link_dnb = data[0]['link_dnb']
            else:link_dnb = 'None'

            # if ('link_cb' in attribute_keys):link_cb = data[0]['link_cb']
            # else:link_cb = 'None'
            if ('comp_url_aven' in attribute_keys):
                link_aven = data[0]['comp_url_aven']
            else:
                link_aven = 'None'

            if ('site_url_oc' in attribute_keys):site_url_oc = data[0]['site_url_oc']
            else:site_url_oc = 'None'

            print('***')
            try:
                g_add,w_ad,dnb_add,oc_add = '',[],'',''
                if ('google_address' in attribute_keys):
                    if(len(data[0]['google_address'])):

                        # if(type(g_add)=='ty')
                        if(len(data[0]['google_address'])==1):
                            print("kk",data[0]['google_address'])
                        else:
                            g_add = data[0]['google_address']


                if (len(data[0]['addresses'])):
                    for each in data[0]['addresses']:
                        w_ad.append(each)
                            # break
                if ('company_address_dnb' in attribute_keys):
                    if(len(data[0]['company_address_dnb'])):
                        dnb_add = data[0]['company_address_dnb'][0]
                if ('registered_address_adr_oc' in attribute_keys):
                    oc_add = data[0]['registered_address_adr_oc']
                    print('oc_ad',oc_add)
                aven_add = ''
                if ('address_aven' in attribute_keys):
                    aven_add = data[0]['address_aven']

                if(isvalid_hq(g_add)):
                    # print('g')
                    data_to_write.append([g_add,google_address_source])#from google
                    adds_with_sources.append([g_add,'google'])
                else:
                    data_to_write.append('None')
                if(len(w_ad)!=0):
                    print(w_ad)
                    data_to_write.append(w_ad)
                else:
                    data_to_write.append('None')
                if(isvalid_hq(dnb_add)):
                    # print('d')
                    data_to_write.append([dnb_add,link_dnb])
                else:
                    data_to_write.append('None')
                if(isvalid_hq(oc_add.lower())):
                    # print('o')
                    data_to_write.append([oc_add,site_url_oc])
                else:
                    data_to_write.append('None')
                if (isvalid_hq(aven_add)):
                    # print('o')
                    data_to_write.append([aven_add, link_aven])
                else:
                    data_to_write.append('None')

            except KeyError:
                print('error')

            # data_to_write.extend(
            #     [data_min[0]['google_address_source'], data_min[0]['link_dnb'], data_min[0]['link_cb'], data_min[0]['site_url_oc']])

            print('completed')
            results_writer.writerow(data_to_write)


    results_file.close()
        # print(data_list)
        #
        # csv_dump_col.update_one({'_id': entry_id}, {'$set': {'address':data_list}})
        # # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'address': 1}})



def tp_fix(id_list):

    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        data_list = []
        attribute_keys = list(data[0].keys())
        print('***')
        try:
            tp_cb_valid = False
            tp_google_valid = False
            if ('Phone_Number_cb' in attribute_keys):
                # print('cb',data[0]['Phone_Number_cb'])
                if(is_valid_tp(data[0]['Phone_Number_cb'])):
                        tp_cb_valid = True
            if ('google_tp' in attribute_keys):
                # print('cb',data[0]['Phone_Number_cb'])
                if(is_valid_tp(data[0]['google_tp'])):
                        tp_google_valid = True
            dnb_tp = []
            if ('company_tp_dnb' in attribute_keys):
                dnb_tp = data[0]['company_tp_dnb']  # from dnb
            w_tp = []
            if (len(data[0]['telephone_numbers'])):
                plus_t = []
                s_six = []
                other_t = []
                for each_t in data[0]['telephone_numbers']:
                    if(each_t[:3] in ['+61','+64']):
                        if(is_valid_tp(each_t)):
                            plus_t.append(each_t)
                    if (each_t[:2] in ['61', '64']):
                        if(is_valid_tp(each_t)):
                            s_six.append(each_t)
                    if ((each_t[0] in ['0']) or (each_t[:4] in ['1300', '1800', '0800'])):
                        if (is_valid_tp(each_t)):
                            other_t.append(each_t)
                w_tp = plus_t+s_six+other_t
            if(len(w_tp)):
                data_list.append(w_tp[0])
            elif (tp_google_valid):
                # print('gg',data[0]['google_tp'][0])
                data_list.append(data[0]['google_tp'])  # from google
            elif(tp_cb_valid):data_list.append(data[0]['Phone_Number_cb'])
            elif('Tel:_aven' in attribute_keys):
                print(data[0]['Tel:_aven'])
                data_list.append(data[0]['Tel:_aven'])
            elif ('phone_li' in attribute_keys):
                print(data[0]['phone_li'].split("\n")[0])
                data_list.append(data[0]['phone_li'].split("\n")[0])
            elif (len(dnb_tp)):
                data_list.append(dnb_tp)  # from dnb
            else:
                data_list.append("None")

            # else:
            #     data_list.append("None")
        except KeyError:
            data_list.append('None')

        tp_num = restructure_tp(data_list[0])
        print(data_list, tp_num)
        data_list = [tp_num]
                    # print(au_p,data_list[0])


        csv_dump_col.update_one({'_id': entry_id}, {'$set': {'telephone_number':data_list}})
        # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'telephone_number': 1}})
        print("tp updated")

def get_address_vector(address):
    lowered = address.lower()
    c_rv = lowered.replace(",", " ")
    vector = (c_rv.split())
    return vector

def get_confidence_all(adds):
    adds_with_conf = []
    av_sources = []
    for k in adds:
        if(k[1] not in av_sources):av_sources.append(k[1])
    for i in range(len(adds)):
        commons = []
        each_ad_a = adds[i][0]
        for j in range(len(adds)):
            each_ad_b = adds[j][0]
            if(adds[i][1]==adds[j][1]):continue

            intersection = set(get_address_vector(each_ad_a)).intersection(get_address_vector(each_ad_b))
            # union = set(get_address_vector(each_ad_a)).union(set(get_address_vector(each_ad_b)))
            if(len(intersection)>3):
                if(adds[j][1] not in commons):
                    commons.append(adds[j][1])
        if((len(av_sources)-1)==0):
            print(each_ad_a,"cannot measure")
        else:
            print(each_ad_a,"score "+str((len(commons))/(len(av_sources)-1)))
            adds_with_conf.append([each_ad_a, ((len(commons))/(len(av_sources)-1))])
    print(adds_with_conf)
    print(adds_with_conf.sort(key = lambda x: x[1]))
    return adds_with_conf

def get_confidence(input_address,address_list):

    av_sources = []
    for k in address_list:
        if(k[1] not in av_sources):av_sources.append(k[1])
    commons = []
    for i in range(len(address_list)):
        each_ad_b = address_list[i][0]
        if(input_address[1]==address_list[i][1]):continue

        intersection = set(get_address_vector(input_address[0])).intersection(get_address_vector(each_ad_b))
        # union = set(get_address_vector(each_ad_a)).union(set(get_address_vector(each_ad_b)))
        if(len(intersection)>3):
            if(address_list[i][1] not in commons):
                commons.append(address_list[i][1])
    if((len(av_sources)-1)==0):
        print(input_address[0],"cannot measure")
        confidence_val = 0.0
    else:
        print(input_address[0],"score "+str((len(commons))/(len(av_sources)-1)))
        confidence_val = ((len(commons))/(len(av_sources)-1))
    return confidence_val

def address_conf(entry_id):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    comp_data_entry = mycol.find({"_id": entry_id})
    data = [i for i in comp_data_entry]
    comp_data_entry_min = csv_dump_col.find({"_id": entry_id})
    data_min = [i for i in comp_data_entry_min]
    selected_address = data_min[0]['address']
    adds_with_sources = []
    attribute_keys = list(data[0].keys())
    print('***')
    try:
        g_add, w_ad, dnb_add, oc_add = '', [], '', ''
        if ('google_address' in attribute_keys):
            if (len(data[0]['google_address'])):

                # if(type(g_add)=='ty')
                if (len(data[0]['google_address']) == 1):
                    print("kk", data[0]['google_address'])
                else:
                    g_add = data[0]['google_address']

        if (len(data[0]['addresses'])):
            for each in data[0]['addresses']:
                w_ad.append(each)
                # break
        if ('company_address_dnb' in attribute_keys):
            if (len(data[0]['company_address_dnb'])):
                dnb_add = data[0]['company_address_dnb'][0]
        if ('registered_address_adr_oc' in attribute_keys):
            oc_add = data[0]['registered_address_adr_oc']
            print('oc_ad', oc_add)
        aven_add = ''
        if ('address_aven' in attribute_keys):
            aven_add = data[0]['address_aven']

        if (isvalid_hq(g_add)):
            # print('g')
            adds_with_sources.append([g_add, 'google'])

        if (len(w_ad) != 0):
            print(w_ad)
            for each_adr in w_ad:
                adds_with_sources.append([each_adr,'website'])

        if (isvalid_hq(dnb_add)):
            # print('d')
            adds_with_sources.append([dnb_add, 'dnb'])

        if (isvalid_hq(oc_add.lower())):
            # print('o')
            adds_with_sources.append([oc_add.lower(), 'oc'])

        if (isvalid_hq(aven_add)):
            # print('o')
            adds_with_sources.append([aven_add, 'avention'])


    except KeyError:
        print('error')
    print('addresses_with_sources',adds_with_sources)
    selected_address_with_source = None
    for each_a_s in adds_with_sources:
        if(each_a_s[0]==selected_address):
            selected_address_with_source=each_a_s
    print('selected_address',selected_address_with_source)
    confidence_v = get_confidence(selected_address_with_source,adds_with_sources)
    print(confidence_v)


def dump_tp_fix(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    with open('edu_tp.csv', mode='w', encoding='utf8',newline='') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(['_id','search_text','link','comp_name','tp','from_website','from_google','from_cb','from_li','from_dnb','from_avention'])

        for entry_id in id_list:
            data_to_write = []
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            comp_data_entry_min = csv_dump_col.find({"_id": entry_id})
            data_min = [i for i in comp_data_entry_min]
            data_to_write.extend([data_min[0]['_id'],data_min[0]['search_text'],data_min[0]['link'],data_min[0]['comp_name'],data_min[0]['telephone_number']])

            attribute_keys = list(data[0].keys())
            if ('google_tp_source' in attribute_keys):google_tp_source = data[0]['google_tp_source']
            else:google_tp_source = 'None'

            if ('link_dnb' in attribute_keys):link_dnb = data[0]['link_dnb']
            else:link_dnb = 'None'

            if ('link_cb' in attribute_keys):link_cb = data[0]['link_cb']
            else:link_cb = 'None'

            if ('comp_url_aven' in attribute_keys):
                link_aven = "https://app.avention.com" + data[0]['comp_url_aven']
            else:
                link_aven = 'None'

            print('***')
            try:
                tp_cb_valid = False
                if ('Phone_Number_cb' in attribute_keys):
                    # print('cb',data[0]['Phone_Number_cb'])
                    if (is_valid_tp(data[0]['Phone_Number_cb'])):
                        tp_cb_valid = True
                tp_google_valid = False
                if ('google_tp' in attribute_keys):
                    # print('cb',data[0]['Phone_Number_cb'])
                    if (is_valid_tp(data[0]['google_tp'])):
                        tp_google_valid = True
                dnb_tp = []
                if ('company_tp_dnb' in attribute_keys):
                    dnb_tp = data[0]['company_tp_dnb']  # from dnb

                w_tp = []
                if (len(data[0]['telephone_numbers'])):
                    plus_t = []
                    s_six = []
                    other_t = []
                    for each_t in data[0]['telephone_numbers']:
                        if (each_t[:3] in ['+61', '+64']):
                            if (is_valid_tp(each_t)):
                                plus_t.append(each_t)
                        if (each_t[:2] in ['61', '64']):
                            if (is_valid_tp(each_t)):
                                s_six.append(each_t)
                        if ((each_t[0] in ['0']) or (each_t[:4] in ['1300', '1800', '0800'])):
                            if (is_valid_tp(each_t)):
                                other_t.append(each_t)
                    w_tp = plus_t + s_six + other_t

                if (len(w_tp)):
                    data_to_write.append([w_tp[0],'from_website'])
                else:
                    data_to_write.append('None')
                if (tp_google_valid):
                    data_to_write.append([data[0]['google_tp'],google_tp_source])  # from google
                else:
                    data_to_write.append('None')
                if (tp_cb_valid):
                    data_to_write.append([data[0]['Phone_Number_cb'],link_cb])
                else:
                    data_to_write.append('None')

                if ('phone_li' in attribute_keys):
                    print(data[0]['phone_li'].split("\n")[0])
                    data_to_write.append([data[0]['phone_li'].split("\n")[0],data[0]['li_url']])
                else:
                    data_to_write.append('None')

                if (len(dnb_tp)):
                    data_to_write.append([dnb_tp,link_dnb])  # from dnb
                else:
                    data_to_write.append('None')
                if ('Tel:_aven' in attribute_keys):
                    print(data[0]['Tel:_aven'])
                    data_to_write.append([data[0]['Tel:_aven'],link_aven])
                else:
                    data_to_write.append('None')


            except KeyError:
                print('error')

            print('completed')
            results_writer.writerow(data_to_write)


    results_file.close()



def check_cp(id_list):
    id_list_s = []
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    c=0
    for entry_id in id_list:
        print(c,entry_id)
        c=c+1
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        # print(data)
        data_list = {}
        # if(('.ca/' in data[0]['link']) or ('.ke/' in data[0]['link'])):
        #     print(data[0]['link'])
        #     id_list_s.append(ObjectId(entry_id))
        attribute_keys = list(data[0].keys())
        data_list['search_text'] = data[0]['search_text']
        data_list['title'] = data[0]['title']
        data_list['link'] = data[0]['link']
        data_list['description'] = data[0]['description']
        data_list['comp_name'] = data[0]['comp_name']
        csv_dump_col.update_one({'_id': entry_id}, {'$set': data_list})


        # for k in attribute_keys:
        #     if('_cb' in k):
        #         mycol.update_one({'_id': entry_id}, {'$unset': {k: 1}})

        # if ('comp_name_cb' in attribute_keys):
        #     comp_name = data[0]['comp_name']
        #     comp_name_cb = data[0]['comp_name_cb']
        #     print(comp_name, comp_name_cb)
        # if ('comp_name_cb' in attribute_keys):
        #     # print('g')
        #     # comp_name = data[0]['comp_name']
        #     comp_name_cb = data[0]['comp_name_cb']
        #     # det_gcp = data[0]['google_tp']
        #     # print(det_gcp)
        #     # print([det_gcp],isvalid_hq(det_gcp))
        #     print(comp_name_cb)
    print(id_list_s)

def  contact_person_fix(id_list):
    ids_list=[]
    # print(id_list)
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        data_list = []
        attribute_keys = list(data[0].keys())
        try:
            wb_list = []
            if ('important_person_company' in attribute_keys):
                det_wb = data[0]['important_person_company']

                # print(det_wb)
                if(det_wb!='No important persons found'):

                    # wb_list = [det_wb[0]['name'], det_wb[0]['job_title']]
                    wb_list = det_wb[0]

            li_list = []
            if (len(data[0]['linkedin_cp_info'])):
                for each in data[0]['linkedin_cp_info']:
                    data_li = (each[0].split('|')[0]).split('-')
                    if (len(data_li) > 2):
                        # print('li cp',[data_li[0],data_li[1].strip()+'_'+data_li[2].strip()])
                        li_list.append([data_li[0], data_li[1].strip() + '_' + data_li[2].strip()])

            if (len(wb_list)):
                # print('g')
                data_list.extend(wb_list)  # from google

            elif ('google_cp' in attribute_keys):
                # print('g')
                det_gcp = data[0]['google_cp']
                print('gog',det_gcp)
                data_list.extend(det_gcp)  # from google
            #crunchbase
            elif ('Founders_cb' in attribute_keys):
                det_cb = data[0]['Founders_cb']
                det_cb = [cb.strip() for cb in det_cb.split(',')][0]
                data_list.extend([det_cb, 'founder(s)'])

            elif ('contacts_aven' in attribute_keys):

                det_aven = data[0]['contacts_aven'][0]
                print('aven', det_aven)
                data_list.extend(det_aven)

            elif ('company_contacts_dnb' in attribute_keys):
                # print('dnb',data[0]['dnb_cp_info'])
                # print('dnb',dnb_list[0])
                det_dnb = data[0]['company_contacts_dnb']
                data_list.extend(det_dnb[0])  # from dnb

            elif ('directors_or_officers_oc' in attribute_keys):
                # print('oc')

                    # print('oc',data[0]['oc_cp_info'])
                oc_cps = []
                # print(data[0]['directors_or_officers_oc'])
                for each_oc in [data[0]['directors_or_officers_oc']]:
                    # print(each_oc)
                    oc_det = each_oc.split(',')
                    # print(oc_det)
                    if(len(oc_det)>1):
                        oc_name = oc_det[0]
                        # print(oc_name)
                        if(len(oc_name)>1):
                            oc_post = oc_det[1]
                            oc_cps.append([oc_name,oc_post])
                    else:
                        oc_cps.append([oc_det, 'agent_'+each_oc[1]])

                # print('oc',oc_cps[0])
                data_list.extend(oc_cps[0])  # from oc
            elif ('CEO_g' in attribute_keys):
                # print('gc')
                # print('gogq',[data[0]['CEO_g'],'CEO'])
                data_list.extend([data[0]['CEO_g'],'CEO'])  # from google qa
            elif ('agent_name_oc' in attribute_keys):
                # print('oca')
                # print('oc_ag',[data[0]['agent_name_oc'],'agent'])
                data_list.extend([data[0]['agent_name_oc'][0],'agent'])  # from oc_agent
            elif (len(li_list)):

                data_list.extend(li_list[0])  # from linkedin
                # print('*****')
            else:
                # print('None')
                data_list.append("None")

        except KeyError:
            data_list.append('None')

        print('dl',data_list)
        # if(data_list[0]=='None'):
        #
        #     ids_list.append(ObjectId(entry_id))

        dict_to_dump={'contact_person':data_list}
        # # # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'contact_person':1}})
        csv_dump_col.update_one({'_id': entry_id}, {'$set': dict_to_dump})
        print("cont updated")
    # print(ids_list)

def  dump_contact_person_fix(id_list):
    ids_list=[]
    # print(id_list)
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    with open('edu_contacts.csv', mode='w', encoding='utf8',newline='') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(['_id','search_text','link','comp_name','contact_person','from_website','from_google','from_crunchbase','from_dnb','from_oc','from_owler','from_oc_agent','from_li','from_avention'])

        for entry_id in id_list:
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            comp_data_entry_min = csv_dump_col.find({"_id": entry_id})
            data_min = [i for i in comp_data_entry_min]
            data_list = []
            attribute_keys = list(data[0].keys())
            data_to_write = []
            data_to_write.extend(
                [data_min[0]['_id'], data_min[0]['search_text'], data_min[0]['link'], data_min[0]['comp_name'],
                 data_min[0]['contact_person']])
            if ('google_cp_source' in attribute_keys):google_cp_source = data[0]['google_cp_source']
            else:google_cp_source = 'None'

            if ('link_dnb' in attribute_keys):link_dnb = data[0]['link_dnb']
            else:link_dnb = 'None'

            if ('link_cb' in attribute_keys):link_cb = data[0]['link_cb']
            else:link_cb = 'None'

            if ('site_url_oc' in attribute_keys):site_url_oc = data[0]['site_url_oc']
            else:site_url_oc = 'None'

            if ('link_owler' in attribute_keys):link_owler = data[0]['link_owler']
            else:link_owler = 'None'

            try:
                # dnb_list=[]
                # if (len(data[0]['dnb_cp_info']) == 3):
                #     dnb_list = data[0]['dnb_cp_info'][2]
                # oc_list = []
                # if (len(data[0]['oc_cp_info']) == 3):
                #     oc_list = data[0]['oc_cp_info'][2]
                wb_list = []
                if ('important_person_company' in attribute_keys):
                    det_wb = data[0]['important_person_company']

                    # print(det_wb)
                    if (det_wb != 'No important persons found'):
                        # wb_list = [det_wb[0]['name'], det_wb[0]['job_title']]
                        wb_list = det_wb[0]

                li_list = []
                if (len(data[0]['linkedin_cp_info'])):
                    for each in data[0]['linkedin_cp_info']:
                        data_li = (each[0].split('|')[0]).split('-')
                        if (len(data_li) > 2):
                            # print('li cp',[data_li[0],data_li[1].strip()+'_'+data_li[2].strip()])
                            li_list.append([data_li[0], data_li[1].strip() + '_' + data_li[2].strip()])

                if (len(wb_list)):
                    # print('g')
                    data_to_write.append(wb_list)  # from wb
                else:data_to_write.append("None")

                if ('google_cp' in attribute_keys):
                    # print('g')
                    det_gcp = data[0]['google_cp']
                    # print('gog',det_gcp)
                    data_to_write.append([det_gcp,google_cp_source])  # from google

                else:data_to_write.append("None")

                #crunchbase
                if ('Founders_cb' in attribute_keys):
                    det_cb = data[0]['Founders_cb']
                    det_cb = [cb.strip() for cb in det_cb.split(',')][0]
                    data_to_write.append([det_cb, 'founder(s)',link_cb])
                else:
                    data_to_write.append("None")

                if ('company_contacts_dnb' in attribute_keys):
                    # print('dnb',data[0]['dnb_cp_info'])
                    # print('dnb',dnb_list[0])
                    det_dnb = data[0]['company_contacts_dnb']
                    data_to_write.append([det_dnb[0],link_dnb])  # from dnb
                else:
                    data_to_write.append("None")
                if ('directors_or_officers_oc' in attribute_keys):
                    # print('oc')
                        # print('oc',data[0]['oc_cp_info'])
                    oc_cps = []
                    for each_oc in [data[0]['directors_or_officers_oc']]:
                        print('each_det',each_oc)
                        oc_det = each_oc.split(',')
                        print(oc_det)
                        if (len(oc_det) > 1):
                            oc_name = oc_det[0]
                            # print(oc_name)
                            if (len(oc_name) > 1):
                                oc_post = oc_det[1]
                                oc_cps.append([oc_name, oc_post])
                        else:
                            oc_cps.append([oc_det, 'agent_' + each_oc[1]])

                    print('oc',oc_cps)
                    data_to_write.append([oc_cps,site_url_oc])  # from oc
                else:
                    data_to_write.append("None")

                if ('CEO_g' in attribute_keys):
                    # print('gc')
                    # print('gogq',[data[0]['CEO_g'],'CEO'])
                    data_to_write.append([data[0]['CEO_g'],'CEO',link_owler])  # from google qa
                else:
                    data_to_write.append("None")



                if ('agent_name_oc' in attribute_keys):
                    # print('oca')
                    # print('oc_ag',[data[0]['agent_name_oc'],'agent'])
                    data_to_write.append([data[0]['agent_name_oc'][0],'agent',site_url_oc])  # from oc_agent
                else:
                    data_to_write.append("None")

                if (len(li_list)):

                    data_to_write.append(li_list)  # from linkedin
                else:
                    data_to_write.append("None")
                    # print('*****')
                if ('contacts_aven' in attribute_keys):
                    det_aven = data[0]['contacts_aven'][0]
                    data_to_write.append(det_aven)  # from linkedin
                else:
                    data_to_write.append("None")


            except KeyError:
                print('error')

            print('completed')
            # if('link_cb' in attribute_keys):
            #     data_to_write.append(data[0]['link_cb'])

            results_writer.writerow(data_to_write)
    results_file.close()



        # dict_to_dump={'contact_person':data_list}
        # # # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'contact_person':1}})
        # csv_dump_col.update_one({'_id': entry_id}, {'$set': dict_to_dump})
        # print("cont updated")
    print(ids_list)

def clear_dnb(id_list):
    mycol = refer_collection()
    ids_list=[]
    for entry_id in id_list:

        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        attris = list(data[0].keys())
    #     if('google_address' in attris):
    #         if(len(data[0]['google_address'])==1):
    #             print(data[0]['google_address'])
    #             ids_list.append(entry_id)
    #             mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'google_address': 1}})
    #             print('cleard_cp',entry_id)
    # print(ids_list)
        # if ('google_cp_source' in attris):
        #     mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'google_cp_source': 1}})
        #     print('cleard_cp_source', entry_id)

        for each_at in attris:
        #     if('_g' in each_at):
        #         mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {each_at: 1}})
        #         print(each_at)

            if ('_g' in each_at[-2:]):
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {each_at: 1}})
                print(each_at)
            if ('_li' in each_at[-3:]):
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {each_at: 1}})
                print(each_at)
            if ('_cb' in each_at[-3:]):
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {each_at: 1}})
                print(each_at)
def check_empty_addresses(id_list):
    mycol = refer_collection()
    ids_list=[]
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        attris = list(data[0].keys())
        if ('addresses' in attris):
            adds = data[0]['addresses']
            if(len(adds)==0):
                print(entry_id, len(adds),adds)
                ids_list.append(entry_id)
    print(ids_list)

def check_tp(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    ids_list=[]
    for entry_id in id_list:
        # comp_data_entry = mycol.find({"_id": entry_id})
        # data = [i for i in comp_data_entry]
        # attris = list(data[0].keys())
        comp_data_entry_min = csv_dump_col.find({"_id": entry_id})
        data_min = [i for i in comp_data_entry_min]
        attris_min = list(data_min[0].keys())
        # if('phone_li' in attris):
        #     print(data[0]['phone_li'].split("\n")[0])
        # for each_a in attris_min:
        #     if('telephone_number' in each_a):
        #         ids_list.append(ObjectId(entry_id))
        #         print(data_min[])
                # break
        # else:print('None',entry_id)
                # print(data[0]['telephone_numbers'])

            # if ('_oc' in each_at):
            #     mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {each_at: 1}})
            #     print(each_at)
    # print(ids_list)
def check_aven(id_list):
    mycol = refer_collection()
    ids_list=[]
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        attris = list(data[0].keys())
        print('****')
        if('important_person_company' in attris):
            print(data[0]['important_person_company'])
            # mycol.update_one({'_id': entry_id}, {'$set': {'important_person_company': 'No important persons found'}})
        # for each_a in attris:
        #     if('_aven' in each_a):
        #         ids_list.append(ObjectId(entry_id))
        #         print(each_a,data[0][each_a])
        #         break
        # else:print('None',entry_id)
    print(ids_list)
def check_link(id_list):
    mycol = refer_collection()
    ids_list=[]
    b_list_file = open('F:\Armitage_project\crawl_n_depth\Simplified_System\Initial_Crawling\\black_list.txt', 'r')
    black_list = b_list_file.read().splitlines()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        attris = list(data[0].keys())
        if('link' in attris):
            # print(data[0]['link'])
            each_l = data[0]['link']
            each_l_dom = data[0]['link'].split("/")[2]
            if each_l_dom in black_list:
                print(each_l)
                ids_list.append(entry_id)
            elif (('.gov.' in each_l) or ('.govt.' in each_l) or ('.edu.' in each_l) or ('.uk' in each_l)):  # filter non wanted websites
                print(each_l)
                ids_list.append(entry_id)
            elif (('.com/' in each_l) or ('.education/' in each_l) or ('.io/' in each_l) or ('.com.au/' in each_l) or (
                    '.net/' in each_l) or ('.org/' in each_l) or ('.co.nz/' in each_l) or ('.nz/' in each_l) or (
                    '.au/' in each_l) or ('.biz/' in each_l)):
                continue
            else:
                print(each_l)
                ids_list.append(entry_id)
    print(ids_list)


        # for each_a in attris:
        #     if('_aven' in each_a):
        # #         ids_list.append(ObjectId(entry_id))
        #         print('got',entry_id)
        #         break
        # else:print('None',entry_id)
                # print(data[0]['telephone_numbers'])

            # if ('_oc' in each_at):
            #     mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {each_at: 1}})
            #     print(each_at)
    # print(ids_list)
def check_cl(id_list):
    mycol = refer_collection()
    with open('scrape_cp.csv', mode='w', encoding='utf8', newline='') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(
            ['_id', 'link', 'comp_name', 'h_s_length', 'addresses', 'telephone_numbers', 'social_media_links',
             'emails'])

        for entry_id in id_list:
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            attris = list(data[0].keys())
            data_list = [data[0]['_id'],data[0]['link'],data[0]['comp_name'],len(data[0]['header_text']),data[0]['addresses'],data[0]['telephone_numbers'],data[0]['social_media_links'][:20],data[0]['emails']]
            if('header_text' in attris):
                h_t = data[0]['header_text']
                print(entry_id,len(h_t))

            results_writer.writerow(data_list)
    results_file.close()
            # for each_cl in crawled_links:
            #     if('contact' in each_cl):
            #         print(each_cl)
# edu_set = [ObjectId('5eb62e2a134cc6fb9536e93d'), ObjectId('5eb630147afe26eca4ba7bfa'), ObjectId('5eb6311c86662885174692de'), ObjectId('5eb631f1fac479799dedd1f8'), ObjectId('5eb6331597c8f5512179c4f1'), ObjectId('5eb634492802acb8c48e02aa'), ObjectId('5eb63539be65b70e5af0c7a9'), ObjectId('5eb6363894bd0b097f9c2734'), ObjectId('5eb6378b772150870b5c8d27'), ObjectId('5eb639ee2c60aae411d1ae8b'), ObjectId('5eb63aff81de1c4846fd91ab'), ObjectId('5eb63c1e9c69232f6ed6edd8'), ObjectId('5eb63d1b9d2ec0b892c42dd5'), ObjectId('5eb63e1ee805d1cff3d80a25'), ObjectId('5eb63ee743b668cb27ef8137'), ObjectId('5eb640560732058562a400b3'), ObjectId('5eb646ce3b4442b4da91c057'), ObjectId('5eb6479687b6932b9e6de098'), ObjectId('5eb648bf6bc924ef46ab60da'), ObjectId('5eb64a8e96bdd2bbbb3287e5'), ObjectId('5eb64bc810a22fecd4eca987'), ObjectId('5eb64cfc8c94747a21f39855'), ObjectId('5eb64e13158973dfa9982019'), ObjectId('5eb64f4ea0549166c51ca057'), ObjectId('5eb650acab06d680d6990351'), ObjectId('5eb651bc5fa088c453991725'), ObjectId('5eb652de55de509b4a9efaf4'), ObjectId('5eb65433af5bcc3efe32c504'), ObjectId('5eb6556c29c37695bc97bec4'), ObjectId('5eb6567909d0de1b6b708cf8'), ObjectId('5eb657e754ee9cbe1a7388c8'), ObjectId('5eb65942b46918d079adebe9'), ObjectId('5eb65a927cb5b3a1ff4ae362'), ObjectId('5eb65b645417d406270e7e63'), ObjectId('5eb65d83728ad01002b3a5f6'), ObjectId('5eb65f2cde8cab37cd68dffd'), ObjectId('5eb6603b6e69c6f2e1092cf8'), ObjectId('5eb661a6796445df9bfd756d'), ObjectId('5eb6631b245b7e033d0f92ed'), ObjectId('5eb66401b0e60a643fae0467'), ObjectId('5eb6651284c93e9e1b685024'), ObjectId('5eb66682dc99a524418da337'), ObjectId('5eb667a554cc6bc47dbfea44'), ObjectId('5eb6688cf9acda3a876322e4'), ObjectId('5eb669883e6dc49bd6f1540f'), ObjectId('5eb66a9b90f9dd06f1107866'), ObjectId('5eb66bb449a0728d932475bc'), ObjectId('5eb66ce4535d821544a14dee'), ObjectId('5eb66dabf3d5b58ef16a4c74'), ObjectId('5eb66e99e95b7d86f2518828'), ObjectId('5eb66fa738555190120005d2'), ObjectId('5eb670c2382a70cea3c90149'), ObjectId('5eb672382cf60f5b673dc845'), ObjectId('5eb6734f61272a1489607d7c'), ObjectId('5eb6746b3f8078c646a32068'), ObjectId('5eb675384beae11731a0ce35'), ObjectId('5eb676209d0d155a1c6530f3'), ObjectId('5eb6777b140e783b3524f4d9'), ObjectId('5eb6783b3dd775bea489b02d'), ObjectId('5eb67952c38498d75c86627f'), ObjectId('5eb67a4c109ddab70aec7b2d'), ObjectId('5eb67bc12373d9a910e8750f'), ObjectId('5eb67d3dd9818bcd44884d39'), ObjectId('5eb67e66b7921dcf1c2e6805'), ObjectId('5eb67fa821374c1c36ea76bb'), ObjectId('5eb680d98c70c48229cd26b6'), ObjectId('5eb6820dcc1fecfea5009f48'), ObjectId('5eb682ecd810c81378eb806d'), ObjectId('5eb68405b8f3f1e1b3084a52'), ObjectId('5eb6853a626f824ef428e315'), ObjectId('5eb688a782ee2ac4699515f2'), ObjectId('5eb689814e048265dd507dbc'), ObjectId('5eb68a771a268ae85ef97960'), ObjectId('5eb68b52298db2bd4cebdd0e'), ObjectId('5eb68c65501e64174bede873'), ObjectId('5eb68d458e708541f4671189'), ObjectId('5eb68e2fab2ce0451e2b4056'), ObjectId('5eb68edce0b5b75b05fba1e6'), ObjectId('5eb690038f7f6e26b6253fd5'), ObjectId('5eb690bd8d99ac316303ffb6'), ObjectId('5eb6918fa2e66438837c2d83'), ObjectId('5eb6925a31a5f94e1207b916'), ObjectId('5eb6944565d7b2466379f198'), ObjectId('5eb694f59c10ae1d407b7c2a'), ObjectId('5eb695e1ffe996bbe09292fe'), ObjectId('5eb696f6ef36438bec383b7e'), ObjectId('5eb697cac579ca076779cb0f'), ObjectId('5eb698a46de98c90f95a497d'), ObjectId('5eb699a671806057e76f0141'), ObjectId('5eb69a7d5587c492135fd56c'), ObjectId('5eb69b6fc6cad85bd913e12a'), ObjectId('5eb69c52d1ecab806f2beead'), ObjectId('5eb69cefc81bdf1aac4bf6a1'), ObjectId('5eb69e087e9ea4385e20beed'), ObjectId('5eb69f48a04ce33b509b4895'), ObjectId('5eb6a058cd265d6ef2ee766f'), ObjectId('5eb6a12f7ef80a97c531cc67'), ObjectId('5eb6a21fe632eaf0b1d593db'), ObjectId('5eb6a63fc0820e4534126e94'), ObjectId('5eb6a72dfc5d1c47d4ca9cd1'), ObjectId('5eb6a8462d272649f7b4df95'), ObjectId('5eb6a930b440ebf60d42d6c2'), ObjectId('5eb6aa15b5b4db2c7393254c'), ObjectId('5eb6ab260aef4a583d77118f'), ObjectId('5eb6ac1bfff106a6f58c42e7'), ObjectId('5eb6ad1662db4e6c180a378b'), ObjectId('5eb6ae390bdb0b194f41f9b3'), ObjectId('5eb6af2a6012ca09c1728130'), ObjectId('5eb6afc4e15b344d1a3aafa0'), ObjectId('5eb6b19b1c6e630676c62445'), ObjectId('5eb6b2a5a9211572420260e9'), ObjectId('5eb6b38eeb5e21b75a0d7cdb'), ObjectId('5eb6b45f4dab807be8d7a28a'), ObjectId('5eb6b53fd8471918b43146b7'), ObjectId('5eb6b61fabf00d5fdb2d05a3'), ObjectId('5eb6b71e5cd9b7b54c7d9961'), ObjectId('5eb6b9158f232307ce0bdc13'), ObjectId('5eb6b9dbb8b6b03010c4dcc6'), ObjectId('5eb6bad32c05d6f34cf32652'), ObjectId('5eb6bbbee2f17c3f3238cec8'), ObjectId('5eb6bca1b68e7672cd0ef210'), ObjectId('5eb6bdb1e7b6cc4614eb0edb'), ObjectId('5eb6beca47492aa1e0553de4'), ObjectId('5eb6bfc707fd60d7d77844de'), ObjectId('5ed3846f023b726e6d17d4f0'), ObjectId('5ed38b25d439f58cc06e5825'), ObjectId('5ed38d5420653aee6e3220c8'), ObjectId('5ed38efe1838c05e0c6fb6e4'), ObjectId('5ed3900863e5bffa1d2b4e2f'), ObjectId('5ed391925d33c4975503bb94'), ObjectId('5ed394144eb75866dfdcdc0d'), ObjectId('5ed39521d784bdc428779a0f'), ObjectId('5ed3966ae5903d41b23471ba'), ObjectId('5ed3980c016ddd49b0f4c304'), ObjectId('5ed3996045e3020d63762dce'), ObjectId('5ed39b1195eba19024e714bf'), ObjectId('5ed39d3781f6df0d82e6bfda'), ObjectId('5ed39f30fc1a9fd5e77e332f'), ObjectId('5ed3a07a5dbe3d7cdbc0a11f'), ObjectId('5ed3a21a7deae88594ebebcb'), ObjectId('5ed3a430b15357da758e9aaf'), ObjectId('5ed3a65cc612795088fb19b8'), ObjectId('5ed3a8655fa4a60f979e1f88'), ObjectId('5ed3ac8b4daab633d19b58d8'), ObjectId('5ed3add3461496c2716f7235'), ObjectId('5ed3af522f225fd825bf711a'), ObjectId('5ed3b088624645fcbe0374c5'), ObjectId('5ed3b2383758cc50c8bdd137'), ObjectId('5ed3b766a882d958e63eb52e')]

# check_cl(edu_set)


def fix_100(id_list):
    mycol = refer_collection()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        attris = list(data[0].keys())
        # print(attris)
        if 'founded_year_g' in attris:
            if('Australian Government' in data[0]['founded_year_g']):
                print(data[0]['founded_year_g'])
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'founded_year_g': 1}})
        if 'CEO_g' in attris:
            if ('Australian Government' in data[0]['CEO_g']):
                print(data[0]['CEO_g'])
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'CEO_g': 1}})
        if 'revenue_g' in attris:
            if ('Australian Government' in data[0]['revenue_g']):
                print(data[0]['revenue_g'])
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'revenue_g': 1}})
        if 'funding_g' in attris:
            if ('Australian Government' in data[0]['funding_g']):
                print(data[0]['funding_g'])
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'funding_g': 1}})
        if 'headquarters_g' in attris:
            if ('Australian Government' in data[0]['headquarters_g']):
                print(data[0]['headquarters_g'])
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'headquarters_g': 1}})
        if 'no_of_employees_g' in attris:
            if ('Australian Government' in data[0]['no_of_employees_g']):
                print(data[0]['no_of_employees_g'])
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'no_of_employees_g': 1}})
        if 'competitors_g' in attris:
            if ('Australian Government' in data[0]['competitors_g']):
                print(data[0]['competitors_g'])
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'competitors_g': 1}})
        if 'invested_in_g' in attris:
            if ('Australian Government' in data[0]['invested_in_g']):
                print(data[0]['invested_in_g'])
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'invested_in_g': 1}})
        if 'sector_g' in attris:
            if ('Australian Government' in data[0]['sector_g']):
                print(data[0]['sector_g'])
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$unset': {'sector_g': 1}})

def partial_export(id_list):
    mycol = refer_collection()
    # store data in a csv file
    dump_name = 'F:\Armitage_project\crawl_n_depth\Simplified_System\end_to_end\data_dump\\' + str(
        id_list[0]) + '_partial_dump_simplified.csv'
    with open(dump_name, mode='w', encoding='utf8',
              newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        attributes_a = ['_id', 'comp_name','founded_year_g','CEO_g','revenue_g','funding_g','headquarters_g','no_of_employees_g','competitors_g',
                        'invested_in_g','sector_g']
        results_writer.writerow(attributes_a)
        for entry_id in id_list:
            comp_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in comp_data_entry]
            data_list = []
            for each_a in attributes_a:
                try:
                    data_list.append(data[0][each_a])
                except KeyError:
                    data_list.append('None')
            results_writer.writerow(data_list)
            print("simplified dump completed")
        results_file.close()
    print("Partial CSV export completed!")

# partial_export(owler)
def fix_ne(id_list):
    mycol = refer_collection()
    csv_dump_col = refer_simplified_dump_col_min()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        data_list = []
        attribute_keys = list(data[0].keys())
        print('***')
        try:
            data_lil = None
            if('company_size_li' in attribute_keys):
                if(data[0]['company_size_li']!=None):
                    if (' employees' in data[0]['company_size_li']):
                        data_lil = data[0]['company_size_li'].replace(' employees', '')
            if ('Number of Employees_cb' in attribute_keys):
                # print('cb')
                data_list.append(data[0]['Number of Employees_cb'])  # from company_size_li
            elif('Employees_(All_Sites):_aven' in attribute_keys):
                print('aven',data[0]['Employees_(All_Sites):_aven'])
                data_list.append(data[0]['Employees_(All_Sites):_aven'])
            elif (data_lil!=None):
                data_list.append(data_lil)  # from company_size_li

            elif ('num_employees_li' in attribute_keys):
                # print('li')
                data_list.append(str(data[0]['num_employees_li']).split("\n")[0])  # from linkedin
            elif ('no_of_employees_g' in attribute_keys):
                # print('g')
                data_list.append(data[0]['no_of_employees_g'])  # from googlecompany_size_li
            else:
                data_list.append("None")
            # else:
            #     data_list.append("None")
        except KeyError:
            data_list.append('None')


        print(data_list)
        # dict_to_dump = {'No_of_employees': data_list}
        csv_dump_col.update_one({'_id': entry_id}, {'$set': {'No_of_employees':data_list}})
        # csv_dump_col.update_one({'_id': entry_id}, {'$unset': {'No_of_employees': 1}})
        print("ne updated")


def data_cleaning(id_list):
    mycol = refer_collection()
    for entry_id in id_list:
        comp_data_entry = mycol.find({"_id": entry_id})
        data = [i for i in comp_data_entry]
        attris = list(data[0].keys())
        # print(attris)
        if 'founded_year_g' in attris:
            # print('fyr')
            if ('was founded in' in data[0]['founded_year_g']):
                f_y = data[0]['founded_year_g'].split("was founded in ")[1]
                print(f_y)
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$set': {'founded_year_g': f_y}})
        if 'CEO_g' in attris:
            # print('ceo')
            if ('CEO is' in data[0]['CEO_g']):
                # print('cc')
                ceo_g = data[0]['CEO_g'].split("CEO is ")[1]
                print('ceo',ceo_g)
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$set': {'CEO_g': ceo_g}})
        if 'revenue_g' in attris:
            # print('rev')
            if ('generates' in data[0]['revenue_g']):
                # print(data[0]['revenue_g'])
                rev = data[0]['revenue_g'].split('generates ')[1].split(" ")[0]
                print(rev)
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$set': {'revenue_g': rev}})
        if 'funding_g' in attris:
            # print('fun')
            if ('has historically raised' in data[0]['funding_g']):
                fund = data[0]['funding_g'].split('has historically raised ')[1].split(" ")[0]
                print(fund)
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$set': {'funding_g': fund}})
        if 'headquarters_g' in attris:
            # print('hed')
            if ('headquarters is in' in data[0]['headquarters_g']):
                hq = data[0]['headquarters_g'].split("headquarters is in ")[1]
                print(hq)
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$set': {'headquarters_g': hq}})
        if 'no_of_employees_g' in attris:
            # print('emp')
            if ('has' in data[0]['no_of_employees_g']):
                emp = data[0]['no_of_employees_g'].split('has ')[1].split(" ")[0]
                print(emp)
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$set': {'no_of_employees_g': emp}})
        if 'competitors_g' in attris:
            # print('cmp')
            if ('top competitors are' in data[0]['competitors_g']):
                compt = data[0]['competitors_g'].split("top competitors are ")[1]
                print(compt)

                mycol.update_one({'_id': ObjectId(entry_id)}, {'$set': {'competitors_g': compt}})
        if 'invested_in_g' in attris:
            # print('inv')
            if ('has invested in companies such as' in data[0]['invested_in_g']):
                inv = data[0]['invested_in_g'].split('has invested in companies such as ')[1]
                print(inv)
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$set': {'invested_in_g': inv}})
        if 'sector_g' in attris:
            # print('sec')
            if ('is in' in data[0]['sector_g']):
                sec = data[0]['sector_g'].split('is in ')[1]
                print(sec)
                mycol.update_one({'_id': ObjectId(entry_id)}, {'$set': {'sector_g': sec}})
# data_cleaning(all_ids_2045)
def is_profile_exist(comp_url):
    mycol = refer_collection()
    is_yes = mycol.find({"link": comp_url}, {"_id" : 1})
    data = [d for d in is_yes]
    return data

def is_query_exist(search_text):
    mycol = refer_query_col()
    is_yes = mycol.find({"search_query": search_text}, {"_id" : 1})
    data = [d for d in is_yes]
    return data

def is_profile_exist_by_domain(comp_url):
    mycol = refer_collection()
    is_yes = mycol.find({"link": {'$regex': comp_url}}, {"_id": 1})
    data = [d for d in is_yes]
    return data
    # if(len(data)):
    #     return True
    # else:
    #     return False

# print(is_profile_exist_by_domain('forums.whirlpool.net.au'))

def exp_raw(id):
    mycol = refer_collection()
    is_yes = mycol.find({"_id": id}, )
    data = [d for d in is_yes]
    attrib = list(data[0].keys())
    vals = []
    for k in attrib:
        if(k=='paragraph_text'):vals.append('skipped')
        if(k=='header_text'):vals.append('skipped')
        else:vals.append(str(data[0][k]).replace(","," "))

    with open('export_raw_data.csv', mode='w', encoding='utf8',newline='') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        results_writer.writerow(attrib)
        results_writer.writerow(vals)
    results_file.close()




all_ids_fixed = [ObjectId('5eb62e2a134cc6fb9536e93d'), ObjectId('5eb630147afe26eca4ba7bfa'), ObjectId('5eb6311c86662885174692de'), ObjectId('5eb631f1fac479799dedd1f8'), ObjectId('5eb6331597c8f5512179c4f1'), ObjectId('5eb634492802acb8c48e02aa'), ObjectId('5eb63539be65b70e5af0c7a9'), ObjectId('5eb6363894bd0b097f9c2734'), ObjectId('5eb6378b772150870b5c8d27'), ObjectId('5eb639ee2c60aae411d1ae8b'), ObjectId('5eb63aff81de1c4846fd91ab'), ObjectId('5eb63c1e9c69232f6ed6edd8'), ObjectId('5eb63d1b9d2ec0b892c42dd5'), ObjectId('5eb63e1ee805d1cff3d80a25'), ObjectId('5eb63ee743b668cb27ef8137'), ObjectId('5eb640560732058562a400b3'), ObjectId('5eb646ce3b4442b4da91c057'), ObjectId('5eb6479687b6932b9e6de098'), ObjectId('5eb648bf6bc924ef46ab60da'), ObjectId('5eb64a8e96bdd2bbbb3287e5'), ObjectId('5eb64bc810a22fecd4eca987'), ObjectId('5eb64cfc8c94747a21f39855'), ObjectId('5eb64e13158973dfa9982019'), ObjectId('5eb64f4ea0549166c51ca057'), ObjectId('5eb650acab06d680d6990351'), ObjectId('5eb651bc5fa088c453991725'), ObjectId('5eb652de55de509b4a9efaf4'), ObjectId('5eb65433af5bcc3efe32c504'), ObjectId('5eb6556c29c37695bc97bec4'), ObjectId('5eb6567909d0de1b6b708cf8'), ObjectId('5eb657e754ee9cbe1a7388c8'), ObjectId('5eb65942b46918d079adebe9'), ObjectId('5eb65a927cb5b3a1ff4ae362'), ObjectId('5eb65b645417d406270e7e63'), ObjectId('5eb65d83728ad01002b3a5f6'), ObjectId('5eb65f2cde8cab37cd68dffd'), ObjectId('5eb6603b6e69c6f2e1092cf8'), ObjectId('5eb661a6796445df9bfd756d'), ObjectId('5eb6631b245b7e033d0f92ed'), ObjectId('5eb66401b0e60a643fae0467'), ObjectId('5eb6651284c93e9e1b685024'), ObjectId('5eb66682dc99a524418da337'), ObjectId('5eb667a554cc6bc47dbfea44'), ObjectId('5eb6688cf9acda3a876322e4'), ObjectId('5eb669883e6dc49bd6f1540f'), ObjectId('5eb66a9b90f9dd06f1107866'), ObjectId('5eb66bb449a0728d932475bc'), ObjectId('5eb66ce4535d821544a14dee'), ObjectId('5eb66dabf3d5b58ef16a4c74'), ObjectId('5eb66e99e95b7d86f2518828'), ObjectId('5eb66fa738555190120005d2'), ObjectId('5eb670c2382a70cea3c90149'), ObjectId('5eb672382cf60f5b673dc845'), ObjectId('5eb6734f61272a1489607d7c'), ObjectId('5eb6746b3f8078c646a32068'), ObjectId('5eb675384beae11731a0ce35'), ObjectId('5eb676209d0d155a1c6530f3'), ObjectId('5eb6777b140e783b3524f4d9'), ObjectId('5eb6783b3dd775bea489b02d'), ObjectId('5eb67952c38498d75c86627f'), ObjectId('5eb67a4c109ddab70aec7b2d'), ObjectId('5eb67bc12373d9a910e8750f'), ObjectId('5eb67d3dd9818bcd44884d39'), ObjectId('5eb67e66b7921dcf1c2e6805'), ObjectId('5eb67fa821374c1c36ea76bb'), ObjectId('5eb680d98c70c48229cd26b6'), ObjectId('5eb6820dcc1fecfea5009f48'), ObjectId('5eb682ecd810c81378eb806d'), ObjectId('5eb68405b8f3f1e1b3084a52'), ObjectId('5eb6853a626f824ef428e315'), ObjectId('5eb688a782ee2ac4699515f2'), ObjectId('5eb689814e048265dd507dbc'), ObjectId('5eb68a771a268ae85ef97960'), ObjectId('5eb68b52298db2bd4cebdd0e'), ObjectId('5eb68c65501e64174bede873'), ObjectId('5eb68d458e708541f4671189'), ObjectId('5eb68e2fab2ce0451e2b4056'), ObjectId('5eb68edce0b5b75b05fba1e6'), ObjectId('5eb690038f7f6e26b6253fd5'), ObjectId('5eb690bd8d99ac316303ffb6'), ObjectId('5eb6918fa2e66438837c2d83'), ObjectId('5eb6925a31a5f94e1207b916'), ObjectId('5eb6944565d7b2466379f198'), ObjectId('5eb694f59c10ae1d407b7c2a'), ObjectId('5eb695e1ffe996bbe09292fe'), ObjectId('5eb696f6ef36438bec383b7e'), ObjectId('5eb697cac579ca076779cb0f'), ObjectId('5eb698a46de98c90f95a497d'), ObjectId('5eb699a671806057e76f0141'), ObjectId('5eb69a7d5587c492135fd56c'), ObjectId('5eb69b6fc6cad85bd913e12a'), ObjectId('5eb69c52d1ecab806f2beead'), ObjectId('5eb69cefc81bdf1aac4bf6a1'), ObjectId('5eb69e087e9ea4385e20beed'), ObjectId('5eb69f48a04ce33b509b4895'), ObjectId('5eb6a058cd265d6ef2ee766f'), ObjectId('5eb6a12f7ef80a97c531cc67'), ObjectId('5eb6a21fe632eaf0b1d593db'), ObjectId('5eb6a63fc0820e4534126e94'), ObjectId('5eb6a72dfc5d1c47d4ca9cd1'), ObjectId('5eb6a8462d272649f7b4df95'), ObjectId('5eb6a930b440ebf60d42d6c2'), ObjectId('5eb6aa15b5b4db2c7393254c'), ObjectId('5eb6ab260aef4a583d77118f'), ObjectId('5eb6ac1bfff106a6f58c42e7'), ObjectId('5eb6ad1662db4e6c180a378b'), ObjectId('5eb6ae390bdb0b194f41f9b3'), ObjectId('5eb6af2a6012ca09c1728130'), ObjectId('5eb6afc4e15b344d1a3aafa0'), ObjectId('5eb6b19b1c6e630676c62445'), ObjectId('5eb6b2a5a9211572420260e9'), ObjectId('5eb6b38eeb5e21b75a0d7cdb'), ObjectId('5eb6b45f4dab807be8d7a28a'), ObjectId('5eb6b53fd8471918b43146b7'), ObjectId('5eb6b61fabf00d5fdb2d05a3'), ObjectId('5eb6b71e5cd9b7b54c7d9961'), ObjectId('5eb6b9158f232307ce0bdc13'), ObjectId('5eb6b9dbb8b6b03010c4dcc6'), ObjectId('5eb6bad32c05d6f34cf32652'), ObjectId('5eb6bbbee2f17c3f3238cec8'), ObjectId('5eb6bca1b68e7672cd0ef210'), ObjectId('5eb6bdb1e7b6cc4614eb0edb'), ObjectId('5eb6beca47492aa1e0553de4'), ObjectId('5eb6bfc707fd60d7d77844de'), ObjectId('5eb6644657dfd2c0b8ad6f9c'), ObjectId('5eb66630e46c2996611e7cc5'), ObjectId('5eb6670c8f3766d3901e7cc5'), ObjectId('5eb667a2f46d5b17e51e7cc5'), ObjectId('5eb66860dab176b3721e7cc5'), ObjectId('5eb6694f13214ceb901e7cc5'), ObjectId('5eb66a1c57d33385281e7cc5'), ObjectId('5eb66b0449715b12861e7cc5'), ObjectId('5eb66bf5c1cd3d67511e7cc5'), ObjectId('5eb66c7efae3969f0e1e7cc5'), ObjectId('5eb66d66b19f4175d41e7cc5'), ObjectId('5eb66e13afcaca79e81e7cc5'), ObjectId('5eb66f73241434c0231e7cc5'), ObjectId('5eb670975ce27f20651e7cc5'), ObjectId('5eb671403fb856baf01e7cc5'), ObjectId('5eb67202016c9eb49e1e7cc5'), ObjectId('5eb672855afc1f3bff1e7cc5'), ObjectId('5eb6732dc2f2cb21251e7cc5'), ObjectId('5eb674640480c494e21e7cc5'), ObjectId('5eb6753ed2085581291e7cc5'), ObjectId('5eb675ac19586b800c1e7cc5'), ObjectId('5eb6763b038d799aef1e7cc5'), ObjectId('5eb6776343946ae8fd1e7cc5'), ObjectId('5eb677f187e92c00051e7cc5'), ObjectId('5eb678eca5ef5a63181e7cc5'), ObjectId('5eb67989fc5079ac861e7cc5'), ObjectId('5eb67aa9307135b7481e7cc5'), ObjectId('5eb67c33c565dca3e61e7cc5'), ObjectId('5eb67d0c36a91550ff1e7cc5'), ObjectId('5eb67ddb4336d384b01e7cc5'), ObjectId('5eb67e90ae420cabcb1e7cc5'), ObjectId('5eb67f5ca8076cfd0a1e7cc5'), ObjectId('5eb68003bb68bcb7741e7cc5'), ObjectId('5eb6810f033af4b22b1e7cc5'), ObjectId('5eb681edb0a260b22a1e7cc5'), ObjectId('5eb682821dc3ebab081e7cc5'), ObjectId('5eb68355a25586c25d1e7cc5'), ObjectId('5eb6846e050a0737611e7cc5'), ObjectId('5eb6856e4c8a5b802f1e7cc5'), ObjectId('5eb6864268930af1f51e7cc5'), ObjectId('5eb686de941ea6f14b1e7cc5'), ObjectId('5eb688c6e8ba899a231e7cc5'), ObjectId('5eb689bf25abe779da1e7cc5'), ObjectId('5eb68afe1af2ab98d31e7cc5'), ObjectId('5eb68bf65c40e7d0d71e7cc5'), ObjectId('5eb68f5da4fd71f5821e7cc5'), ObjectId('5eb690478934691bf01e7cc5'), ObjectId('5eb6913eabf312822a1e7cc5'), ObjectId('5eb691e4f27c5211d21e7cc5'), ObjectId('5eb692b5bb6685adac1e7cc5'), ObjectId('5eb693d2d045d59f3b1e7cc5'), ObjectId('5eb6950c33fb947c391e7cc5'), ObjectId('5eb695e258473bd2511e7cc5'), ObjectId('5eb6968b400af16b271e7cc5'), ObjectId('5eb69733109de20b7e1e7cc5'), ObjectId('5eb697d1fb1caa3d7c1e7cc5'), ObjectId('5eb6988dc9615b33321e7cc5'), ObjectId('5eb69968d9785183931e7cc5'), ObjectId('5eb69a96a657bfc8991e7cc5'), ObjectId('5eb69c9f160e789d7e1e7cc5'), ObjectId('5eb69d5dd8d4ba89261e7cc5'), ObjectId('5eb69e1a46e5e5f33b1e7cc5'), ObjectId('5eb69f2843ef874fb81e7cc5'), ObjectId('5eb6a18ae6c27a5e961e7cc5'), ObjectId('5eb6a230795dc98ebd1e7cc5'), ObjectId('5eb6a2ee6c39588d0c1e7cc5'), ObjectId('5eb6a3d924946bdefc1e7cc5'), ObjectId('5eb6a504d1511c119a1e7cc5'), ObjectId('5eb6a5c37baf5cbfaa1e7cc5'), ObjectId('5eb6a670bc98e2e1471e7cc5'), ObjectId('5eb6a7b02266f527831e7cc5'), ObjectId('5eb6a895c2e3166bcc1e7cc5'), ObjectId('5eb6a9f32ea14a40531e7cc5'), ObjectId('5eb6aa92ee8178abc81e7cc5'), ObjectId('5eb6ab66c0c668b01d1e7cc5'), ObjectId('5eb6b0e61efe4c8c1f1e7cc5'), ObjectId('5eb6b168313d3030621e7cc5'), ObjectId('5eb6b201a201f790431e7cc5'), ObjectId('5eb6b361ce454282431e7cc5'), ObjectId('5eb6b3e04b08fc11b61e7cc5'), ObjectId('5eb6b49ef2b0c3149b1e7cc5'), ObjectId('5eb6b59f9ea7d290471e7cc5'), ObjectId('5eb6b675d1df7e04541e7cc5'), ObjectId('5eb6b75ef05682bd561e7cc5'), ObjectId('5eb6b8a9b0bfa077aa1e7cc5'), ObjectId('5eb6b928dd96b98b8b1e7cc5'), ObjectId('5eb6ba00d479014c311e7cc5'), ObjectId('5eb6bafd19a91c6bc11e7cc5'), ObjectId('5eb6bbe2c4e683d6001e7cc5'), ObjectId('5eb6bd08754af87d741e7cc5'), ObjectId('5eb6bd6f88582ed22e1e7cc5'), ObjectId('5eb6be6b9a04c870951e7cc5'), ObjectId('5eb6bf9531912db86d1e7cc5'), ObjectId('5eb6c13482dff544b31e7cc5'), ObjectId('5eb6c2265a296856911e7cc5'), ObjectId('5eb6c4f7fc8c7e73f71e7cc5'), ObjectId('5eb6c70a75e27bc9f01e7cc5'), ObjectId('5eb6c8e8f1c972d9d11e7cc5'), ObjectId('5eb6c9a73c6af847871e7cc5'), ObjectId('5eb6cad795a02f54c11e7cc5'), ObjectId('5eb6cbbb8e1ea19f721e7cc5'), ObjectId('5eb6cd0b76b872aac31e7cc5'), ObjectId('5eb6cf8d2afda4b75b1e7cc5'), ObjectId('5eb6d0b930966bc45d1e7cc5'), ObjectId('5eb6d180d6c5e588bc1e7cc5'), ObjectId('5eb6d2f157712c0e6b1e7cc5'), ObjectId('5eb6d3e51fd67335b41e7cc5'), ObjectId('5eb6d4b11fa223ec991e7cc5'), ObjectId('5eb6d573eeef09f4631e7cc5'), ObjectId('5eb6d5ed1ea282b3c71e7cc5'), ObjectId('5eb6d80ebb52c48b521e7cc5'), ObjectId('5eb6d92a12a10caf0b1e7cc5'), ObjectId('5eb6d9b2ad56eddd801e7cc5'), ObjectId('5eb6da581aea51c4141e7cc5'), ObjectId('5eb6db02d64b5ffaf01e7cc5'), ObjectId('5eb6dbee173c3e60211e7cc5'), ObjectId('5eb6dd0a8975e79a311e7cc5'), ObjectId('5eb6ddce3b3856712c1e7cc5'), ObjectId('5eb6de8bef8013ae3a1e7cc5'), ObjectId('5eb6dfa18548b41f1e1e7cc5'), ObjectId('5eb6e025a38f0a5bd51e7cc5'), ObjectId('5eb6e1bdc3b80c65f01e7cc5'), ObjectId('5eb6e2e985f544c0f31e7cc5'), ObjectId('5eb6e46fe2a11439211e7cc5'), ObjectId('5eb6e4e68944fb51261e7cc5'), ObjectId('5eb6e5f72810e4528c1e7cc5'), ObjectId('5eb6e71e229726a60d1e7cc5'), ObjectId('5eb6e833e6819157ab1e7cc5'), ObjectId('5eb6e92a73b223baa71e7cc5'), ObjectId('5eb6eb8eddadc0791a1e7cc5'), ObjectId('5eb6ecdfb8eac020ef1e7cc5'), ObjectId('5eb6ef069fd3d2700e1e7cc5'), ObjectId('5eb6f05e6cccb4ec201e7cc5'), ObjectId('5eb6f1abab044238231e7cc5'), ObjectId('5eb6f2785c17eeee301e7cc5'), ObjectId('5eb6f33f610110f7811e7cc5'), ObjectId('5eb6f5f338500f639d1e7cc5'), ObjectId('5eb6f75c547b2dc8a81e7cc5'), ObjectId('5eb6f86fa74f3f01391e7cc5'), ObjectId('5eb6faac13ef4ea5f11e7cc5'), ObjectId('5eb6fdc8c9af34d4321e7cc5'), ObjectId('5eb7015b64a4225c3e1e7cc5'), ObjectId('5eb701c9fd7dd6f0f81e7cc5'), ObjectId('5eb70303b9bd62c2d81e7cc5'), ObjectId('5eb707e40b3d32a9441e7cc5'), ObjectId('5eb70a317191684f471e7cc5'), ObjectId('5eb70b32d76dd257a81e7cc5'), ObjectId('5eb70c4eec6b83a56c1e7cc5'), ObjectId('5eb70d32fe79fe7ae11e7cc5'), ObjectId('5eb70dfc9b8c5669f61e7cc5'), ObjectId('5eb70e8d034df06da41e7cc5'), ObjectId('5eb70fe65ae110a83f1e7cc5'), ObjectId('5eb7108f8c31b21e521e7cc5'), ObjectId('5eb711cbd9698d895c1e7cc5'), ObjectId('5eb712ea41a21fd6dc1e7cc5'), ObjectId('5eb714466deb9085851e7cc5'), ObjectId('5eb714c5156d39e56e1e7cc5'), ObjectId('5eb7167ff888e8df4c1e7cc5'), ObjectId('5eb7172ad0c81b0d771e7cc5'), ObjectId('5eb718151826d970d21e7cc5'), ObjectId('5eb71938ccab1717f01e7cc5'), ObjectId('5eb71a2f30b005afe41e7cc5'), ObjectId('5eb71ad877b13eddbe1e7cc5'), ObjectId('5eb71ce921e8f2861f1e7cc5'), ObjectId('5eb71dca81f016c91a1e7cc5'), ObjectId('5eb71f0a7683d7d4101e7cc5'), ObjectId('5eb7203f4f2f7c0af81e7cc5'), ObjectId('5eb7213113ccf498df1e7cc5'), ObjectId('5eb7220bcc166c7e981e7cc5'), ObjectId('5eb72366ce65662b761e7cc5'), ObjectId('5eb7244a3dd3a2d7cc1e7cc5'), ObjectId('5eb72642b228878d531e7cc5'), ObjectId('5eb727cdaecb81e9bf1e7cc5'), ObjectId('5eb728f7fc797b3e091e7cc5'), ObjectId('5eb72aac0a755be3db1e7cc5'), ObjectId('5eb72bb61eabe2ed531e7cc5'), ObjectId('5eb72cf9e1fce67eae1e7cc5'), ObjectId('5eb730746bb3b692581e7cc5'), ObjectId('5eb730f0b6bdb8bbfc1e7cc5'), ObjectId('5eb731a0a3a39894761e7cc5'), ObjectId('5eb732a744e4da73881e7cc5'), ObjectId('5eb733f0abb68d26771e7cc5'), ObjectId('5eb734c35daa087a711e7cc5'), ObjectId('5eb735c8092b0431131e7cc5'), ObjectId('5eb73fde13df6f7b301e7cc5'), ObjectId('5eb7412226ae5213cf1e7cc5'), ObjectId('5eb7438bfa589ddb521e7cc5'), ObjectId('5eb74470a02a1a69941e7cc5'), ObjectId('5eb746a1e8e7f7509f1e7cc5'), ObjectId('5eb748526f5ea73b621e7cc5'), ObjectId('5eb74998ba43f388011e7cc5'), ObjectId('5eb74b1ffa73ce5db21e7cc5'), ObjectId('5eb74c79daf84fbe7c1e7cc5'), ObjectId('5eb74daa8e571dfa141e7cc5'), ObjectId('5eb7896b081724025f640206'), ObjectId('5eb7897f081724025f640207'), ObjectId('5eb78992081724025f640208'), ObjectId('5eb789a4081724025f640209'), ObjectId('5eb789b6081724025f64020a'), ObjectId('5eb789c9081724025f64020b'), ObjectId('5eb789dc081724025f64020c'), ObjectId('5eb789ee081724025f64020d'), ObjectId('5eb78a01081724025f64020e'), ObjectId('5eb78a13081724025f64020f'), ObjectId('5eb78a25081724025f640210'), ObjectId('5eb78a38081724025f640211'), ObjectId('5eb78a4a081724025f640212'), ObjectId('5eb78a5d081724025f640213'), ObjectId('5eb78a6f081724025f640214'), ObjectId('5eb78a82081724025f640215'), ObjectId('5eb78a95081724025f640216'), ObjectId('5eb78aa7081724025f640217'), ObjectId('5eb78aba081724025f640218'), ObjectId('5eb7aadc52f1054848f5583f'), ObjectId('5eb7ab0452f1054848f55840'), ObjectId('5eb7ab3552f1054848f55841'), ObjectId('5eb7ab4752f1054848f55842'), ObjectId('5eb7ab5a52f1054848f55843'), ObjectId('5eb7ab6d52f1054848f55844'), ObjectId('5eb7ab8052f1054848f55845'), ObjectId('5eb7ab9252f1054848f55846'), ObjectId('5eb7abc752f1054848f55847'), ObjectId('5eb7abda52f1054848f55848'), ObjectId('5eb7abec52f1054848f55849'), ObjectId('5eb7bf7b11ad0e77a8454c20'), ObjectId('5eb7bf9a11ad0e77a8454c21'), ObjectId('5eb7bfac11ad0e77a8454c22'), ObjectId('5eb7bfe611ad0e77a8454c23'), ObjectId('5eb7c00211ad0e77a8454c24'), ObjectId('5eb7c01411ad0e77a8454c25'), ObjectId('5eb7c02811ad0e77a8454c26'), ObjectId('5eb7c03b11ad0e77a8454c27'), ObjectId('5eb7c04d11ad0e77a8454c28'), ObjectId('5eb7c05f11ad0e77a8454c29'), ObjectId('5eb7c07c11ad0e77a8454c2a'), ObjectId('5eb7c08e11ad0e77a8454c2b'), ObjectId('5eb7c0a011ad0e77a8454c2c'), ObjectId('5eb81d4d312f24e51eaa1661'), ObjectId('5eb81d6b312f24e51eaa1662'), ObjectId('5eb81d7d312f24e51eaa1663'), ObjectId('5eb81da1312f24e51eaa1664'), ObjectId('5eb81db3312f24e51eaa1665'), ObjectId('5eb81dc6312f24e51eaa1666'), ObjectId('5eb81dd8312f24e51eaa1667'), ObjectId('5eb81dea312f24e51eaa1668'), ObjectId('5eb81dfd312f24e51eaa1669'), ObjectId('5eb81e2a312f24e51eaa166a'), ObjectId('5eb81e3d312f24e51eaa166b'), ObjectId('5eb81e4f312f24e51eaa166c'), ObjectId('5eb83bb0c20632fd5f21f86d'), ObjectId('5eb83c8a6623055fd421f86d'), ObjectId('5eb83dd63612e8063d21f86d'), ObjectId('5eb83e9d7f0be3c68d21f86d'), ObjectId('5eb83f62e799b9666421f86d'), ObjectId('5eb8417497a7e1b24921f86d'), ObjectId('5eb842cdd24ad47da321f86d'), ObjectId('5eb84387d74544658d21f86d'), ObjectId('5eb844b48bd34e3bcb21f86d'), ObjectId('5eb8452dab8cc3965d21f86d'), ObjectId('5eb845f3acb80ec7c321f86d'), ObjectId('5eb846d473cb9c981121f86d'), ObjectId('5eb847ff38670c0bf521f86d'), ObjectId('5eb848f164dc91c82021f86d'), ObjectId('5eb84a27e7e7c4410d21f86d'), ObjectId('5eb84b2e74c886c55621f86d'), ObjectId('5eb84bdab796088dd121f86d'), ObjectId('5eb84df11ad39fb85b21f86d'), ObjectId('5eb84eadd4bb82049521f86d'), ObjectId('5eb84fe508717ac7dd21f86d'), ObjectId('5eb8517e89396f769e21f86d'), ObjectId('5eb85245d92e9c836b21f86d'), ObjectId('5eb853490aaf61fffc21f86d'), ObjectId('5eb8545dbd6648186b21f86d'), ObjectId('5eb855aa4a7a482fac21f86d'), ObjectId('5eb856dcb34632d71421f86d'), ObjectId('5eb858ab89ca8a714f21f86d'), ObjectId('5eb85a05917001c29321f86d'), ObjectId('5eb85afdfdc73635ab21f86d'), ObjectId('5eb85c4ac83e2ed19721f86d'), ObjectId('5eb85d15da02c4e01821f86d'), ObjectId('5eb85dab7bfffd11c521f86d'), ObjectId('5eb85e43aa8c7e619421f86d'), ObjectId('5eb85f63862fafb0e021f86d'), ObjectId('5eb86122ce929d30d721f86d'), ObjectId('5eb8623bdac3bd4e7f21f86d'), ObjectId('5eb86330ca955600ac21f86d'), ObjectId('5eb863dbb3620c184721f86d'), ObjectId('5eb86507eaccbefb4d21f86d'), ObjectId('5eb866198421e3010421f86d'), ObjectId('5eb8672d51cf71b03d21f86d'), ObjectId('5eb8685ab30e6a462321f86d'), ObjectId('5eb868ec94d882c47c21f86d'), ObjectId('5eb86a31de8016954a21f86d'), ObjectId('5eb86b55f632667f7e21f86d'), ObjectId('5eb86c08d1a5f8db5f21f86d'), ObjectId('5eb86cc182031d652821f86d'), ObjectId('5eb86d4e9609a169d021f86d'), ObjectId('5eb86dfe3b429177a721f86d'), ObjectId('5eb86e7cac9651095921f86d'), ObjectId('5eb86f7613cbb54fe721f86d'), ObjectId('5eb870500793149fa821f86d'), ObjectId('5eb871bfb7374d40cf21f86d'), ObjectId('5eb873c205f65c055421f86d'), ObjectId('5eb8754af638182f4521f86d'), ObjectId('5eb8760ff7dcca255d21f86d'), ObjectId('5eb87727974768f30821f86d'), ObjectId('5eb8780e8d8c35ca9c21f86d'), ObjectId('5eb87917ea8377045721f86d'), ObjectId('5eb879f2b83e5d3a8e21f86d'), ObjectId('5eb87a9ca4a19ac29321f86d'), ObjectId('5eb87ba1dc1e218e7421f86d'), ObjectId('5eb87c945b332f05d121f86d'), ObjectId('5eb87dbc2074be568b21f86d'), ObjectId('5eb87eca54f8828b4e21f86d'), ObjectId('5eb87fb20c0112b7ad21f86d'), ObjectId('5eb880b1614e84a77a21f86d'), ObjectId('5eb881e8f31ce00d4a21f86d'), ObjectId('5eb8831ab323150e1621f86d'), ObjectId('5eb88412761d7e71c921f86d'), ObjectId('5eb884e6d62901c44821f86d'), ObjectId('5eb885858ec581dcd221f86d'), ObjectId('5eb886a2151d63eaee21f86d'), ObjectId('5eb88723f57be6e74e21f86d'), ObjectId('5eb88819f0ffd1483a21f86d'), ObjectId('5eb888dcfd39cc64d921f86d'), ObjectId('5eb889f4ff01ae732f21f86d'), ObjectId('5eb88ad5479569d7e321f86d'), ObjectId('5eb88bbf9c23677f5c21f86d'), ObjectId('5eb88d68f362f40c3421f86d'), ObjectId('5eb88e682df9b5110721f86d'), ObjectId('5eb88f98a60f86f3ef21f86d'), ObjectId('5eb890aa418697e9e421f86d'), ObjectId('5eb8921599a8e5b1f621f86d'), ObjectId('5eb8933c424b54e75121f86d'), ObjectId('5eb8943b6f1514ca3321f86d'), ObjectId('5eb89535aabccb4aab21f86d'), ObjectId('5eb896c896f67bcbc321f86d'), ObjectId('5eb8978f89169ba53d21f86d'), ObjectId('5eb898be51220c01de21f86d'), ObjectId('5eb89a57e84723b8ec21f86d'), ObjectId('5eb89c1e05692d835d21f86d'), ObjectId('5eb89d659149fe900a21f86d'), ObjectId('5eb89df91960c5e9ec21f86d'), ObjectId('5eb89ecd8bf8c16ccf21f86d'), ObjectId('5eb89febd32a61b6c321f86d'), ObjectId('5eb8a1447e730f301521f86d'), ObjectId('5eb8a239464da6884521f86d'), ObjectId('5eb8a30c88d5b4a59121f86d'), ObjectId('5eb8a3f0482eb3feca21f86d'), ObjectId('5eb8a4a6ae599bdfa921f86d'), ObjectId('5eb8a5d1d36fe9f4e121f86d'), ObjectId('5eb8a709099797362b21f86d'), ObjectId('5eb8a83745cee6157a21f86d'), ObjectId('5eb8a955ddc60d84d721f86d'), ObjectId('5eb8aa2e549e722cf921f86d'), ObjectId('5eb8ab15843916c1ec21f86d'), ObjectId('5eb8ab897019bd41e021f86d'), ObjectId('5eb8acf5ec58bd651021f86d'), ObjectId('5eb8adf340037d708b21f86d'), ObjectId('5eb8aed47b8ce2708b21f86d'), ObjectId('5eb8b0273477405e3921f86d'), ObjectId('5eb8b16eeb46817aa921f86d'), ObjectId('5eb8b262c08e90f27321f86d'), ObjectId('5eb8b2c39a33df091821f86d'), ObjectId('5eb8b3cd429175d72321f86d'), ObjectId('5eb8b4c5d1c21dd7ce21f86d'), ObjectId('5eb8b5d7c385759b1421f86d'), ObjectId('5eb8b75137347cbaa321f86d'), ObjectId('5eb8b84c47dde0acac21f86d'), ObjectId('5eb8b912b06f3bcb0421f86d'), ObjectId('5eb8b9855c080d2f1121f86d'), ObjectId('5eb8ba493dc9c4974f21f86d'), ObjectId('5eb8bb252743a7288021f86d'), ObjectId('5eb8bcdf968edc55ea21f86d'), ObjectId('5eb8bd998572a191e321f86d'), ObjectId('5eb8bea3f03d66565d21f86d'), ObjectId('5eb8bfba829032dce021f86d'), ObjectId('5eb8c14565f929811d21f86d'), ObjectId('5eb8c1d5fe1ba67fcd21f86d'), ObjectId('5eb8c2b414da7621f021f86d'), ObjectId('5eb8c3875259f3781f21f86d'), ObjectId('5eb8c491832b7b76fa21f86d'), ObjectId('5eb8c5fcb8a1c0352b21f86d'), ObjectId('5eb8c6dcb28e55297a21f86d'), ObjectId('5eb8c7e1d74c10705521f86d'), ObjectId('5eb8c9b046a9eb0b8621f86d'), ObjectId('5eb8ca4045be5799f521f86d'), ObjectId('5eb8cb349dcab3b90c21f86d'), ObjectId('5eb8cc5df291ba000021f86d'), ObjectId('5eb8ccfeb6f8890b1521f86d'), ObjectId('5eb8cee6ce909d778c21f86d'), ObjectId('5eb8d0d95c7b35b7c421f86d'), ObjectId('5eb8d1d3c01e5308b521f86d'), ObjectId('5eb8d3459b83f4fa6121f86d'), ObjectId('5eb8d4fdabcf9fb65c21f86d'), ObjectId('5eb8d5cb9be0efb86721f86d'), ObjectId('5eb8d681e47422a52421f86d'), ObjectId('5eb8d6fa86dbdd4f6221f86d'), ObjectId('5eb8d806a0f83f495121f86d'), ObjectId('5eb8d9a9e7a770a3ad21f86d'), ObjectId('5eb8dab1a54485a67d21f86d'), ObjectId('5eb8dbd9e608e62aa921f86d'), ObjectId('5eb8dd2eb8359de9fb21f86d'), ObjectId('5eb8de14e961249cf821f86d'), ObjectId('5eb8df468065ee492521f86d'), ObjectId('5eb8e093f2829184d021f86d'), ObjectId('5eb8e1c5e383a8096121f86d'), ObjectId('5eb8e23d68e392761821f86d'), ObjectId('5eb8e35659da95b81421f86d'), ObjectId('5eb8e4508f2df69ea521f86d'), ObjectId('5eb8e5bd8973815f4521f86d'), ObjectId('5eb8e7228500cd563621f86d'), ObjectId('5eb8e813d9d2c9f40121f86d'), ObjectId('5eb8e90528a65c503a21f86d'), ObjectId('5eb8ea3dade030acbc21f86d'), ObjectId('5eb8eb8f7e96c2e52021f86d'), ObjectId('5eb8ec3968930ce0dc21f86d'), ObjectId('5eb8eec96236e1001721f86d'), ObjectId('5eb8ef7b29e2302f9421f86d'), ObjectId('5eb8f03f60558f7f2821f86d'), ObjectId('5eb8f0f37637ebf2f421f86d'), ObjectId('5eb8f199e3d0f6397321f86d'), ObjectId('5eb8f298726ce61bc621f86d'), ObjectId('5eb8f3298d159182be21f86d'), ObjectId('5eb8f4027596476b4e21f86d'), ObjectId('5eb8f4c8b81159e2d121f86d'), ObjectId('5eb8f590fdb965d43a21f86d'), ObjectId('5eb8f6b6214f14826b21f86d'), ObjectId('5eb8f7d0b6e2fbd56f21f86d'), ObjectId('5eb8f8f640293aa81821f86d'), ObjectId('5eb8f9a0e6440a6b8a21f86d'), ObjectId('5eb8fa6df0d07e01bb21f86d'), ObjectId('5eb8fb6637371fbadd21f86d'), ObjectId('5eb8fc2111aa8649a021f86d'), ObjectId('5eb8fd315118a2341121f86d'), ObjectId('5eb8fddd76e458d1f521f86d'), ObjectId('5eb8fe80ab6df587b721f86d'), ObjectId('5eb8ff3c18d32b70bd21f86d'), ObjectId('5eb8ffde228b9dcd4721f86d'), ObjectId('5eb900d48f9aa5e01421f86d'), ObjectId('5eb9016e0b29a3ec7b21f86d'), ObjectId('5eb90231d7710ea89e21f86d'), ObjectId('5eb9030223ce0eaa0e21f86d'), ObjectId('5eb903bd297b7ab6ea21f86d'), ObjectId('5eb90466b8ff202ce721f86d'), ObjectId('5eb9051bd7cc3fdd4a21f86d'), ObjectId('5eb906268b04d8180921f86d'), ObjectId('5eb906b4ac1b87756821f86d'), ObjectId('5eb907adb885b0595e21f86d'), ObjectId('5eb908650c9ba6d0c721f86d'), ObjectId('5eb9098a548b88f22f21f86d'), ObjectId('5eb90aa037a21af96a21f86d'), ObjectId('5eb90b6ff57c66a55021f86d'), ObjectId('5eb90c97d95f0dfd8321f86d'), ObjectId('5eb90d26c24efc344421f86d'), ObjectId('5eb90defe65269ec2921f86d'), ObjectId('5eb90edc081077a28221f86d'), ObjectId('5eb90ff42891822aa721f86d'), ObjectId('5eb910de6bc058e77521f86d'), ObjectId('5eb9121e6b00d398d321f86d'), ObjectId('5eb912f7cf42d0dd1321f86d'), ObjectId('5eb913be1fed838a5421f86d'), ObjectId('5eb914608106a0349521f86d'), ObjectId('5eb915c6fee756399921f86d'), ObjectId('5eb9165c2023b5b0a221f86d'), ObjectId('5eb9172a5f87037fd821f86d'), ObjectId('5eb91804d3c4eabcb021f86d'), ObjectId('5eb918f8be95d058e821f86d'), ObjectId('5eb919d57a1990cecb21f86d'), ObjectId('5eb91ae4754abd427521f86d'), ObjectId('5eb91b88f67f334bd121f86d'), ObjectId('5eb91c5c9952bbf5a121f86d'), ObjectId('5eb91d09164fbbbaac21f86d'), ObjectId('5eb91da3788ecf0ce521f86d'), ObjectId('5eb91e8fa56f9483ce21f86d'), ObjectId('5eb91f39ed94b2224a21f86d'), ObjectId('5eb91ff051c237641c21f86d'), ObjectId('5eb920f94efa4817c021f86d'), ObjectId('5eb921bdedc138291621f86d'), ObjectId('5eb922aecb23d6990521f86d'), ObjectId('5eb923e3a13ac27f3a21f86d'), ObjectId('5eb9248a5ed09e3eea21f86d'), ObjectId('5eb92552b5646f410c21f86d'), ObjectId('5eb9263c768da2781321f86d'), ObjectId('5eb927549b6f7b419d21f86d'), ObjectId('5eb9282909dc67e37421f86d'), ObjectId('5eb929221bbcf7be6f21f86d'), ObjectId('5eb92a461d8435dcd921f86d'), ObjectId('5eb92afa636ef5238c21f86d'), ObjectId('5eb92ba8400dbda15921f86d'), ObjectId('5eb92c710bba61585121f86d'), ObjectId('5eb92d1830daa2538321f86d'), ObjectId('5eb92db361dff8952121f86d'), ObjectId('5eb92e3a89f495fffb21f86d'), ObjectId('5eb92f14ab9ce4f52721f86d'), ObjectId('5eb92fbf0c67b29a9d21f86d'), ObjectId('5eb9312dd15399709d21f86d'), ObjectId('5eb9323b820a6f535621f86d'), ObjectId('5eb93372d46993fbd721f86d'), ObjectId('5eb93429f1f936171a21f86d'), ObjectId('5eb93528186ec1081a21f86d'), ObjectId('5eb93751a44b8aefc721f86d'), ObjectId('5eb9381f8c2abb0f7a21f86d'), ObjectId('5eb938c55389d4db7521f86d'), ObjectId('5eb93967d1022da19a21f86d'), ObjectId('5eb93a35286bebbd3721f86d'), ObjectId('5eb93ad6ca0222976421f86d'), ObjectId('5eb93ba69a5bb9122221f86d'), ObjectId('5eb93ca853c2585cd021f86d'), ObjectId('5eb93d70f717e1186221f86d'), ObjectId('5eb93e5a0f155b463f21f86d'), ObjectId('5eb93f261b3133e13e21f86d'), ObjectId('5eb93fc62c92f2fd7a21f86d'), ObjectId('5eb9406f046057c71821f86d'), ObjectId('5eb940f8afecef72d421f86d'), ObjectId('5eb942ca6c178e0efd21f86d'), ObjectId('5eb94474a5cacd316f21f86d'), ObjectId('5eb945325c630e50b121f86d'), ObjectId('5eb945fbae4b1c370c21f86d'), ObjectId('5eb946b622486d789a21f86d'), ObjectId('5eb9476fbc961c207721f86d'), ObjectId('5eb9482c9f4c1019e321f86d'), ObjectId('5eb9492babf495d98021f86d'), ObjectId('5eb94a4a475222827e21f86d'), ObjectId('5eb94b5d81f9e4fb7a21f86d'), ObjectId('5eb94caf01a53921bf21f86d'), ObjectId('5eb94e5a2b07874ec121f86d'), ObjectId('5eb953a6814e7d21e321f86d'), ObjectId('5eb954b4f35a078cf721f86d'), ObjectId('5eb955a2e5f652442821f86d'), ObjectId('5eb95622a2c1b74c6221f86d'), ObjectId('5eb956c2bcbd15f71721f86d'), ObjectId('5eb9575c09862b02c421f86d'), ObjectId('5eb957e0b1f04156bd21f86d'), ObjectId('5eb958ead7392a242521f86d'), ObjectId('5eb959a6a700a8698721f86d'), ObjectId('5eb95a61fcaba234be21f86d'), ObjectId('5eb95b4882f4282eca21f86d'), ObjectId('5eb95cfb74762e537021f86d'), ObjectId('5eb95e0b322ca6d92b21f86d'), ObjectId('5eb95ee13787207a7121f86d'), ObjectId('5eb960159b562cfe5121f86d'), ObjectId('5eb961218c2c25bba721f86d'), ObjectId('5eb9623e7d5b6734b221f86d'), ObjectId('5eb9631ee5516c892621f86d'), ObjectId('5eb964411c69e097b721f86d'), ObjectId('5eb96558e18d2010a521f86d'), ObjectId('5eb96699db4578f41e21f86d'), ObjectId('5eb96777c06cc7453321f86d'), ObjectId('5eb968a6866513087c21f86d'), ObjectId('5eb969ff340cfd882f21f86d'), ObjectId('5eb96b5f67ab27c7ad21f86d'), ObjectId('5eb96c713854c44c7c21f86d'), ObjectId('5eb96e930abe67402d21f86d'), ObjectId('5eb96f8410dbd1b97121f86d'), ObjectId('5eb97050e14afd37d421f86d'), ObjectId('5eb97181a1c0acf29521f86d'), ObjectId('5eb9729dcfb1b5aedc21f86d'), ObjectId('5eb97380f4737bdfc621f86d'), ObjectId('5eb974b0d87fa029cc21f86d'), ObjectId('5eb975ec968778eb8321f86d'), ObjectId('5eb9773a705bc362dd21f86d'), ObjectId('5eb978928fcb381c9821f86d'), ObjectId('5eb979e6a8267a4cf321f86d'), ObjectId('5eb97b0f60e92f6b3c21f86d'), ObjectId('5eb97cb0b1b81f1f1121f86d'), ObjectId('5eb97d68a224556d5021f86d'), ObjectId('5eb97defa49bce200921f86d'), ObjectId('5eb97f0e0983cb7e1b21f86d'), ObjectId('5eb98037bd57a54e0921f86d'), ObjectId('5eb9814a3aa1b7828e21f86d'), ObjectId('5eb9828938c7d411f521f86d'), ObjectId('5eb983e524cbf9087f21f86d'), ObjectId('5eb98518b78a7be0a921f86d'), ObjectId('5eb985c3d4acd4f70321f86d'), ObjectId('5eb986b68377e255da21f86d'), ObjectId('5eb987b62d22e3927d21f86d'), ObjectId('5eb988e826bc569c4521f86d'), ObjectId('5eb98a0cf9f33e743e21f86d'), ObjectId('5eb98b60bd0350ef9421f86d'), ObjectId('5eb98c1aa42c5bfdb221f86d'), ObjectId('5eb98cc54fb80cdf1921f86d'), ObjectId('5eb98e6877b6929b6021f86d'), ObjectId('5eb98f63c77b06851a21f86d'), ObjectId('5eb98fe243b394756d21f86d'), ObjectId('5eb990fd55b72b8c5121f86d'), ObjectId('5eb991c373c817b2bb21f86d'), ObjectId('5eb992c4c0fd5f51a121f86d'), ObjectId('5eb99398736b4cd23721f86d'), ObjectId('5eb994d95eab3ba67221f86d'), ObjectId('5eb995d5fe3c5625c521f86d'), ObjectId('5eb996a983125131a121f86d'), ObjectId('5eb997dc39cd53206621f86d'), ObjectId('5eb998b240569a005a21f86d'), ObjectId('5eb999b37b891cb90621f86d'), ObjectId('5eb99acd846eb61f2a21f86d'), ObjectId('5eb99bcf2818e7046021f86d'), ObjectId('5eb99c9e646e68a4be21f86d'), ObjectId('5eb99d7f9b164a7cae21f86d'), ObjectId('5eb99e60690e8264fc21f86d'), ObjectId('5eb99f05e49d1227cd21f86d'), ObjectId('5eb99f72890089aa8921f86d'), ObjectId('5eb9a02446ec38c9b221f86d'), ObjectId('5eb9a0e02afb29a0c221f86d'), ObjectId('5eb9a2131454cdd80c21f86d'), ObjectId('5eb9a3161c2a9e14cd21f86d'), ObjectId('5eb9a4394b823b542921f86d'), ObjectId('5eb9a510ede9d735bb21f86d'), ObjectId('5eb9a5c5c24f6024db21f86d'), ObjectId('5eb9a6ddfce4130a7921f86d'), ObjectId('5eb9a7a0a5df084c9521f86d'), ObjectId('5eb9a90b6ed7a467e521f86d'), ObjectId('5eb9a9faae3bf308b421f86d'), ObjectId('5eb9ab221619cc9dc321f86d'), ObjectId('5eb9ac3d09f67fba8521f86d'), ObjectId('5eb9ad5d70c1226baa21f86d'), ObjectId('5eb9aea5fea105dfcb21f86d'), ObjectId('5eb9af637342fa7aa621f86d'), ObjectId('5eb9b040a8f4550b7f21f86d'), ObjectId('5eb9b1450406e3e2b321f86d'), ObjectId('5eb9b28a501fa5268421f86d'), ObjectId('5eb9b3072fc2705be521f86d'), ObjectId('5eb9b3801885a6622921f86d'), ObjectId('5eb9b44d4ee0fd99bb21f86d'), ObjectId('5eb9b517d4ae71db7f21f86d'), ObjectId('5eb9b5c9c60e3be81421f86d'), ObjectId('5eb9b7a6206f878ed521f86d'), ObjectId('5eb9b87e9dd4c7ca0621f86d'), ObjectId('5eb9b94210d23baa8f21f86d'), ObjectId('5eb9ba554ec213f32d21f86d'), ObjectId('5eb9bb86c18b4ececb21f86d'), ObjectId('5eb9bc50d2451747b621f86d'), ObjectId('5eb9bd5a3ad6427d8721f86d'), ObjectId('5eb9be1269310756c221f86d'), ObjectId('5eb9bf57b3f56179ae21f86d'), ObjectId('5eb9bfd43cef2bdc8b21f86d'), ObjectId('5eb9c193286421764421f86d'), ObjectId('5eb9c21d2884e8e37021f86d'), ObjectId('5eb9c35fea7b131dc021f86d'), ObjectId('5eb9c465c47657758321f86d'), ObjectId('5eb9c525b11354116b21f86d'), ObjectId('5eb9c643e192bb672a21f86d'), ObjectId('5eb9c762343f83b86d21f86d'), ObjectId('5eb9c864a7682e360921f86d'), ObjectId('5eb9c943cd65d837aa21f86d'), ObjectId('5eba2263f773e4001a6aa0f6'), ObjectId('5eba2352cedb2578006aa0f6'), ObjectId('5eba23efdd87446de86aa0f6'), ObjectId('5eba257fcc2f2c7c9c6aa0f6'), ObjectId('5eba2665b027044d6e6aa0f6'), ObjectId('5eba27389dcc86f4c06aa0f6'), ObjectId('5eba280fe4f85334f86aa0f6'), ObjectId('5eba28e8099768a4226aa0f6'), ObjectId('5eba29b6e888782e336aa0f6'), ObjectId('5eba2a5fec4bf6a2ac6aa0f6'), ObjectId('5eba2b4bc2a93be6f36aa0f6'), ObjectId('5eba2bcac660d396e06aa0f6'), ObjectId('5eba2c7910d3fcd0016aa0f6'), ObjectId('5eba2d1a34b0c190d96aa0f6'), ObjectId('5eba2df4477d2e3b636aa0f6'), ObjectId('5eba2f018e651e78046aa0f6'), ObjectId('5eba2f87b8a341be376aa0f6'), ObjectId('5eba300c9e893551cd6aa0f6'), ObjectId('5eba31b7f6172358836aa0f6'), ObjectId('5eba329963a55f0c8c6aa0f6'), ObjectId('5eba3301cfa7ca34776aa0f6'), ObjectId('5eba33ba769415bf8e6aa0f6'), ObjectId('5eba348b1bb03934586aa0f6'), ObjectId('5eba35a621d955a8846aa0f6'), ObjectId('5eba366d4f17291cf16aa0f6'), ObjectId('5eba377b06d5d7cae86aa0f6'), ObjectId('5eba37f95f008936766aa0f6'), ObjectId('5eba38c76af7ef3b7e6aa0f6'), ObjectId('5eba39d8508b3ebd7d6aa0f6'), ObjectId('5eba3ac085bbe969606aa0f6'), ObjectId('5eba3bc367f232bfc66aa0f6'), ObjectId('5eba3c539b68e6839d6aa0f6'), ObjectId('5eba3d4411a138ad6c6aa0f6'), ObjectId('5eba3e291a4d4152146aa0f6'), ObjectId('5eba3eb48cfb836bb26aa0f6'), ObjectId('5eba3f7712384cd39f6aa0f6'), ObjectId('5eba405603a6b818b36aa0f6'), ObjectId('5eba41451c03037ed46aa0f6'), ObjectId('5eba41f3e5f55f61626aa0f6'), ObjectId('5eba42c76eff662a836aa0f6'), ObjectId('5eba438af8df0e405c6aa0f6'), ObjectId('5eba44dffaff1040856aa0f6'), ObjectId('5eba465367e2e0746e6aa0f6'), ObjectId('5eba4709e77bc924246aa0f6'), ObjectId('5eba47b9b707e6f1e06aa0f6'), ObjectId('5eba48a2233f736bf66aa0f6'), ObjectId('5eba49569c892864786aa0f6'), ObjectId('5eba4a66d6d6339c0c6aa0f6'), ObjectId('5eba4d1c7865b19fa46aa0f6'), ObjectId('5eba4dd122d2726da76aa0f6'), ObjectId('5eba4f212327b4ff6a6aa0f6'), ObjectId('5eba4fe33a6073535d6aa0f6'), ObjectId('5eba5150149ebad13e6aa0f6'), ObjectId('5eba5331bb1bc22a246aa0f6'), ObjectId('5eba54d650564c9d836aa0f6'), ObjectId('5eba55801730aa03736aa0f6'), ObjectId('5eba567e096b17a0416aa0f6'), ObjectId('5eba57766d39f1ec2d6aa0f6'), ObjectId('5eba58cc19effd0e1a6aa0f6'), ObjectId('5eba59d4ae344110c06aa0f6'), ObjectId('5eba5b4b0f90c581b16aa0f6'), ObjectId('5eba5c24a3fd3760796aa0f6'), ObjectId('5eba5e0ce7638ef1516aa0f6'), ObjectId('5eba5ed41ca960da286aa0f6'), ObjectId('5eba60afba4fa3b36b6aa0f6'), ObjectId('5eba625b2d49e42e1c6aa0f6'), ObjectId('5eba630ac6804396ae6aa0f6'), ObjectId('5eba639dfe9d26a2cc6aa0f6'), ObjectId('5eba64b3905430eac56aa0f6'), ObjectId('5eba65976eef9fd32c6aa0f6'), ObjectId('5eba66a2de6f378f236aa0f6'), ObjectId('5eba67bb80950b7e306aa0f6'), ObjectId('5eba68fe5678fd00496aa0f6'), ObjectId('5eba6ab9dec9a444e86aa0f6'), ObjectId('5eba6bee75d3f006bf6aa0f6'), ObjectId('5eba6cd088ad4c0ff46aa0f6'), ObjectId('5eba6d4cd5ace97fb96aa0f6'), ObjectId('5eba6f05f4e96945a06aa0f6'), ObjectId('5eba7019c89d3f6e6a6aa0f6'), ObjectId('5eba711df07d9dbde96aa0f6'), ObjectId('5eba71b43d0da18b486aa0f6'), ObjectId('5eba72bf29bfd4fe486aa0f6'), ObjectId('5eba73be695509da3a6aa0f6'), ObjectId('5eba75450f6888ba2a6aa0f6'), ObjectId('5eba76512d6b7665f26aa0f6'), ObjectId('5eba7784b7471b3d796aa0f6'), ObjectId('5eba78960d9267723e6aa0f6'), ObjectId('5eba798394297e61d66aa0f6'), ObjectId('5eba7a7c8da40306ca6aa0f6'), ObjectId('5eba7bb375c77e62786aa0f6'), ObjectId('5eba7c6f8806297a7f6aa0f6'), ObjectId('5eba7d9acbebed16d16aa0f6'), ObjectId('5eba7e6a4ac93d07586aa0f6'), ObjectId('5eba7f641e610563e56aa0f6'), ObjectId('5eba8076eaae1336ac6aa0f6'), ObjectId('5eba81a29ac6ca027f6aa0f6'), ObjectId('5eba82d61569ae110d6aa0f6'), ObjectId('5eba83dc15c6efd50b6aa0f6'), ObjectId('5eba8547f25e4d61306aa0f6'), ObjectId('5eba873f2222b725b06aa0f6'), ObjectId('5eba87f883988b10aa6aa0f6'), ObjectId('5eba8963179bd48ab86aa0f6'), ObjectId('5eba8a414f293d8b036aa0f6'), ObjectId('5eba8b7bc165ac9a746aa0f6'), ObjectId('5eba8c007638f1558f6aa0f6'), ObjectId('5eba8ccb06aa805bef6aa0f6'), ObjectId('5eba8e0aae92c041386aa0f6'), ObjectId('5eba8ee7fbda26ac916aa0f6'), ObjectId('5eba9047a23e7af6b16aa0f6'), ObjectId('5eba91fff4b97f0bcb6aa0f6'), ObjectId('5eba9279d9e37a11566aa0f6'), ObjectId('5eba9323df5007ab736aa0f6'), ObjectId('5eba94739a5d337aba6aa0f6'), ObjectId('5eba9943e741efec006aa0f6'), ObjectId('5eba9a4ea65fa58bb06aa0f6'), ObjectId('5eba9b43e77fdcce046aa0f6'), ObjectId('5eba9c8a968247a8d76aa0f6'), ObjectId('5eba9dbe1bf1e1ed036aa0f6'), ObjectId('5eba9e6b969fcf61496aa0f6'), ObjectId('5eba9fd947665f99366aa0f6'), ObjectId('5ebaa11b7d17877bda6aa0f6'), ObjectId('5ebaa2c4104f2af4a96aa0f6'), ObjectId('5ebaa3cddd085426996aa0f6'), ObjectId('5ebaa4cbb057c14adb6aa0f6'), ObjectId('5ebaa5c8353d52e82e6aa0f6'), ObjectId('5ebaa6d4722cd892f56aa0f6'), ObjectId('5ebaa7cef9260e981b6aa0f6'), ObjectId('5ebaa88bb5b73f3fcb6aa0f6'), ObjectId('5ebaa9912eb6b5d8f26aa0f6'), ObjectId('5ebaaa8d1ac51d6f916aa0f6'), ObjectId('5ebaab8780587d952a6aa0f6'), ObjectId('5ebaac2b193157f6836aa0f6'), ObjectId('5ebaadebdb317e012b6aa0f6'), ObjectId('5ebaaedd4ced4de4306aa0f6'), ObjectId('5ebab0035cabfab4ef6aa0f6'), ObjectId('5ebab1279bd6e029266aa0f6'), ObjectId('5ebab2306a4e27a8386aa0f6'), ObjectId('5ebab33361d9f5e2666aa0f6'), ObjectId('5ebab3c510300b5ff76aa0f6'), ObjectId('5ebab4413d218c114f6aa0f6'), ObjectId('5ebab4fdbd5947bb256aa0f6'), ObjectId('5ebab5c182b35e046c6aa0f6'), ObjectId('5ebab6c12780d878da6aa0f6'), ObjectId('5ebab7794a8f375c3b6aa0f6'), ObjectId('5ebab834bfb2fd001a6aa0f6'), ObjectId('5ebab8b343f3393a5f6aa0f6'), ObjectId('5ebab9bc034f665cc26aa0f6'), ObjectId('5ebaba90ee31fa88276aa0f6'), ObjectId('5ebabb683764bc3eec6aa0f6'), ObjectId('5ebabcb754275a966c6aa0f6'), ObjectId('5ebabde785e42d4c986aa0f6'), ObjectId('5ebabf39293dbd093e6aa0f6'), ObjectId('5ebac08cffac78a0406aa0f6'), ObjectId('5ebac1f14aa92171216aa0f6'), ObjectId('5ebac30d8cb26d3f246aa0f6'), ObjectId('5ebac42d0ff4c7cf7a6aa0f6'), ObjectId('5ebac53e1a5cbe715b6aa0f6'), ObjectId('5ebac648b587a572b46aa0f6'), ObjectId('5ebac74e6acf2bb95e6aa0f6'), ObjectId('5ebac8372ee8ac336b6aa0f6'), ObjectId('5ebac8f47dd4237f9f6aa0f6'), ObjectId('5ebac9fe5b6414637b6aa0f6'), ObjectId('5ebacb1f229567f5d96aa0f6'), ObjectId('5ebacc2a81cd4e11bf6aa0f6'), ObjectId('5ebacd20a7b3dae2966aa0f6'), ObjectId('5ebacde1ae613e594b6aa0f6'), ObjectId('5ebacec04c41eee26f6aa0f6'), ObjectId('5ebad134649127b0af6aa0f6'), ObjectId('5ebad244d01ac6e8b06aa0f6'), ObjectId('5ebad345c5294710bd6aa0f6'), ObjectId('5ebad450edde3325cc6aa0f6'), ObjectId('5ebad5b1149ea3c87d6aa0f6'), ObjectId('5ebad67ab7380cbd126aa0f6'), ObjectId('5ebad76c8c21e0df746aa0f6'), ObjectId('5ebad8db94f2b114706aa0f6'), ObjectId('5ebadabfa4af8dfe4f6aa0f6'), ObjectId('5ebadbf9a0a8b573246aa0f6'), ObjectId('5ebadcb52dbeb1a2526aa0f6'), ObjectId('5ebadd7b6f82e334456aa0f6'), ObjectId('5ebaded573c25c747d6aa0f6'), ObjectId('5ebadfc61660f1acf06aa0f6'), ObjectId('5ebae0ebfbd5cc5b866aa0f6'), ObjectId('5ebae1e8f723d84a7e6aa0f6'), ObjectId('5ebae32315c974bd266aa0f6'), ObjectId('5ebae4895d510595eb6aa0f6'), ObjectId('5ebae51b6eb81889b66aa0f6'), ObjectId('5ebae5d0e078c54c4d6aa0f6'), ObjectId('5ebae692e2e081f7a56aa0f6'), ObjectId('5ebae79da17a846ef66aa0f6'), ObjectId('5ebae888c57f427f356aa0f6'), ObjectId('5ebae95136756eae276aa0f6'), ObjectId('5ebaea2741d1765d0f6aa0f6'), ObjectId('5ebaeadb466c8d6d1a6aa0f6'), ObjectId('5ebaebed364e6e646f6aa0f6'), ObjectId('5ebaecc5d4faa1b7116aa0f6'), ObjectId('5ebaedd33c500af46b6aa0f6'), ObjectId('5ebaeefe813b3d94046aa0f6'), ObjectId('5ebaf02f66e6b35cad6aa0f6'), ObjectId('5ebaf130a45a262ec36aa0f6'), ObjectId('5ebaf205269eba74566aa0f6'), ObjectId('5ebaf31c727be0a35f6aa0f6'), ObjectId('5ebaf4650f01d720626aa0f6'), ObjectId('5ebaf577044f6d8da06aa0f6'), ObjectId('5ebaf68a1c80e18bed6aa0f6'), ObjectId('5ebaf795137b20e3926aa0f6'), ObjectId('5ebaf8c4ae83bb5e476aa0f6'), ObjectId('5ebaf9e40d8eb1a5176aa0f6'), ObjectId('5ebafae203af48b0dd6aa0f6'), ObjectId('5ebafbf4c7ee87af176aa0f6'), ObjectId('5ebafd7507eff9111d6aa0f6'), ObjectId('5ebafe299ff39017936aa0f6'), ObjectId('5ebafee615da04b1646aa0f6'), ObjectId('5ebb0046ac06c34fc06aa0f6'), ObjectId('5ebb018598ee79d5536aa0f6'), ObjectId('5ebb038bd7e6a0bebc6aa0f6'), ObjectId('5ebb0457a0f18732ad6aa0f6'), ObjectId('5ebb057e834e6569dd6aa0f6'), ObjectId('5ebb06d867646869aa6aa0f6'), ObjectId('5ebb07c6f15e2d54bc6aa0f6'), ObjectId('5ebb08ce4151d3e1396aa0f6'), ObjectId('5ebb09ff7268acf8b56aa0f6'), ObjectId('5ebb0b08b2b6887d306aa0f6'), ObjectId('5ebb0c329735ae1f7f6aa0f6'), ObjectId('5ebb0d5f9cf7fb77476aa0f6'), ObjectId('5ebb0e492729174f736aa0f6'), ObjectId('5ebb0f4f6431a880276aa0f6'), ObjectId('5ebb102bf1e74e3c996aa0f6'), ObjectId('5ebb10dc2b7ed1c54d6aa0f6'), ObjectId('5ebb11e1da539786e56aa0f6'), ObjectId('5ebb12e5d3303de7976aa0f6'), ObjectId('5ebb13f027f78959816aa0f6'), ObjectId('5ebb14fb488f9a623b6aa0f6'), ObjectId('5ebb157b7b6f9f0ab06aa0f6'), ObjectId('5ebb16bcb3d0e568746aa0f6'), ObjectId('5ebb17d29f6f703ae16aa0f6'), ObjectId('5ebb1973869d3884ce6aa0f6'), ObjectId('5ebb1b2592796da28e6aa0f6'), ObjectId('5ebb1bad90ce0c25196aa0f6'), ObjectId('5ebb20a9dce43be37a6aa0f6'), ObjectId('5ebb21a830f9e211516aa0f6'), ObjectId('5ebb2304fb4ab518cb6aa0f6'), ObjectId('5ebb23d8615a7285726aa0f6'), ObjectId('5ebb246cb8f739279f6aa0f6'), ObjectId('5ebb2565bda0c8ad976aa0f6'), ObjectId('5ebb26a63768ab5fec6aa0f6'), ObjectId('5ebb27dc1e963b5e266aa0f6'), ObjectId('5ebb289996a0cbb8336aa0f6'), ObjectId('5ebb29102dcad31d896aa0f6'), ObjectId('5ebb2a101861d9bfd56aa0f6'), ObjectId('5ebb2b5759358f42b86aa0f6'), ObjectId('5ebb2bf6eef7c615c56aa0f6'), ObjectId('5ebb771c12d8507c296aa0f6'), ObjectId('5ebb7804dc3f93d04b6aa0f6'), ObjectId('5ebb78ed22da81f4096aa0f6'), ObjectId('5ebb79ae471ee598196aa0f6'), ObjectId('5ebb7ab29063aea3e96aa0f6'), ObjectId('5ebb7b9d643c42e52e6aa0f6'), ObjectId('5ebb7c96fb954f50b26aa0f6'), ObjectId('5ebb806d62aa3f1b736aa0f6'), ObjectId('5ebb81954f7aafaea36aa0f6'), ObjectId('5ebb8296a8ed6d09326aa0f6'), ObjectId('5ebb8429e7c427718e6aa0f6'), ObjectId('5ebb8569a436a562d76aa0f6'), ObjectId('5ebb863985f92bf7846aa0f6'), ObjectId('5ebb882f4f508a202c6aa0f6'), ObjectId('5ebb890e08de38906a6aa0f6'), ObjectId('5ebb8a5eac435a66bc6aa0f6'), ObjectId('5ebb8b8a247adf3bac6aa0f6'), ObjectId('5ebb8cdecc408edf436aa0f6'), ObjectId('5ebb8e4c80f02c418e6aa0f6'), ObjectId('5ebb8fea3499a27a476aa0f6'), ObjectId('5ebb914e219529bcd26aa0f6'), ObjectId('5ebb92cb76ec45be916aa0f6'), ObjectId('5ebb94372ad5f4459e6aa0f6'), ObjectId('5ebb954eb4b1733ba66aa0f6'), ObjectId('5ebb96b7b8ea5eddc86aa0f6'), ObjectId('5ebb981f578345eba46aa0f6'), ObjectId('5ebb98f9bb40e262a96aa0f6'), ObjectId('5ebb99e728578c91d56aa0f6'), ObjectId('5ebb9b3aa999402ad36aa0f6'), ObjectId('5ebb9c44c1b42cbbc56aa0f6'), ObjectId('5ebb9cbe6ea41c22346aa0f6'), ObjectId('5ebb9e08b5462147036aa0f6'), ObjectId('5ebb9fbe0739dc31176aa0f6'), ObjectId('5ebba11575f19b90476aa0f6'), ObjectId('5ebba293eb3408469f6aa0f6'), ObjectId('5ebba3e1b9a190811b6aa0f6'), ObjectId('5ebba5f7bc38d10fb76aa0f6'), ObjectId('5ebba6d482bda639156aa0f6'), ObjectId('5ebba7a353afb167066aa0f6'), ObjectId('5ebba856281233e3ec6aa0f6'), ObjectId('5ebba91e94db78e4eb6aa0f6'), ObjectId('5ebba9f416df4600a36aa0f6'), ObjectId('5ebbaab4446067c7656aa0f6'), ObjectId('5ebbab6dad852c37026aa0f6'), ObjectId('5ebbacc55e984c90896aa0f6'), ObjectId('5ebbae609ac80be49a6aa0f6'), ObjectId('5ebbaf5923e8de12726aa0f6'), ObjectId('5ebbb03674dee939a46aa0f6'), ObjectId('5ebbb0a28efd4d38d46aa0f6'), ObjectId('5ebbb14e4e694aa47d6aa0f6'), ObjectId('5ebbb1b85dfbaa4d786aa0f6'), ObjectId('5ebbb2c0cb9975fbf36aa0f6'), ObjectId('5ebbb46aa481553d446aa0f6'), ObjectId('5ebbb580d1393f6ff36aa0f6'), ObjectId('5ebbb6751b21c7ed6a6aa0f6'), ObjectId('5ebbb762f199d6ef886aa0f6'), ObjectId('5ebbb7d677a48dcddd6aa0f6'), ObjectId('5ebbb8d35d3880d4b16aa0f6'), ObjectId('5ebbb9935098991b3e6aa0f6'), ObjectId('5ebbba53ac65270bd06aa0f6'), ObjectId('5ebbbaec434b6f155b6aa0f6'), ObjectId('5ebbbbf72f5413756d6aa0f6'), ObjectId('5ebbbc8d7199b845bf6aa0f6'), ObjectId('5ebbbd1f442930d4936aa0f6'), ObjectId('5ebbbde28e5144df826aa0f6'), ObjectId('5ebbbf1cd3a944233a6aa0f6'), ObjectId('5ebbbff61549076a1b6aa0f6'), ObjectId('5ebbc0696cbe306f756aa0f6'), ObjectId('5ebbc14c1e9f60b2826aa0f6'), ObjectId('5ebbc219ae5d8bcd816aa0f6'), ObjectId('5ebbc3f44931fd15ad6aa0f6'), ObjectId('5ebbc4dd2563b3460d6aa0f6'), ObjectId('5ebbca20827f1af2c397178d'), ObjectId('5ebbcad24bdc100b9297178d'), ObjectId('5ebbcbd8e6ec72146a97178d'), ObjectId('5ebbcc99b03ab9032f97178d'), ObjectId('5ebbcd1b4e715b717b97178d'), ObjectId('5ebbce48438ab3f89797178d'), ObjectId('5ebbcf0ba231769fda97178d'), ObjectId('5ebbd01600a1c5e0fc97178d'), ObjectId('5ebbd0afae75f0608b97178d'), ObjectId('5ebbd13d126ffba29897178d'), ObjectId('5ebbd2161b5e9d954997178d'), ObjectId('5ebbd27d8816705d3e97178d'), ObjectId('5ebbd3601115d30fca97178d'), ObjectId('5ebbd42b4ee5dcfa8d97178d'), ObjectId('5ebbd5f5f1e510ea0e97178d'), ObjectId('5ebbd6d689d268831997178d'), ObjectId('5ebbd7af5ca946e06b97178d'), ObjectId('5ebbd8a31840d1cde197178d'), ObjectId('5ebbd9b45a74e14cdf97178d'), ObjectId('5ebbda9ee9ce37b87497178d'), ObjectId('5ebbdbdc70e15a08c397178d'), ObjectId('5ebbdd4d7655a83e6297178d'), ObjectId('5ebbde40e7d479de4a97178d'), ObjectId('5ebbdf1e4c04cacbb697178d'), ObjectId('5ebbdfe4e5ea81fcd297178d'), ObjectId('5ebbe0b386f2ef4c7b97178d'), ObjectId('5ebbe18dac66bed3de97178d'), ObjectId('5ebbe2b2b0a795f33f97178d'), ObjectId('5ebbe3b6102784fdea97178d'), ObjectId('5ebbe4af340990d62f97178d'), ObjectId('5ebbe5255d76242aef97178d'), ObjectId('5ebbe638671e802e6397178d'), ObjectId('5ebbe7300dbe31b16997178d'), ObjectId('5ebbe7cc430903f91597178d'), ObjectId('5ebbe87a8a059c7c6297178d'), ObjectId('5ebbeaf57cdedca11397178d'), ObjectId('5ebbeb9a4ce622fc5f97178d'), ObjectId('5ebbed663646af3c7b97178d'), ObjectId('5ebbee6a5f009009c597178d'), ObjectId('5ebbf1c39cc1200a2797178d'), ObjectId('5ebbf299c5a7f124b697178d'), ObjectId('5ebbf3360421d9c77797178d'), ObjectId('5ebbf3ed1166a781cc97178d'), ObjectId('5ebbf5959491ae92e997178d'), ObjectId('5ebbf642304c4f80ab97178d'), ObjectId('5ebbf73c8aae5c54cd97178d'), ObjectId('5ebbf84b53ba3184e697178d'), ObjectId('5ebbfac2f4308c2cc497178d'), ObjectId('5ebbfbdf6c99d1297497178d'), ObjectId('5ebbfd0a6291766e8c97178d'), ObjectId('5ebbfe2692b1ee138897178d'), ObjectId('5ebbfecd381a18083097178d'), ObjectId('5ebbffe954b500b09497178d'), ObjectId('5ebc00c75da3de695b97178d'), ObjectId('5ebc0276088a2cf87797178d'), ObjectId('5ebc034d1034c24aad97178d'), ObjectId('5ebc048e11ccbe0da897178d'), ObjectId('5ebc075694bc2c707997178d'), ObjectId('5ebc0875b11342f88097178d'), ObjectId('5ebc09a74efa0725f497178d'), ObjectId('5ebc0acbe84a4f5ebc97178d'), ObjectId('5ebc0bd6237a0574d297178d'), ObjectId('5ebc0d3c73e648b83597178d'), ObjectId('5ebc0dbe0dabb3379b97178d'), ObjectId('5ebc0ee1d9892b0c1b97178d'), ObjectId('5ebc13d75c86d945b197178d'), ObjectId('5ebc150e82d13b7b3697178d'), ObjectId('5ebc16489fcd033f6297178d'), ObjectId('5ebc17c2b4123e4f7197178d'), ObjectId('5ebc189513f4a8262197178d'), ObjectId('5ebc19aafc23d292fa97178d'), ObjectId('5ebc1adac6d203564e97178d'), ObjectId('5ebc1c5f3a0803f22f97178d'), ObjectId('5ebc1e001783515cd097178d'), ObjectId('5ebc1efebff60eafcc97178d'), ObjectId('5ebc1fa10215e6d08097178d'), ObjectId('5ebc2273674baef33497178d'), ObjectId('5ebc239dcf12c8ef1397178d'), ObjectId('5ebc24c73d53d2699c97178d'), ObjectId('5ebc2606a78eecfe5397178d'), ObjectId('5ebc27e9bd0f15a4d697178d'), ObjectId('5ebc28e2414c3fac1397178d'), ObjectId('5ebc2a0004edb50ae697178d'), ObjectId('5ebc2b0bf9360bbe0097178d'), ObjectId('5ebc2bd7c815a5eb3197178d'), ObjectId('5ebc2c7a12c0462f6597178d'), ObjectId('5ebc2e1cba7a46c38597178d'), ObjectId('5ebc2ee30d89056a5397178d'), ObjectId('5ebc3034223430f85897178d'), ObjectId('5ebc3169d17d5cf8b097178d'), ObjectId('5ebc32b53ef4cdcab097178d'), ObjectId('5ebc344e630bf85da197178d'), ObjectId('5ebc35b8f60ec679e997178d'), ObjectId('5ebc3732359c41b6fb97178d'), ObjectId('5ebc37fdd57cee6b8097178d'), ObjectId('5ebc3937d67ddeedc697178d'), ObjectId('5ebc3a2d3d43846c8097178d'), ObjectId('5ebc3b8c8f905cc1e997178d'), ObjectId('5ebc3d0f0f1bbea78f97178d'), ObjectId('5ebc3d972739abfa2597178d'), ObjectId('5ebc3e33f8232116ed97178d'), ObjectId('5ebc3f2f65d503e38b97178d'), ObjectId('5ebc3fe0843419ca2497178d'), ObjectId('5ebc44847ce40c9ba7bb9565'), ObjectId('5ebc452ac7057c1a4cbb9565'), ObjectId('5ebc475c409fdd7855bb9565'), ObjectId('5ebc4c4bff166bccf3bb9565'), ObjectId('5ebc4dc1a821835a79bb9565'), ObjectId('5ebc4edd839d7e0760bb9565'), ObjectId('5ebc5065dc5d111808bb9565'), ObjectId('5ebc51615809efe175bb9565'), ObjectId('5ebc524ab08e89b0dbbb9565'), ObjectId('5ebc53a9503b1f44d4bb9565'), ObjectId('5ebc54e10c8dd65b2ebb9565'), ObjectId('5ebc55d8b8becb694ebb9565'), ObjectId('5ebc56ea2e7d8c6aeebb9565'), ObjectId('5ebc5998cf082e6085bb9565'), ObjectId('5ebc5b1f9c4cc72ad1bb9565'), ObjectId('5ebc5bf2b3cbaa2082bb9565'), ObjectId('5ebc5d4be04b819ebbbb9565'), ObjectId('5ebc5e6ac44c18198cbb9565'), ObjectId('5ebc5f97704055e80fbb9565'), ObjectId('5ebc609f7eac357441bb9565'), ObjectId('5ebc61e72f2c7dada9bb9565'), ObjectId('5ebc6297ec72b05079bb9565'), ObjectId('5ebc63bfd0307282bfbb9565'), ObjectId('5ebc64ebef1ae0f93cbb9565'), ObjectId('5ebc662f30a73754bdbb9565'), ObjectId('5ebc670e0989242104bb9565'), ObjectId('5ebc67e2c23fb5f50fbb9565'), ObjectId('5ebc689e354f01cef5bb9565'), ObjectId('5ebc69f507bbf21102bb9565'), ObjectId('5ebc6b4ce3edb257d2bb9565'), ObjectId('5ebc6d29ef740596e3bb9565'), ObjectId('5ebc6e966b32dc548abb9565'), ObjectId('5ebc6fe10cc45c110abb9565'), ObjectId('5ebc70d663d25e7626bb9565'), ObjectId('5ebc71db7a7539f778bb9565'), ObjectId('5ebc73a5647bebbebebb9565'), ObjectId('5ebc754411d8be18d7bb9565'), ObjectId('5ebc766e133af6bd40bb9565'), ObjectId('5ebc7775f2d5414b72bb9565'), ObjectId('5ebc78525c1c202b83bb9565'), ObjectId('5ebc794dc19a9f9959bb9565'), ObjectId('5ebc7a0de27e58b722bb9565'), ObjectId('5ebc7aff7e8c51fa5cbb9565'), ObjectId('5ebc7c753b4b632571bb9565'), ObjectId('5ebc7dd360f39467b0bb9565'), ObjectId('5ebc7f0c9596b2c3c3bb9565'), ObjectId('5ebc802cdae450fef8bb9565'), ObjectId('5ebc81328a39a23545bb9565'), ObjectId('5ebc82311e0fecd49dbb9565'), ObjectId('5ebc8330d68e5922acbb9565'), ObjectId('5ebc845c0d4da08c6cbb9565'), ObjectId('5ebc856de0d100ac75bb9565'), ObjectId('5ebc8681384fba1159bb9565'), ObjectId('5ebc871ed930e86275bb9565'), ObjectId('5ebc885ca272f357d6bb9565'), ObjectId('5ebc895185be38e47dbb9565'), ObjectId('5ebc8a1782d758f81ebb9565'), ObjectId('5ebc8afd1a8aacb685bb9565'), ObjectId('5ebc8bcf0674f6a5cfbb9565'), ObjectId('5ebc8cb6cd39f22394bb9565'), ObjectId('5ebc8e617c59b90a2fbb9565'), ObjectId('5ebc8fbeea52288a8bbb9565'), ObjectId('5ebc91d972a50ff18ebb9565'), ObjectId('5ebc9256c5958bd302bb9565'), ObjectId('5ebc9362ebb1fc2b07bb9565'), ObjectId('5ebc94b647c2e77ca3bb9565'), ObjectId('5ebc95ea7cbc6a1403bb9565'), ObjectId('5ebc971bba16733a02bb9565'), ObjectId('5ebc984530037449c9bb9565'), ObjectId('5ebc9949a160c22deebb9565'), ObjectId('5ebc9a1c3e0aa5990cbb9565'), ObjectId('5ebc9b8128578a3d31bb9565'), ObjectId('5ebc9c74ab2ef6351bbb9565'), ObjectId('5ebc9d363989161b11bb9565'), ObjectId('5ebc9e03cafeebb26bbb9565'), ObjectId('5ebc9f2b619a56275fbb9565'), ObjectId('5ebca00d314c2dc72ebb9565'), ObjectId('5ebca14eba194fdeb1bb9565'), ObjectId('5ebca2376f78cb5a2bbb9565'), ObjectId('5ebca33057b4b2b734bb9565'), ObjectId('5ebca4cc099c653561bb9565'), ObjectId('5ebca5591baac0e83dbb9565'), ObjectId('5ebca66e74328e8022bb9565'), ObjectId('5ebca7cbe6c4023d26bb9565'), ObjectId('5ebca8cf6f840edcb3bb9565'), ObjectId('5ebcaaa8d0354e60babb9565'), ObjectId('5ebcabd24a644677ffbb9565'), ObjectId('5ebcacc3f7e2f8ee8bbb9565'), ObjectId('5ebcae4585e6061bd0bb9565'), ObjectId('5ebcaf4e9622183001bb9565'), ObjectId('5ebcb05aa44de503fabb9565'), ObjectId('5ebcb132a2093d13d0bb9565'), ObjectId('5ebcb2cd922e75c876bb9565'), ObjectId('5ebcb3cadc1a1388c7bb9565'), ObjectId('5ebcb523969284d23dbb9565'), ObjectId('5ebcb6ef119620ed97bb9565'), ObjectId('5ebcb7d69224a1b74bbb9565'), ObjectId('5ebcb885a6da1f930cbb9565'), ObjectId('5ebcb9a118d81d1cbbbb9565'), ObjectId('5ebcbb0d3f90784303bb9565'), ObjectId('5ebcbb957c67c9cef5bb9565'), ObjectId('5ebcbc85352785ec12bb9565'), ObjectId('5ebcbe138fff794862bb9565'), ObjectId('5ebcbf2b2af1f062e3bb9565'), ObjectId('5ebcc0475af8654d72bb9565'), ObjectId('5ebcc26b484ede5904bb9565'), ObjectId('5ebcc3221604f7f7d7bb9565'), ObjectId('5ebcc45397acd3f8a2bb9565'), ObjectId('5ebcc58db3643873f0bb9565'), ObjectId('5ebcc68da3ba29bee5bb9565'), ObjectId('5ebcc7e3353f259c9abb9565'), ObjectId('5ebcc8f0f96bd933a5bb9565'), ObjectId('5ebcc9fddc68e0bf3bbb9565'), ObjectId('5ebccb40f70ef18b49bb9565'), ObjectId('5ebccc66d9df03169dbb9565'), ObjectId('5ebccdc25d73fe7a88bb9565'), ObjectId('5ebccec14cf1a77a62bb9565'), ObjectId('5ebccf799a297ffebebb9565'), ObjectId('5ebcd0764dd2fbfc26bb9565'), ObjectId('5ebcd153160254fc9ebb9565'), ObjectId('5ebcd27767809786bbbb9565'), ObjectId('5ebcd34a6098473cd4bb9565'), ObjectId('5ebcd49deab020e028bb9565'), ObjectId('5ebcd58d767c6a2fe0bb9565'), ObjectId('5ebcd64ef2f9eecf34bb9565'), ObjectId('5ebcd7203769d8b4c0bb9565'), ObjectId('5ebcd8315d3c46bf0fbb9565'), ObjectId('5ebcd8f9be1e13b63dbb9565'), ObjectId('5ebcda7eba71eaca87bb9565'), ObjectId('5ebcdb34435b150550bb9565'), ObjectId('5ebcdbeae8aab054c3bb9565'), ObjectId('5ebcdd7c16e302af0ebb9565'), ObjectId('5ebcde7a6ebb152546bb9565'), ObjectId('5ebcdf95359df0d164bb9565'), ObjectId('5ebce0c51dd1903478bb9565'), ObjectId('5ebce1aeadd4c0a3e0bb9565'), ObjectId('5ebce3325e4212bb48bb9565'), ObjectId('5ebce442ac3373eba6bb9565'), ObjectId('5ebce6892067022a62bb9565'), ObjectId('5ebce7d93cbe748a83bb9565'), ObjectId('5ebce92bc83f027dd9bb9565'), ObjectId('5ebcea5cff05bac2f1bb9565'), ObjectId('5ebceb0d15a9e9eaeebb9565'), ObjectId('5ebcec1647057d3c45bb9565'), ObjectId('5ebcec9c106f4c3a1abb9565'), ObjectId('5ebced87f299814126bb9565'), ObjectId('5ebcee74bf85ed3c28bb9565'), ObjectId('5ebcef579014fddb7dbb9565'), ObjectId('5ebceffc85e7506011bb9565'), ObjectId('5ebcf08b9522522d60bb9565'), ObjectId('5ebcf108f63f96f109bb9565'), ObjectId('5ebcf1fbc6b289d0edbb9565'), ObjectId('5ebcf2cfd0b71e96f4bb9565'), ObjectId('5ebcf4890f1e5ba0b0bb9565'), ObjectId('5ebcf577f441e92192bb9565'), ObjectId('5ebcf6440dff2a61acbb9565'), ObjectId('5ebcf6bd7316da96c6bb9565'), ObjectId('5ebcf76e2566f6bb05bb9565'), ObjectId('5ebcf7ec5640f2f328bb9565'), ObjectId('5ebcf89836daf4509fbb9565'), ObjectId('5ebcf93215c77e8b87bb9565'), ObjectId('5ebcf9dd1301cad34fbb9565'), ObjectId('5ebcfb8cbc87dec79cbb9565'), ObjectId('5ebcfc44eb11b2e47dbb9565'), ObjectId('5ebcfd2cd7ea48b3e7bb9565'), ObjectId('5ebcfdbf9f11780689bb9565'), ObjectId('5ebcfe8e2952286fefbb9565'), ObjectId('5ebcff1f2a93fc931ebb9565'), ObjectId('5ebd0001b3509c960abb9565'), ObjectId('5ebd00dab8cc7ea5dabb9565'), ObjectId('5ebd015476f2c8cf87bb9565'), ObjectId('5ebd020f569f790404bb9565'), ObjectId('5ebd02c50f15cbd93ebb9565'), ObjectId('5ebd03e6f2c2c8038ebb9565'), ObjectId('5ebd053641df3cea32bb9565'), ObjectId('5ebd06cf8892fa02bdbb9565'), ObjectId('5ebd07eba463f4d183bb9565'), ObjectId('5ebd09a4d64c61ea04bb9565'), ObjectId('5ebd0bae98ffab8e7bbb9565'), ObjectId('5ebd0ce9c8aa38951ebb9565'), ObjectId('5ebd0e220b718b8620bb9565'), ObjectId('5ebd0ee0880136b7afbb9565'), ObjectId('5ebd10661c8d8ad3c3bb9565'), ObjectId('5ebd12255f594b4b6bbb9565'), ObjectId('5ebd1363f25e6f6546bb9565'), ObjectId('5ebd147c1119c14953bb9565'), ObjectId('5ebd1608d47c1e2418bb9565'), ObjectId('5ebd17086956b802f8bb9565'), ObjectId('5ebd17e68b7f616830bb9565'), ObjectId('5ebd18eaa5627dc978bb9565'), ObjectId('5ebd1a2393c45cb40ebb9565'), ObjectId('5ebd1bd524285f988ebb9565'), ObjectId('5ebd1d70fe9a4e44f4bb9565'), ObjectId('5ebd1f24a731947d23bb9565'), ObjectId('5ebd1fb4f902dca8cabb9565'), ObjectId('5ebd2277174a04dafebb9565'), ObjectId('5ebd2355666a191d89bb9565'), ObjectId('5ebd23fc201cd3e6bfbb9565'), ObjectId('5ebd24a06e160e43c7bb9565'), ObjectId('5ebd255d9fd249f446bb9565'), ObjectId('5ebd25dab8ddbb12a7bb9565'), ObjectId('5ebd26b2031e847836bb9565'), ObjectId('5ebd275825abac33cbbb9565'), ObjectId('5ebd27e02408aec98abb9565'), ObjectId('5ebd2901bb17922d7ebb9565'), ObjectId('5ebd29aa90e09a86f5bb9565'), ObjectId('5ebd2a999e04ea59e8bb9565'), ObjectId('5ebd2bc121c02d589bbb9565'), ObjectId('5ebd2ce2b594bfb1f2bb9565'), ObjectId('5ebd2da465c3917732bb9565'), ObjectId('5ebd2e4d3dedb20ec3bb9565'), ObjectId('5ebd2f1fd143dae4b2bb9565'), ObjectId('5ebd2f90141e8ce48dbb9565'), ObjectId('5ebd303965742b506dbb9565'), ObjectId('5ebd30ffb412a41516bb9565'), ObjectId('5ebd321634c77f5798bb9565'), ObjectId('5ebd32b7fd1b187544bb9565'), ObjectId('5ebd3a22f321cdd207d1b7ab'), ObjectId('5ebd3d8fdda69510b998bd17'), ObjectId('5ebd796a1bfded191c23510e'), ObjectId('5ebd7a3eda443a028023510e'), ObjectId('5ebd7ac8160e002bbf23510e'), ObjectId('5ebd7b3bd1fd26d5cc23510e'), ObjectId('5ebd7c7c3c6bb6723023510e'), ObjectId('5ebd7dad99369e7c8a23510e'), ObjectId('5ebd7efb7c379d2d3223510e'), ObjectId('5ebd80bea3836a0c0a23510e'), ObjectId('5ebd820d22437f5c2e23510e'), ObjectId('5ebd82952597752f6123510e'), ObjectId('5ebd83a67b2f65704b23510e'), ObjectId('5ebd846612cc2d9c4723510e'), ObjectId('5ebd8552b5ed2ef2ca23510e'), ObjectId('5ebd869733f40229cf23510e'), ObjectId('5ebd880505e303dbb623510e'), ObjectId('5ebd891ef3f083120923510e'), ObjectId('5ebd89935397bc7a1223510e'), ObjectId('5ebd89f973222ecec623510e'), ObjectId('5ebd8b2c57805a023423510e'), ObjectId('5ebd8bb7c7fcca593123510e'), ObjectId('5ebd8d2b33490849bf23510e'), ObjectId('5ebd8fbf8661ff060b23510e'), ObjectId('5ebd90482da109482423510e'), ObjectId('5ebd9115db4fc596b623510e'), ObjectId('5ebd91f955bf1e293e23510e'), ObjectId('5ebd933586a108cfb023510e'), ObjectId('5ebd94593ca68ec88723510e'), ObjectId('5ebd95693164a0561223510e'), ObjectId('5ebd967ef5ece6be7e23510e'), ObjectId('5ebd97ec7e075bdf1b23510e'), ObjectId('5ebd99ac214dbaec9623510e'), ObjectId('5ebd9ae62149a04ac623510e'), ObjectId('5ebd9bf1cf2d75f30f23510e'), ObjectId('5ebd9ce9eaadcab91823510e'), ObjectId('5ebd9e6071b196bdfc23510e'), ObjectId('5ebda025c44c9aff7223510e'), ObjectId('5ebda1a4a16b09d54a23510e'), ObjectId('5ebda2ba083600027023510e'), ObjectId('5ebda4d0e699595c9623510e'), ObjectId('5ebda614f739ee878c23510e'), ObjectId('5ebda6f5f677c6517323510e'), ObjectId('5ebda7e7c62ddf274523510e'), ObjectId('5ebda85963ec391d0423510e'), ObjectId('5ebda96cb1d8f4b5d123510e'), ObjectId('5ebdaa5980d75dbb8a23510e'), ObjectId('5ebdab1fa90496c00923510e'), ObjectId('5ebdac1e698107bc9823510e'), ObjectId('5ebdace3e64012f6a923510e'), ObjectId('5ebdad8cecd540c25723510e'), ObjectId('5ebdae9c34c98ecb7623510e'), ObjectId('5ebdaf8b9bc87e4ae123510e'), ObjectId('5ebdb0f46a8d6bcad323510e'), ObjectId('5ebdb1f814ffb1de1623510e'), ObjectId('5ebdb373d8a95e350723510e'), ObjectId('5ebdb47f71a9142a3023510e'), ObjectId('5ebdb569c9068fce6f23510e'), ObjectId('5ebdb99bc81520990b23510e'), ObjectId('5ebdbad429ebb8695723510e'), ObjectId('5ebdbc0b78d6e31acb23510e'), ObjectId('5ebdbd15c8a723347223510e'), ObjectId('5ebdbdd165c9f2bd2f23510e'), ObjectId('5ebdbeb84dfbdf1a7a23510e'), ObjectId('5ebdbf95ce002b817323510e'), ObjectId('5ebdc0fd5a8c685cac23510e'), ObjectId('5ebdc20a048a5606a723510e'), ObjectId('5ebdc34558c210e6ba23510e'), ObjectId('5ebdc42199677f61df23510e'), ObjectId('5ebdc5017211f4b06623510e'), ObjectId('5ebdc6236c117f8e5023510e'), ObjectId('5ebdc74811460dba3723510e'), ObjectId('5ebdc80f0c314bab7323510e'), ObjectId('5ebdc958c8f07adf0623510e'), ObjectId('5ebdcaad9cf085d4ca23510e'), ObjectId('5ebdcaffdc37ce0eb523510e'), ObjectId('5ebdcc63b52e86ccbb23510e'), ObjectId('5ebdcd27f635aea54523510e'), ObjectId('5ebdcea895901e01ea23510e'), ObjectId('5ebdd02873d18252e223510e'), ObjectId('5ebdd18870ec30b67223510e'), ObjectId('5ebdd26e1c338de66323510e'), ObjectId('5ebdd38c88cd8b3fd723510e'), ObjectId('5ebdd43fe809becffc23510e'), ObjectId('5ebdd55626d98da9da23510e'), ObjectId('5ebdd670c814f7619d23510e'), ObjectId('5ebdd74720861643ea23510e'), ObjectId('5ebdd85bbca17ead8e23510e'), ObjectId('5ebdd9a44e1876956023510e'), ObjectId('5ebddac50666fc8fdf23510e'), ObjectId('5ebddc8722342f2d5723510e'), ObjectId('5ebdddc7b8981578ff23510e'), ObjectId('5ebddf0e9c07e3009a23510e'), ObjectId('5ebde014b77485010323510e'), ObjectId('5ebde118ab63535ed623510e'), ObjectId('5ebde222c41ab21a8f23510e'), ObjectId('5ebde2be526174d1d423510e'), ObjectId('5ebde6341572b9f0a223510e'), ObjectId('5ebde728e9d9461b7f23510e'), ObjectId('5ebde81b6a78f4b2ac23510e'), ObjectId('5ebdea079e80f3015523510e'), ObjectId('5ebdeb3a8867ec6b5023510e'), ObjectId('5ebdec8b3f2db62a9a23510e'), ObjectId('5ebded47254503787123510e'), ObjectId('5ebdedff4bac6e548023510e'), ObjectId('5ebdeee5ca347a3a4023510e'), ObjectId('5ebdefedb6640fc26023510e'), ObjectId('5ebdf12c980c486e1923510e'), ObjectId('5ebdf1ee1c933824fa23510e'), ObjectId('5ebdf2f345de40632a23510e'), ObjectId('5ebdf3fe8014807b3023510e'), ObjectId('5ebdf62db6b0896a2823510e'), ObjectId('5ebdf723711cbc68f823510e'), ObjectId('5ebdf7e7a11831c6d923510e'), ObjectId('5ebdf969e41f17a4b223510e'), ObjectId('5ebdfa74cb8e7b4c4e23510e'), ObjectId('5ebdfaf5f7d4a26ae323510e'), ObjectId('5ebdfbd6a8c986176023510e'), ObjectId('5ebdfc9f10ddc6734e23510e'), ObjectId('5ebdfd3dbec363e31b23510e'), ObjectId('5ebdfeddbbcc93a8d223510e'), ObjectId('5ebdfff4de647a467f23510e'), ObjectId('5ebe00ca119d06ca3223510e'), ObjectId('5ebe01d5a1d5b4617023510e'), ObjectId('5ebe02c44897de14a923510e'), ObjectId('5ebe03c6baab1b599123510e'), ObjectId('5ebe04feb352a6756223510e'), ObjectId('5ebe06455b6ac2ba0323510e'), ObjectId('5ebe07d6812edc601b23510e'), ObjectId('5ebe08c8918a95661523510e'), ObjectId('5ebe0a0d110384add423510e'), ObjectId('5ebe0bb08df9dfa24723510e'), ObjectId('5ebe0c575ca295797423510e'), ObjectId('5ebe0cd9a0d22e0d5723510e'), ObjectId('5ebe0da5663c0d400d23510e'), ObjectId('5ebe0e4e173a912a8923510e'), ObjectId('5ebe0f126e2565a3c323510e'), ObjectId('5ebe102a6773d0b2e023510e'), ObjectId('5ebe114e7586bde45e23510e'), ObjectId('5ebe1252b1affb0b0223510e'), ObjectId('5ebe12faf9da04afc323510e'), ObjectId('5ebe13b5de4d6a45b423510e'), ObjectId('5ebe14b3c9699ceeaa23510e'), ObjectId('5ebe17207e47e5354a23510e'), ObjectId('5ebe17b768839a80c223510e'), ObjectId('5ebe184e197a75e64f23510e'), ObjectId('5ebe18e7baba7a348c23510e'), ObjectId('5ebe1a2f6a016e79f223510e'), ObjectId('5ebe1adfc02a37a04d23510e'), ObjectId('5ebe1b997ef9ba265c23510e'), ObjectId('5ebe1c36bc048b033d23510e'), ObjectId('5ebe1ccc9f4b32070b23510e'), ObjectId('5ebe1d5f229dc61a2c23510e'), ObjectId('5ebe1deb74e3e08f2f23510e'), ObjectId('5ebe1ec6ef211ca78a23510e'), ObjectId('5ebe1f7622f89fa85c23510e'), ObjectId('5ebe2082cb26ce3d9623510e'), ObjectId('5ebe2160729709f17023510e'), ObjectId('5ebe21f3ef0b7214b323510e'), ObjectId('5ebe22e7c0ed77f6d523510e'), ObjectId('5ebe23b6365f130bb623510e'), ObjectId('5ebe246b13657b035323510e'), ObjectId('5ebe255e4c5abad2c023510e'), ObjectId('5ebe25c747a6ac779b23510e'), ObjectId('5ebe2684bd1bf8333523510e'), ObjectId('5ebe27ce38d7be0c9023510e'), ObjectId('5ebe28e9361dd7cb3c23510e'), ObjectId('5ebe29a35b269bf26b23510e'), ObjectId('5ebe2a9000a6c0640423510e'), ObjectId('5ebe2b82008f27cd2923510e'), ObjectId('5ebe2c580e4ce0536723510e'), ObjectId('5ebe2d811f6f235f9423510e'), ObjectId('5ebe2f9594b8ddf1bf23510e'), ObjectId('5ebe3110c8eb4ce0d623510e'), ObjectId('5ebe32490e54e54ac323510e'), ObjectId('5ebe33cfe6adf5656423510e'), ObjectId('5ebe3587f54656eb7923510e'), ObjectId('5ebe371fee35df244c23510e'), ObjectId('5ebe380ed58d76612d23510e'), ObjectId('5ebe38fc932283cfde23510e'), ObjectId('5ebe39c4604716934c23510e'), ObjectId('5ebe3a796fce07fc0323510e'), ObjectId('5ebe3b841215466f7a23510e'), ObjectId('5ebe3c08a4fcb859d923510e'), ObjectId('5ebe3d2a685d3bbcd923510e'), ObjectId('5ebe3e3bdcc73fc7c123510e'), ObjectId('5ebe3ef42128e09edb23510e'), ObjectId('5ebe4189c511affa9a23510e'), ObjectId('5ebe4326ecd569c2ec23510e'), ObjectId('5ebe444e343cd5178023510e'), ObjectId('5ebe44edc3e237374723510e'), ObjectId('5ebe45b8c176a0ce0423510e'), ObjectId('5ebe471453b9ecf8ef23510e'), ObjectId('5ebe47fdc240012fb223510e'), ObjectId('5ebe489a345c2b4da723510e'), ObjectId('5ebe491ab0e14f5de823510e'), ObjectId('5ebe4a32c97f50467923510e'), ObjectId('5ebe4b4cd5f021d40a23510e'), ObjectId('5ebe4c1bd474c4e5b323510e'), ObjectId('5ebe4ca3cfd906efa323510e'), ObjectId('5ebe4d4b15a39a0c2e23510e'), ObjectId('5ebe4dd709926c96a223510e'), ObjectId('5ebe4e433674355bc023510e'), ObjectId('5ebe4eb5ca87309d1c23510e'), ObjectId('5ebe4fa68a8a10b98623510e'), ObjectId('5ebe50421cf82abcf923510e'), ObjectId('5ebe50bdc35eceb02023510e'), ObjectId('5ebe52e548f0ecc70f23510e'), ObjectId('5ebe5379cff7492f5623510e'), ObjectId('5ebe546483a93c8ddb23510e'), ObjectId('5ebe56fa3440fa97d523510e'), ObjectId('5ebe57ad48910a9ff723510e'), ObjectId('5ebe58ca83dd2353f023510e'), ObjectId('5ebe5a49e5dcabd06c23510e'), ObjectId('5ebe5ba075c5904fbc23510e'), ObjectId('5ebe5cbdc63f4a286123510e'), ObjectId('5ebe5d5a48b0eab19723510e'), ObjectId('5ebe5dfbb66c40d9a423510e'), ObjectId('5ebe5ebede558cbbb223510e'), ObjectId('5ebe5f3f177d38f8c523510e'), ObjectId('5ebe6024c21f8d600f23510e'), ObjectId('5ebe616a764275331523510e'), ObjectId('5ebe622b85dee1476423510e'), ObjectId('5ebe635d7a6f29121023510e'), ObjectId('5ebe647f5d46a1366b23510e'), ObjectId('5ebe65da6a9d6de27923510e'), ObjectId('5ebe678912502325db23510e'), ObjectId('5ebe69389a62211d6d23510e'), ObjectId('5ebe6adc56caef814023510e'), ObjectId('5ebe6cfe66ab22f9a923510e'), ObjectId('5ebe6e53860742577823510e'), ObjectId('5ebe6f0d98eff0aa6323510e'), ObjectId('5ebe70d1a7c94ecd7b23510e'), ObjectId('5ebe71d36c3fdeb61d23510e'), ObjectId('5ebe730e5d65d8d2ae23510e'), ObjectId('5ebe73928e1194814323510e'), ObjectId('5ec20a8df687ff620dd08ffd'), ObjectId('5ec20b2e7ee23711b9d08ffd'), ObjectId('5ec20bc95eb68a915cd08ffd'), ObjectId('5ec20cc7732097ba8ad08ffd'), ObjectId('5ec20dfbc8d363fe73d08ffd'), ObjectId('5ec20ede27fadfdd47d08ffd'), ObjectId('5ec20fc991aaa72304d08ffd'), ObjectId('5ec2104f497f895a9cd08ffd'), ObjectId('5ec211049bab3d37d2d08ffd'), ObjectId('5ec211e48505fe901dd08ffd'), ObjectId('5ec2136d9ac1ff38b0d08ffd'), ObjectId('5ec214765b9b6920ecd08ffd'), ObjectId('5ec215543a859fdf88d08ffd'), ObjectId('5ec21619438f8a1e8bd08ffd'), ObjectId('5ec216f0ca568a4941d08ffd'), ObjectId('5ec21799ae9dc7d64ed08ffd'), ObjectId('5ec21818ac63a29512d08ffd'), ObjectId('5ec21919b2f7815b96d08ffd'), ObjectId('5ec21a2ae157ec6308d08ffd'), ObjectId('5ec21aa965ad51eb4dd08ffd'), ObjectId('5ec21c219357b0c1eed08ffd'), ObjectId('5ec21d0c2fcab31316d08ffd'), ObjectId('5ec21dc7358961c823d08ffd'), ObjectId('5ec21e82438ec56770d08ffd'), ObjectId('5ec21f6a2befc723f3d08ffd'), ObjectId('5ec2203a335d298239d08ffd'), ObjectId('5ec220f8cf464d1769d08ffd'), ObjectId('5ec221a17d0d245a3cd08ffd'), ObjectId('5ec2224098e5201baed08ffd'), ObjectId('5ec2241725ade07b26d08ffd'), ObjectId('5ec22510147a0fc9b7d08ffd'), ObjectId('5ec225cdd083609887d08ffd'), ObjectId('5ec2269cac51bcdc4dd08ffd'), ObjectId('5ec22783a3b00a6f39d08ffd'), ObjectId('5ec2282e7de77a69b7d08ffd'), ObjectId('5ec229880457130f0ad08ffd'), ObjectId('5ec22a286aa7b2f87fd08ffd'), ObjectId('5ec22ba1294f6f446bd08ffd'), ObjectId('5ec22c3b7002e2b8a1d08ffd'), ObjectId('5ec22d02b7c830d85cd08ffd'), ObjectId('5ec22dbf4aca739bacd08ffd'), ObjectId('5ec22e41b6e6d4624bd08ffd'), ObjectId('5ec22efb08af4c47fdd08ffd'), ObjectId('5ec22fcb44f7b4dfb1d08ffd'), ObjectId('5ec230518227f7bceed08ffd'), ObjectId('5ec23104b2b6836637d08ffd'), ObjectId('5ec231c0bfac4de028d08ffd'), ObjectId('5ec232715b6a072779d08ffd'), ObjectId('5ec23348f5f268a3c0d08ffd'), ObjectId('5ec23455d964f932bdd08ffd'), ObjectId('5ec23538b951a56b4fd08ffd'), ObjectId('5ec235eab321c49b2bd08ffd'), ObjectId('5ec23710599a08c5fdd08ffd'), ObjectId('5ec239ff2238a1f9d2d08ffd'), ObjectId('5ec23ad2a2c9338e0dd08ffd'), ObjectId('5ec23b4c4a76c8c16ad08ffd'), ObjectId('5ec23c07016ceead4ad08ffd'), ObjectId('5ec23d01e7875d6ec6d08ffd'), ObjectId('5ec23df2bf7991c467d08ffd'), ObjectId('5ec23eb410081f5532d08ffd'), ObjectId('5ec23f90f441b7fd1fd08ffd'), ObjectId('5ec24063f679b60aafd08ffd'), ObjectId('5ec24155a66fea5c51d08ffd'), ObjectId('5ec2422c64e43b2f41d08ffd'), ObjectId('5ec242a19d1014af3bd08ffd'), ObjectId('5ec243424e63cb702fd08ffd'), ObjectId('5ec243ee34635d5f76d08ffd'), ObjectId('5ec244619729800771d08ffd'), ObjectId('5ec244fdfe651af9f0d08ffd'), ObjectId('5ec2459d77f945cad9d08ffd'), ObjectId('5ec24617506595602ad08ffd'), ObjectId('5ec246a8e9be5ce540d08ffd'), ObjectId('5ec24747d2654d3f9cd08ffd'), ObjectId('5ec248ac8c5bfb592fd08ffd'), ObjectId('5ec249bd1a6e53564bd08ffd'), ObjectId('5ec24a63548ffb04f5d08ffd'), ObjectId('5ec24b23af92ca5bcdd08ffd'), ObjectId('5ec24ce901e6de5db5d08ffd'), ObjectId('5ec24df67f29b5c53fd08ffd'), ObjectId('5ec24eb75c15c61225d08ffd'), ObjectId('5ec24f50aaf3998a63d08ffd'), ObjectId('5ec25055fb6c66bfe7d08ffd'), ObjectId('5ec25154e08a6f3b5bd08ffd'), ObjectId('5ec251d99c2b8f1c33d08ffd'), ObjectId('5ec2529091262b4135d08ffd'), ObjectId('5ec253a572e6a5b8dbd08ffd'), ObjectId('5ec2547eb817507ceed08ffd'), ObjectId('5ec2555f398fbddf6bd08ffd'), ObjectId('5ec25603ebe398f839d08ffd'), ObjectId('5ec25681f6686e65d6d08ffd'), ObjectId('5ec25723016ffa26a0d08ffd'), ObjectId('5ec2581cce74147a42d08ffd'), ObjectId('5ec258da1b87ceba8cd08ffd'), ObjectId('5ec2597f9f5d4ca8f6d08ffd'), ObjectId('5ec25a45f9c2319636d08ffd'), ObjectId('5ec25af1fe9551eae5d08ffd'), ObjectId('5ec25b8abc2df24082d08ffd'), ObjectId('5ec25c232cdcdffa69d08ffd'), ObjectId('5ec25d3620ca9d30b4d08ffd'), ObjectId('5ec25dc408daa00e01d08ffd'), ObjectId('5ec25ea2c46c77f8f3d08ffd'), ObjectId('5ec25f2057c1fb9268d08ffd'), ObjectId('5ec25fd2a46d610ba0d08ffd'), ObjectId('5ec2609daf69566ebfd08ffd'), ObjectId('5ec2618f08d578e86bd08ffd'), ObjectId('5ec2635d0c0df3decfd08ffd'), ObjectId('5ec2643f87dc5179e5d08ffd'), ObjectId('5ec264e5fde80534ead08ffd'), ObjectId('5ec265f19d421d6f34d08ffd'), ObjectId('5ec26671f3e39e07b9d08ffd'), ObjectId('5ec266f42405fcbc2fd08ffd'), ObjectId('5ec267a9614a677f4ad08ffd'), ObjectId('5ec26897b46ac02756d08ffd'), ObjectId('5ec26959705db73b99d08ffd'), ObjectId('5ec269e72bad462454d08ffd'), ObjectId('5ec26aae9c94c6b42dd08ffd'), ObjectId('5ec26ba58f056ca605d08ffd'), ObjectId('5ec26d0a7462e3b2b4d08ffd'), ObjectId('5ec26db22874d3e7a1d08ffd'), ObjectId('5ec26e366194d5671ad08ffd'), ObjectId('5ec26eccf4a1a69faad08ffd'), ObjectId('5ec26f2d384ef25892d08ffd'), ObjectId('5ec26f960c28425fc6d08ffd'), ObjectId('5ec270991df2b6dcb3d08ffd'), ObjectId('5ec2714b3ffee3bc9dd08ffd'), ObjectId('5ec271eb10b62fd1c2d08ffd'), ObjectId('5ec27288bd74feea65d08ffd'), ObjectId('5ec2734a8356c97f44d08ffd'), ObjectId('5ec274551c6cfd72bad08ffd'), ObjectId('5ec2750d493f9d64e3d08ffd'), ObjectId('5ec275ba97992f1134d08ffd'), ObjectId('5ec27641b4a189d3fad08ffd'), ObjectId('5ec27727fd3d080103d08ffd'), ObjectId('5ec277d5ca4f08b78dd08ffd'), ObjectId('5ec278aa7c9f8148cbd08ffd'), ObjectId('5ec27946ed9442bed0d08ffd'), ObjectId('5ec27a0560b88319b4d08ffd'), ObjectId('5ec27ace4475d6fc0cd08ffd'), ObjectId('5ec27be89d8a019a4dd08ffd'), ObjectId('5ec27c972320b2efd9d08ffd'), ObjectId('5ec27d29c1215c372ad08ffd'), ObjectId('5ec27daaca79a51e4ed08ffd'), ObjectId('5ec27e46d5c6b3d772d08ffd'), ObjectId('5ec27ef4b8aca303e8d08ffd'), ObjectId('5ec2800bb7d0988a19d08ffd'), ObjectId('5ec2809d68f85aca90d08ffd'), ObjectId('5ec2811a0358b118e9d08ffd'), ObjectId('5ec282a717f1a373ded08ffd'), ObjectId('5ec2834afada92cceed08ffd'), ObjectId('5ec285634cafcdb16dd08ffd'), ObjectId('5ec2861fe690a8c605d08ffd'), ObjectId('5ec2870297e71b2224d08ffd'), ObjectId('5ec2882e9b412efe2ed08ffd'), ObjectId('5ec289225b8276076bd08ffd'), ObjectId('5ec28a560042707268d08ffd'), ObjectId('5ec28b4c1a3f238debd08ffd'), ObjectId('5ec28c3711f50cb049d08ffd'), ObjectId('5ec28d33a1eaf8b38dd08ffd'), ObjectId('5ec28e72c900d3c5aad08ffd'), ObjectId('5ec28f7ea98b43e760d08ffd'), ObjectId('5ec2909b1642056f60d08ffd'), ObjectId('5ec29188a970126b6cd08ffd'), ObjectId('5ec29205199b47a279d08ffd'), ObjectId('5ec2931bc0ad9248e6d08ffd'), ObjectId('5ec2943099671b3926d08ffd'), ObjectId('5ec2957cf9ac784f00d08ffd'), ObjectId('5ec296461cd121f455d08ffd'), ObjectId('5ec297b81ea52b7eead08ffd'), ObjectId('5ec2987f03d6dfc76fd08ffd'), ObjectId('5ec298f4f5f0dd0ccdd08ffd'), ObjectId('5ec29f29d804f0761cd08ffd'), ObjectId('5ec2a06ee9d5ed6f19d08ffd'), ObjectId('5ec2a1e052c0d2770ed08ffd'), ObjectId('5ec2a31794d6625b4ed08ffd'), ObjectId('5ec2a471f8ab29096dd08ffd'), ObjectId('5ec2a580ab0402974bd08ffd'), ObjectId('5ec2a668d6612a93f5d08ffd'), ObjectId('5ec2a760509168bd48d08ffd'), ObjectId('5ec2a83dfd6180aba2d08ffd'), ObjectId('5ec2a952971a583df2d08ffd'), ObjectId('5ec2aa04af3b98009ad08ffd'), ObjectId('5ec2aadc412396f0cdd08ffd'), ObjectId('5ec2abe020315d5804d08ffd'), ObjectId('5ec2ad0b0e14d7a6d8d08ffd'), ObjectId('5ec2ae6e427f88452bd08ffd'), ObjectId('5ec2aef51e4f004dadd08ffd'), ObjectId('5ec2afca06665058c6d08ffd'), ObjectId('5ec2b0c945552336b5d08ffd'), ObjectId('5ec2b1ca31b9046978d08ffd'), ObjectId('5ec2b2b00e76e69558d08ffd'), ObjectId('5ec2b43685a2f92633d08ffd'), ObjectId('5ec2b5406c7dbb552ed08ffd'), ObjectId('5ec2b5f9df2124ca28d08ffd'), ObjectId('5ec2b76a09548e8058d08ffd'), ObjectId('5ec2b98bd80d085baed08ffd'), ObjectId('5ec2ba293cc97cfe03d08ffd'), ObjectId('5ec2bafb5942aca9f2d08ffd'), ObjectId('5ec2bc0bcbfab288a9d08ffd'), ObjectId('5ec2bcc322b5e302ead08ffd'), ObjectId('5ec2bd51c1fad7d413d08ffd'), ObjectId('5ec2bddd76eb2e5d07d08ffd'), ObjectId('5ec2beba23fd6fb2b8d08ffd'), ObjectId('5ec2bfbf01a412bb1fd08ffd'), ObjectId('5ec2c061dd4178beb5d08ffd'), ObjectId('5ec2c1282bf6d05dcfd08ffd'), ObjectId('5ec2c1bbfb16c38036d08ffd'), ObjectId('5ec2c306f214f4b61bd08ffd'), ObjectId('5ec2c3efd8d520e160d08ffd'), ObjectId('5ec2c46847f3a255d0d08ffd'), ObjectId('5ec2c51a045f1a7508d08ffd'), ObjectId('5ec2c5dbd348cd81fbd08ffd'), ObjectId('5ec2c6fab7d1f5624ad08ffd'), ObjectId('5ec2c7a08558b84b71d08ffd'), ObjectId('5ec2c8508bd6bdbdc0d08ffd'), ObjectId('5ec2c8e910bdf18b51d08ffd'), ObjectId('5ec2c9898fa16f4a79d08ffd'), ObjectId('5ec2ca00f18e322609d08ffd'), ObjectId('5ec2caa5f6a74cc792d08ffd'), ObjectId('5ec2cb9f4e9f0dd4a8d08ffd'), ObjectId('5ec2cdedb1f6b40b84d08ffd'), ObjectId('5ec2cefecd9f1f68a6d08ffd'), ObjectId('5ec2cfa75b2f7c2326d08ffd'), ObjectId('5ec2d09084399c9f05d08ffd'), ObjectId('5ec2d12c5caea061cad08ffd'), ObjectId('5ec2d1ed49fd07a0dcd08ffd'), ObjectId('5ec2d2cebb80b7166bd08ffd'), ObjectId('5ec2d39acc72f4d0a9d08ffd'), ObjectId('5ec2d48fcf5de39b25d08ffd'), ObjectId('5ec2d5b866a1cc5043d08ffd'), ObjectId('5ec2d70878eb72dd7cd08ffd'), ObjectId('5ec2d854ff096f7e22d08ffd'), ObjectId('5ec2d98e3b684229d1d08ffd'), ObjectId('5ec2dab10e1437ee20d08ffd'), ObjectId('5ec2dbc936d5fcca0dd08ffd'), ObjectId('5ec2dcf639fe0a0512d08ffd'), ObjectId('5ec2de1c1830cf434ad08ffd'), ObjectId('5ec2df4284310f309fd08ffd'), ObjectId('5ec2dfd22cd3eef557d08ffd'), ObjectId('5ec2e0550b1ee2fb8fd08ffd'), ObjectId('5ec2e124d477fee603d08ffd'), ObjectId('5ec2e3487c18ec185ad08ffd'), ObjectId('5ec2e4887921fa320ad08ffd'), ObjectId('5ec2e5b016c16643bdd08ffd'), ObjectId('5ec2e6314464e3b4b3d08ffd'), ObjectId('5ec2e7976dfe70ba67d08ffd'), ObjectId('5ec2e8435b8b633017d08ffd'), ObjectId('5ec2e8e601229acd4bd08ffd'), ObjectId('5ec2e9c78cb93d2419d08ffd'), ObjectId('5ec2eb4267d8606175d08ffd'), ObjectId('5ec2ebf8d07233da27d08ffd'), ObjectId('5ec2ed5c4f2c175bd9d08ffd'), ObjectId('5ec2eeb5856d69ccd0d08ffd'), ObjectId('5ec2f0c8536b732760d08ffd'), ObjectId('5ec2f1f8333a35d3fcd08ffd'), ObjectId('5ec2f324cd51f9c853d08ffd'), ObjectId('5ec2f49e235cdc5381d08ffd'), ObjectId('5ec2f60b07f2ba99b9d08ffd'), ObjectId('5ed3846f023b726e6d17d4f0'), ObjectId('5ed38b25d439f58cc06e5825'), ObjectId('5ed38d5420653aee6e3220c8'), ObjectId('5ed38efe1838c05e0c6fb6e4'), ObjectId('5ed3900863e5bffa1d2b4e2f'), ObjectId('5ed391925d33c4975503bb94'), ObjectId('5ed394144eb75866dfdcdc0d'), ObjectId('5ed39521d784bdc428779a0f'), ObjectId('5ed3966ae5903d41b23471ba'), ObjectId('5ed3980c016ddd49b0f4c304'), ObjectId('5ed3996045e3020d63762dce'), ObjectId('5ed39b1195eba19024e714bf'), ObjectId('5ed39d3781f6df0d82e6bfda'), ObjectId('5ed39f30fc1a9fd5e77e332f'), ObjectId('5ed3a07a5dbe3d7cdbc0a11f'), ObjectId('5ed3a21a7deae88594ebebcb'), ObjectId('5ed3a430b15357da758e9aaf'), ObjectId('5ed3a65cc612795088fb19b8'), ObjectId('5ed3a8655fa4a60f979e1f88'), ObjectId('5ed3ac8b4daab633d19b58d8'), ObjectId('5ed3add3461496c2716f7235'), ObjectId('5ed3af522f225fd825bf711a'), ObjectId('5ed3b088624645fcbe0374c5'), ObjectId('5ed3b2383758cc50c8bdd137'), ObjectId('5ed3b766a882d958e63eb52e')]
edu_set = [ObjectId('5eb62e2a134cc6fb9536e93d'), ObjectId('5eb630147afe26eca4ba7bfa'), ObjectId('5eb6311c86662885174692de'), ObjectId('5eb631f1fac479799dedd1f8'), ObjectId('5eb6331597c8f5512179c4f1'), ObjectId('5eb634492802acb8c48e02aa'), ObjectId('5eb63539be65b70e5af0c7a9'), ObjectId('5eb6363894bd0b097f9c2734'), ObjectId('5eb6378b772150870b5c8d27'), ObjectId('5eb639ee2c60aae411d1ae8b'), ObjectId('5eb63aff81de1c4846fd91ab'), ObjectId('5eb63c1e9c69232f6ed6edd8'), ObjectId('5eb63d1b9d2ec0b892c42dd5'), ObjectId('5eb63e1ee805d1cff3d80a25'), ObjectId('5eb63ee743b668cb27ef8137'), ObjectId('5eb640560732058562a400b3'), ObjectId('5eb646ce3b4442b4da91c057'), ObjectId('5eb6479687b6932b9e6de098'), ObjectId('5eb648bf6bc924ef46ab60da'), ObjectId('5eb64a8e96bdd2bbbb3287e5'), ObjectId('5eb64bc810a22fecd4eca987'), ObjectId('5eb64cfc8c94747a21f39855'), ObjectId('5eb64e13158973dfa9982019'), ObjectId('5eb64f4ea0549166c51ca057'), ObjectId('5eb650acab06d680d6990351'), ObjectId('5eb651bc5fa088c453991725'), ObjectId('5eb652de55de509b4a9efaf4'), ObjectId('5eb65433af5bcc3efe32c504'), ObjectId('5eb6556c29c37695bc97bec4'), ObjectId('5eb6567909d0de1b6b708cf8'), ObjectId('5eb657e754ee9cbe1a7388c8'), ObjectId('5eb65942b46918d079adebe9'), ObjectId('5eb65a927cb5b3a1ff4ae362'), ObjectId('5eb65b645417d406270e7e63'), ObjectId('5eb65d83728ad01002b3a5f6'), ObjectId('5eb65f2cde8cab37cd68dffd'), ObjectId('5eb6603b6e69c6f2e1092cf8'), ObjectId('5eb661a6796445df9bfd756d'), ObjectId('5eb6631b245b7e033d0f92ed'), ObjectId('5eb66401b0e60a643fae0467'), ObjectId('5eb6651284c93e9e1b685024'), ObjectId('5eb66682dc99a524418da337'), ObjectId('5eb667a554cc6bc47dbfea44'), ObjectId('5eb6688cf9acda3a876322e4'), ObjectId('5eb669883e6dc49bd6f1540f'), ObjectId('5eb66a9b90f9dd06f1107866'), ObjectId('5eb66bb449a0728d932475bc'), ObjectId('5eb66ce4535d821544a14dee'), ObjectId('5eb66dabf3d5b58ef16a4c74'), ObjectId('5eb66e99e95b7d86f2518828'), ObjectId('5eb66fa738555190120005d2'), ObjectId('5eb670c2382a70cea3c90149'), ObjectId('5eb672382cf60f5b673dc845'), ObjectId('5eb6734f61272a1489607d7c'), ObjectId('5eb6746b3f8078c646a32068'), ObjectId('5eb675384beae11731a0ce35'), ObjectId('5eb676209d0d155a1c6530f3'), ObjectId('5eb6777b140e783b3524f4d9'), ObjectId('5eb6783b3dd775bea489b02d'), ObjectId('5eb67952c38498d75c86627f'), ObjectId('5eb67a4c109ddab70aec7b2d'), ObjectId('5eb67bc12373d9a910e8750f'), ObjectId('5eb67d3dd9818bcd44884d39'), ObjectId('5eb67e66b7921dcf1c2e6805'), ObjectId('5eb67fa821374c1c36ea76bb'), ObjectId('5eb680d98c70c48229cd26b6'), ObjectId('5eb6820dcc1fecfea5009f48'), ObjectId('5eb682ecd810c81378eb806d'), ObjectId('5eb68405b8f3f1e1b3084a52'), ObjectId('5eb6853a626f824ef428e315'), ObjectId('5eb688a782ee2ac4699515f2'), ObjectId('5eb689814e048265dd507dbc'), ObjectId('5eb68a771a268ae85ef97960'), ObjectId('5eb68b52298db2bd4cebdd0e'), ObjectId('5eb68c65501e64174bede873'), ObjectId('5eb68d458e708541f4671189'), ObjectId('5eb68e2fab2ce0451e2b4056'), ObjectId('5eb68edce0b5b75b05fba1e6'), ObjectId('5eb690038f7f6e26b6253fd5'), ObjectId('5eb690bd8d99ac316303ffb6'), ObjectId('5eb6918fa2e66438837c2d83'), ObjectId('5eb6925a31a5f94e1207b916'), ObjectId('5eb6944565d7b2466379f198'), ObjectId('5eb694f59c10ae1d407b7c2a'), ObjectId('5eb695e1ffe996bbe09292fe'), ObjectId('5eb696f6ef36438bec383b7e'), ObjectId('5eb697cac579ca076779cb0f'), ObjectId('5eb698a46de98c90f95a497d'), ObjectId('5eb699a671806057e76f0141'), ObjectId('5eb69a7d5587c492135fd56c'), ObjectId('5eb69b6fc6cad85bd913e12a'), ObjectId('5eb69c52d1ecab806f2beead'), ObjectId('5eb69cefc81bdf1aac4bf6a1'), ObjectId('5eb69e087e9ea4385e20beed'), ObjectId('5eb69f48a04ce33b509b4895'), ObjectId('5eb6a058cd265d6ef2ee766f'), ObjectId('5eb6a12f7ef80a97c531cc67'), ObjectId('5eb6a21fe632eaf0b1d593db'), ObjectId('5eb6a63fc0820e4534126e94'), ObjectId('5eb6a72dfc5d1c47d4ca9cd1'), ObjectId('5eb6a8462d272649f7b4df95'), ObjectId('5eb6a930b440ebf60d42d6c2'), ObjectId('5eb6aa15b5b4db2c7393254c'), ObjectId('5eb6ab260aef4a583d77118f'), ObjectId('5eb6ac1bfff106a6f58c42e7'), ObjectId('5eb6ad1662db4e6c180a378b'), ObjectId('5eb6ae390bdb0b194f41f9b3'), ObjectId('5eb6af2a6012ca09c1728130'), ObjectId('5eb6afc4e15b344d1a3aafa0'), ObjectId('5eb6b19b1c6e630676c62445'), ObjectId('5eb6b2a5a9211572420260e9'), ObjectId('5eb6b38eeb5e21b75a0d7cdb'), ObjectId('5eb6b45f4dab807be8d7a28a'), ObjectId('5eb6b53fd8471918b43146b7'), ObjectId('5eb6b61fabf00d5fdb2d05a3'), ObjectId('5eb6b71e5cd9b7b54c7d9961'), ObjectId('5eb6b9158f232307ce0bdc13'), ObjectId('5eb6b9dbb8b6b03010c4dcc6'), ObjectId('5eb6bad32c05d6f34cf32652'), ObjectId('5eb6bbbee2f17c3f3238cec8'), ObjectId('5eb6bca1b68e7672cd0ef210'), ObjectId('5eb6bdb1e7b6cc4614eb0edb'), ObjectId('5eb6beca47492aa1e0553de4'), ObjectId('5eb6bfc707fd60d7d77844de'), ObjectId('5ed3846f023b726e6d17d4f0'), ObjectId('5ed38b25d439f58cc06e5825'), ObjectId('5ed38d5420653aee6e3220c8'), ObjectId('5ed38efe1838c05e0c6fb6e4'), ObjectId('5ed3900863e5bffa1d2b4e2f'), ObjectId('5ed391925d33c4975503bb94'), ObjectId('5ed394144eb75866dfdcdc0d'), ObjectId('5ed39521d784bdc428779a0f'), ObjectId('5ed3966ae5903d41b23471ba'), ObjectId('5ed3980c016ddd49b0f4c304'), ObjectId('5ed3996045e3020d63762dce'), ObjectId('5ed39b1195eba19024e714bf'), ObjectId('5ed39d3781f6df0d82e6bfda'), ObjectId('5ed39f30fc1a9fd5e77e332f'), ObjectId('5ed3a07a5dbe3d7cdbc0a11f'), ObjectId('5ed3a21a7deae88594ebebcb'), ObjectId('5ed3a430b15357da758e9aaf'), ObjectId('5ed3a65cc612795088fb19b8'), ObjectId('5ed3a8655fa4a60f979e1f88'), ObjectId('5ed3ac8b4daab633d19b58d8'), ObjectId('5ed3add3461496c2716f7235'), ObjectId('5ed3af522f225fd825bf711a'), ObjectId('5ed3b088624645fcbe0374c5'), ObjectId('5ed3b2383758cc50c8bdd137'), ObjectId('5ed3b766a882d958e63eb52e')]
left_set = [item for item in all_ids_fixed if item not in edu_set]

to_fix = [ObjectId('5f1e94db027fb1582fb3874a'), ObjectId('5f1e9574027fb1582fb38758'), ObjectId('5f1e997862de5888b3f12e3e'), ObjectId('5f1e99ee62de5888b3f12e46'), ObjectId('5f1e9be462de5888b3f12e5b'), ObjectId('5f1e9c3b62de5888b3f12e63'), ObjectId('5f1e9cb062de5888b3f12e6d'), ObjectId('5f1eac7f62de5888b3f12ea3'), ObjectId('5f1eacf362de5888b3f12ea7'), ObjectId('5f1ead1d62de5888b3f12eab'), ObjectId('5f1ead5462de5888b3f12eaf'), ObjectId('5f1eadd362de5888b3f12eb3'), ObjectId('5f1eae8662de5888b3f12ec8'), ObjectId('5f1eaef362de5888b3f12ed2'), ObjectId('5f1ecdec62de5888b3f12ee7'), ObjectId('5f1ece0162de5888b3f12ee9'), ObjectId('5f1ece2062de5888b3f12eeb'), ObjectId('5f1ece9262de5888b3f12ef1'), ObjectId('5f1ecf5362de5888b3f12f04'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f1ece6962de5888b3f12eef'), ObjectId('5f1ed77162de5888b3f12f17'), ObjectId('5f1ed7a562de5888b3f12f1b'), ObjectId('5f1ed7c362de5888b3f12f1d'), ObjectId('5f1ed7ee62de5888b3f12f21'), ObjectId('5f1ed83762de5888b3f12f25'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f1ed90062de5888b3f12f3c'), ObjectId('5f1ed9a162de5888b3f12f4a'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('5f1eda3262de5888b3f12f5f'), ObjectId('5f1eda4862de5888b3f12f61'), ObjectId('5f1ed92a62de5888b3f12f40'), ObjectId('5f1ed94062de5888b3f12f42'), ObjectId('5f1ed98b62de5888b3f12f48')]
to_fix_all = [ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f183dde464603f10dce0da2'), ObjectId('5f183dfe464603f10dce0da4'), ObjectId('5f183e14464603f10dce0da6'), ObjectId('5f183e53464603f10dce0dab'), ObjectId('5f183e89464603f10dce0dae'), ObjectId('5f183e9d464603f10dce0db0'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f183f13464603f10dce0dba'), ObjectId('5f183eb3464603f10dce0db2'), ObjectId('5f183f28464603f10dce0dbc'), ObjectId('5f183efd464603f10dce0db8'), ObjectId('5f183ee7464603f10dce0db6'), ObjectId('5f183e29464603f10dce0da8'), ObjectId('5f186b7cb448d46665f7ff02'), ObjectId('5f18750a182dbb7a59a62642'), ObjectId('5f187522182dbb7a59a62644'), ObjectId('5f18756b182dbb7a59a62649'), ObjectId('5f187595182dbb7a59a6264d'), ObjectId('5f1875c9182dbb7a59a62650'), ObjectId('5f187556182dbb7a59a62647'), ObjectId('5f187580182dbb7a59a6264b'), ObjectId('5f18840a35a2278f64f9e5f2'), ObjectId('5f18841f35a2278f64f9e5f4'), ObjectId('5f18843e35a2278f64f9e5f6'), ObjectId('5f18962935a2278f64f9e647'), ObjectId('5f189e1d35a2278f64f9e676'), ObjectId('5f18ed6535a2278f64f9e6bf'), ObjectId('5f18ec3135a2278f64f9e6a7'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f18ec7035a2278f64f9e6ac'), ObjectId('5f18ec8435a2278f64f9e6ae'), ObjectId('5f18eca435a2278f64f9e6b0'), ObjectId('5f18ecbb35a2278f64f9e6b2'), ObjectId('5f18ecd035a2278f64f9e6b4'), ObjectId('5f18ece535a2278f64f9e6b6'), ObjectId('5f18ecfa35a2278f64f9e6b8'), ObjectId('5f18ed0f35a2278f64f9e6ba'), ObjectId('5f18ed5035a2278f64f9e6bd'), ObjectId('5f18ed8f35a2278f64f9e6ce'), ObjectId('5f19077f5fe76f8f85f401fa'), ObjectId('5f197a573efb8669e251a4f6'), ObjectId('5f197b283efb8669e251a500'), ObjectId('5f19c87c09e1c3c703025666'), ObjectId('5f19c8a709e1c3c70302566a'), ObjectId('5f19c95d09e1c3c70302567a'), ObjectId('5f19c9a609e1c3c703025680'), ObjectId('5f19ca3509e1c3c70302568c'), ObjectId('5f19ca4a09e1c3c70302568e'), ObjectId('5f19ca9409e1c3c703025694'), ObjectId('5f19c8f009e1c3c703025670'), ObjectId('5f19cabe09e1c3c703025698'), ObjectId('5f19c8bc09e1c3c70302566c'), ObjectId('5f19c98709e1c3c70302567e'), ObjectId('5f19ca5e09e1c3c703025690'), ObjectId('5f19d55909e1c3c7030256ab'), ObjectId('5f19d58409e1c3c7030256af'), ObjectId('5f19d59a09e1c3c7030256b1'), ObjectId('5f19d5af09e1c3c7030256b3'), ObjectId('5f19d61009e1c3c7030256bb'), ObjectId('5f19d68709e1c3c7030256c5'), ObjectId('5f19d6b209e1c3c7030256c9'), ObjectId('5f19d6df09e1c3c7030256cd'), ObjectId('5f19d72109e1c3c7030256d3'), ObjectId('5f19d56f09e1c3c7030256ad'), ObjectId('5f19d78d09e1c3c7030256dd'), ObjectId('5f19d54209e1c3c7030256a9'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f19d70b09e1c3c7030256d1'), ObjectId('5f1e94db027fb1582fb3874a'), ObjectId('5f1e9574027fb1582fb38758'), ObjectId('5f1e997862de5888b3f12e3e'), ObjectId('5f1e99ee62de5888b3f12e46'), ObjectId('5f1e9be462de5888b3f12e5b'), ObjectId('5f1e9c3b62de5888b3f12e63'), ObjectId('5f1e9cb062de5888b3f12e6d'), ObjectId('5f1eac7f62de5888b3f12ea3'), ObjectId('5f1eacf362de5888b3f12ea7'), ObjectId('5f1ead1d62de5888b3f12eab'), ObjectId('5f1ead5462de5888b3f12eaf'), ObjectId('5f1eadd362de5888b3f12eb3'), ObjectId('5f1eae8662de5888b3f12ec8'), ObjectId('5f1eaef362de5888b3f12ed2'), ObjectId('5f1ecdec62de5888b3f12ee7'), ObjectId('5f1ece0162de5888b3f12ee9'), ObjectId('5f1ece2062de5888b3f12eeb'), ObjectId('5f1ece9262de5888b3f12ef1'), ObjectId('5f1ecf5362de5888b3f12f04'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f1ece6962de5888b3f12eef'), ObjectId('5f1ed77162de5888b3f12f17'), ObjectId('5f1ed7a562de5888b3f12f1b'), ObjectId('5f1ed7c362de5888b3f12f1d'), ObjectId('5f1ed7ee62de5888b3f12f21'), ObjectId('5f1ed83762de5888b3f12f25'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f1ed90062de5888b3f12f3c'), ObjectId('5f1ed9a162de5888b3f12f4a'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('5f1eda3262de5888b3f12f5f'), ObjectId('5f1eda4862de5888b3f12f61'), ObjectId('5f1ed92a62de5888b3f12f40'), ObjectId('5f1ed94062de5888b3f12f42'), ObjectId('5f1ed98b62de5888b3f12f48')]

# simplified_update(to_fix_all)
# check_aven(edu_set)
# address_conf(edu_set[0:1])
# check_aven(left_set)
# simplified_export_with_sources(to_fix_all)
# check_tp(edu_set)
# check_tp(edu_set)
# clear_dnb(left_set)
# dump_address_fix(edu_set)
# flat_csv(edu_set)
# simplified_update(edu_set)
# check_aven(edu_set)

# check_link(left_set)
# contact_person_fix(edu_set)
# dump_contact_person_fix(edu_set)
# contact_person_fix(edu_set)
# hq_fix(edu_set)
# dump_hq_fix(edu_set)
# fix_ne(edu_set)
# rev_fix(edu_set)
# email_fix(list_aus)
# tp_fix(edu_set)
# simplified_update(edu_set)
# simplified_export_with_sources(edu_set)
# dump_tp_fix(edu_set)
# address_fix(edu_set)
# dump_address_fix(edu_set)
# sector_fix(edu_set)
# fy_fix(list_aus)
# partial_export(all_ids_2017)
# fix_100(ids_l[0:100])

# check_link(left_set)
# check_empty_addresses(left_set)

# [ObjectId('5eb7c0a011ad0e77a8454c2c'), ObjectId('5eb81dd8312f24e51eaa1667'), ObjectId('5eb81e2a312f24e51eaa166a'), ObjectId('5eb94caf01a53921bf21f86d'), ObjectId('5ebc44847ce40c9ba7bb9565'), ObjectId('5ebc452ac7057c1a4cbb9565'), ObjectId('5ebcc58db3643873f0bb9565')]
# to_get = [ObjectId('5f3d21329e81673edaf9fae6'),ObjectId('5ebe0cd9a0d22e0d5723510e'),ObjectId('5ebe0a0d110384add423510e'),ObjectId('5f3cfbf0c71b48600826b3ec'),ObjectId('5ebe17207e47e5354a23510e'),ObjectId('5f1881c535a2278f64f9e5d8'),ObjectId('5ebe0bb08df9dfa24723510e'),ObjectId('5f3cfc2fc71b48600826b407'),ObjectId('5ebe1c36bc048b033d23510e'),ObjectId('5f3cfc5dc71b48600826b41a'),ObjectId('5f3cfc79c71b48600826b429'),ObjectId('5f3cfc8fc71b48600826b438'),ObjectId('5ec27727fd3d080103d08ffd'),ObjectId('5ec277d5ca4f08b78dd08ffd'),ObjectId('5f3cfcc1c71b48600826b44f'),ObjectId('5ec27a0560b88319b4d08ffd'),ObjectId('5ebc53a9503b1f44d4bb9565'),ObjectId('5eb957e0b1f04156bd21f86d'),ObjectId('5ebc54e10c8dd65b2ebb9565'),ObjectId('5ebc55d8b8becb694ebb9565')]
# later = [ObjectId('5f4f18e1b40ca91fa5181641'),ObjectId('5f4f19b0b40ca91fa518165f'),ObjectId('5f4f19efb40ca91fa518166e'),ObjectId('5f4f3fabb40ca91fa5181690'),ObjectId('5f4f4035b40ca91fa51816ae'),ObjectId('5f4f3fe9b40ca91fa518169f'),ObjectId('5f4f1953b40ca91fa5181650'),ObjectId('5f4f406bb40ca91fa51816bd'),ObjectId('5f4f3f69b40ca91fa5181681')]

# simplified_export_with_sources(later)
# simplified_export([ObjectId('5ebc56ea2e7d8c6aeebb9565')])
# dnb, crunchbase, owler, oc, linkedin, avention
def check_ids(id_list):
    csv_dump_col = refer_simplified_dump_col_min()
    for id in id_list:
        entry = csv_dump_col.find({"_id": str(id)},)
        data = [d for d in entry]
        print(data[0]['_id'])
        csv_dump_col.update_one({'_id': id}, {'$set': {'u_id': ObjectId(id)}})
def re_fix(id_list):
    mycol = refer_collection()
    for id_a in id_list:
        entry = mycol.find({"_id": id_a}, )
        data = [d for d in entry]
        print(data[0]['_id'])
        mycol.update_one({'_id': id_a}, {'$set': {'simplified_dump_state': 'Completed'}})
# re_list = [ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f183dde464603f10dce0da2'), ObjectId('5f183dfe464603f10dce0da4'), ObjectId('5f183e14464603f10dce0da6'), ObjectId('5f183e53464603f10dce0dab'), ObjectId('5f183e89464603f10dce0dae'), ObjectId('5f183e89464603f10dce0dae'), ObjectId('5f183e9d464603f10dce0db0'), ObjectId('5f183eb3464603f10dce0db2'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f183ee7464603f10dce0db6'), ObjectId('5f183efd464603f10dce0db8'), ObjectId('5f183f13464603f10dce0dba'), ObjectId('5f183f28464603f10dce0dbc'), ObjectId('5f186b7cb448d46665f7ff02'), ObjectId('5f18750a182dbb7a59a62642'), ObjectId('5f187522182dbb7a59a62644'), ObjectId('5f187556182dbb7a59a62647'), ObjectId('5f18756b182dbb7a59a62649'), ObjectId('5f187580182dbb7a59a6264b'), ObjectId('5f187595182dbb7a59a6264d'), ObjectId('5f1875c9182dbb7a59a62650'), ObjectId('5f18840a35a2278f64f9e5f2'), ObjectId('5f18841f35a2278f64f9e5f4'), ObjectId('5f18843e35a2278f64f9e5f6'), ObjectId('5f18962935a2278f64f9e647'), ObjectId('5f189e1d35a2278f64f9e676'), ObjectId('5f18ec3135a2278f64f9e6a7'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f18ec7035a2278f64f9e6ac'), ObjectId('5f18ec8435a2278f64f9e6ae'), ObjectId('5f18eca435a2278f64f9e6b0'), ObjectId('5f18ecbb35a2278f64f9e6b2'), ObjectId('5f18ecd035a2278f64f9e6b4'), ObjectId('5f18ece535a2278f64f9e6b6'), ObjectId('5f18ecfa35a2278f64f9e6b8'), ObjectId('5f18ed0f35a2278f64f9e6ba'), ObjectId('5f18ed5035a2278f64f9e6bd'), ObjectId('5f18ed6535a2278f64f9e6bf'), ObjectId('5f18ed8f35a2278f64f9e6ce'), ObjectId('5f19077f5fe76f8f85f401fa'), ObjectId('5f197a573efb8669e251a4f6'), ObjectId('5f197b283efb8669e251a500'), ObjectId('5f19c87c09e1c3c703025666'), ObjectId('5f19c8a709e1c3c70302566a'), ObjectId('5f19c8bc09e1c3c70302566c'), ObjectId('5f19c8f009e1c3c703025670'), ObjectId('5f19c95d09e1c3c70302567a'), ObjectId('5f19c98709e1c3c70302567e'), ObjectId('5f19c9a609e1c3c703025680'), ObjectId('5f19ca3509e1c3c70302568c'), ObjectId('5f19ca4a09e1c3c70302568e'), ObjectId('5f19ca5e09e1c3c703025690'), ObjectId('5f19ca9409e1c3c703025694'), ObjectId('5f19cabe09e1c3c703025698'), ObjectId('5f19d54209e1c3c7030256a9'), ObjectId('5f19d55909e1c3c7030256ab'), ObjectId('5f19d56f09e1c3c7030256ad'), ObjectId('5f19d58409e1c3c7030256af'), ObjectId('5f19d59a09e1c3c7030256b1'), ObjectId('5f19d5af09e1c3c7030256b3'), ObjectId('5f19d61009e1c3c7030256bb'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f19d68709e1c3c7030256c5'), ObjectId('5f19d6b209e1c3c7030256c9'), ObjectId('5f19d6df09e1c3c7030256cd'), ObjectId('5f19d70b09e1c3c7030256d1'), ObjectId('5f19d72109e1c3c7030256d3'), ObjectId('5f19d78d09e1c3c7030256dd'), ObjectId('5f1e94db027fb1582fb3874a'), ObjectId('5f1e9574027fb1582fb38758'), ObjectId('5f1e997862de5888b3f12e3e'), ObjectId('5f1e99ee62de5888b3f12e46'), ObjectId('5f1e9be462de5888b3f12e5b'), ObjectId('5f1e9c3b62de5888b3f12e63'), ObjectId('5f1e9cb062de5888b3f12e6d'), ObjectId('5f1eac7f62de5888b3f12ea3'), ObjectId('5f1eacf362de5888b3f12ea7'), ObjectId('5f1ead1d62de5888b3f12eab'), ObjectId('5f1ead5462de5888b3f12eaf'), ObjectId('5f1eadd362de5888b3f12eb3'), ObjectId('5f1eae8662de5888b3f12ec8'), ObjectId('5f1eaef362de5888b3f12ed2'), ObjectId('5f1ecdec62de5888b3f12ee7'), ObjectId('5f1ece0162de5888b3f12ee9'), ObjectId('5f1ece2062de5888b3f12eeb'), ObjectId('5f1ece6962de5888b3f12eef'), ObjectId('5f1ece9262de5888b3f12ef1'), ObjectId('5f1ecf5362de5888b3f12f04'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f1ed77162de5888b3f12f17'), ObjectId('5f1ed7a562de5888b3f12f1b'), ObjectId('5f1ed7c362de5888b3f12f1d'), ObjectId('5f1ed7ee62de5888b3f12f21'), ObjectId('5f1ed83762de5888b3f12f25'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f1ed90062de5888b3f12f3c'), ObjectId('5f1ed92a62de5888b3f12f40'), ObjectId('5f1ed94062de5888b3f12f42'), ObjectId('5f1ed98b62de5888b3f12f48'), ObjectId('5f1ed9a162de5888b3f12f4a'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('5f1eda3262de5888b3f12f5f'), ObjectId('5f1eda4862de5888b3f12f61')]
# re_fix(re_list)

def get_entries_project(project_id):
    all_entires = []
    completed_count = 0
    incomplete_count = 0
    incompletes = []
    problems = []
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
                all_entires.extend(obs_ids)

                for k in obs_ids:
                    prof_data_entry = profile_col.find({"_id": k})
                    # print('proj', proj_data_entry)
                    prof_data = [i for i in prof_data_entry]
                    prof_attribute_keys = list(prof_data[0].keys())

                    if ('simplified_dump_state' in prof_attribute_keys):
                        if(prof_data[0]['simplified_dump_state']=='Completed'):
                            completed_count+=1
                        # else:print(prof_data[0]['simplified_dump_state'])
                        elif (prof_data[0]['simplified_dump_state'] == 'Incomplete'):
                            incomplete_count+= 1
                            incompletes.append(k)
                        else:
                            problems.append(k)
                    else:
                        problems.append(k)
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

        # all_entires = list(set(all_entires))
        # return all_entires
    else:
        print("This project do not have any queries yet")
        # return []

    print('comp',completed_count)
    print('inc',incomplete_count)
    print('inc',incompletes)
    print('prob',problems)

# print(len(get_entries_project(ObjectId('5f7558e6fce4b64506137661'))))
# csv_exp_s_c(id_list,output_path)





def adding_ig(id_list):

    mycol = refer_collection()
    for id_a in id_list:
        entry = mycol.find({"_id": id_a})
        data = [d for d in entry]
        print(data[0]['_id'])
        mycol.update_one({'_id': id_a}, {'$set': {'ignore_flag': '1'}})
id_lll = [ObjectId("5fe3216aef6c237eaef05804")]

# adding_ig(id_lll)
# print(get_entries_project(ObjectId('5f6d7213c7efa7fb46a2c44a')))
# simplified_update([ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f183dde464603f10dce0da2'), ObjectId('5f183dfe464603f10dce0da4'), ObjectId('5f183e14464603f10dce0da6'), ObjectId('5f183e53464603f10dce0dab'), ObjectId('5f183e89464603f10dce0dae'), ObjectId('5f183e89464603f10dce0dae'), ObjectId('5f183e9d464603f10dce0db0'), ObjectId('5f183eb3464603f10dce0db2'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f183ee7464603f10dce0db6'), ObjectId('5f183efd464603f10dce0db8'), ObjectId('5f183f13464603f10dce0dba'), ObjectId('5f183f28464603f10dce0dbc'), ObjectId('5f186b7cb448d46665f7ff02'), ObjectId('5f18750a182dbb7a59a62642'), ObjectId('5f187522182dbb7a59a62644'), ObjectId('5f187556182dbb7a59a62647'), ObjectId('5f18756b182dbb7a59a62649'), ObjectId('5f187580182dbb7a59a6264b'), ObjectId('5f187595182dbb7a59a6264d'), ObjectId('5f1875c9182dbb7a59a62650'), ObjectId('5f18840a35a2278f64f9e5f2'), ObjectId('5f18841f35a2278f64f9e5f4'), ObjectId('5f18843e35a2278f64f9e5f6'), ObjectId('5f18962935a2278f64f9e647'), ObjectId('5f189e1d35a2278f64f9e676'), ObjectId('5f18ec3135a2278f64f9e6a7'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f18ec7035a2278f64f9e6ac'), ObjectId('5f18ec8435a2278f64f9e6ae'), ObjectId('5f18eca435a2278f64f9e6b0'), ObjectId('5f18ecbb35a2278f64f9e6b2'), ObjectId('5f18ecd035a2278f64f9e6b4'), ObjectId('5f18ece535a2278f64f9e6b6'), ObjectId('5f18ecfa35a2278f64f9e6b8'), ObjectId('5f18ed0f35a2278f64f9e6ba'), ObjectId('5f18ed5035a2278f64f9e6bd'), ObjectId('5f18ed6535a2278f64f9e6bf'), ObjectId('5f18ed8f35a2278f64f9e6ce'), ObjectId('5f19077f5fe76f8f85f401fa'), ObjectId('5f197a573efb8669e251a4f6'), ObjectId('5f197b283efb8669e251a500'), ObjectId('5f19c87c09e1c3c703025666'), ObjectId('5f19c8a709e1c3c70302566a'), ObjectId('5f19c8bc09e1c3c70302566c'), ObjectId('5f19c8f009e1c3c703025670'), ObjectId('5f19c95d09e1c3c70302567a'), ObjectId('5f19c98709e1c3c70302567e'), ObjectId('5f19c9a609e1c3c703025680'), ObjectId('5f19ca3509e1c3c70302568c'), ObjectId('5f19ca4a09e1c3c70302568e'), ObjectId('5f19ca5e09e1c3c703025690'), ObjectId('5f19ca9409e1c3c703025694'), ObjectId('5f19cabe09e1c3c703025698'), ObjectId('5f19d54209e1c3c7030256a9'), ObjectId('5f19d55909e1c3c7030256ab'), ObjectId('5f19d56f09e1c3c7030256ad'), ObjectId('5f19d58409e1c3c7030256af'), ObjectId('5f19d59a09e1c3c7030256b1'), ObjectId('5f19d5af09e1c3c7030256b3'), ObjectId('5f19d61009e1c3c7030256bb'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f19d68709e1c3c7030256c5'), ObjectId('5f19d6b209e1c3c7030256c9'), ObjectId('5f19d6df09e1c3c7030256cd'), ObjectId('5f19d70b09e1c3c7030256d1'), ObjectId('5f19d72109e1c3c7030256d3'), ObjectId('5f19d78d09e1c3c7030256dd'), ObjectId('5f1e94db027fb1582fb3874a'), ObjectId('5f1e9574027fb1582fb38758'), ObjectId('5f1e997862de5888b3f12e3e'), ObjectId('5f1e99ee62de5888b3f12e46'), ObjectId('5f1e9be462de5888b3f12e5b'), ObjectId('5f1e9c3b62de5888b3f12e63'), ObjectId('5f1e9cb062de5888b3f12e6d'), ObjectId('5f1eac7f62de5888b3f12ea3'), ObjectId('5f1eacf362de5888b3f12ea7'), ObjectId('5f1ead1d62de5888b3f12eab'), ObjectId('5f1ead5462de5888b3f12eaf'), ObjectId('5f1eadd362de5888b3f12eb3'), ObjectId('5f1eae8662de5888b3f12ec8'), ObjectId('5f1eaef362de5888b3f12ed2'), ObjectId('5f1ecdec62de5888b3f12ee7'), ObjectId('5f1ece0162de5888b3f12ee9'), ObjectId('5f1ece2062de5888b3f12eeb'), ObjectId('5f1ece6962de5888b3f12eef'), ObjectId('5f1ece9262de5888b3f12ef1'), ObjectId('5f1ecf5362de5888b3f12f04'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f1ed77162de5888b3f12f17'), ObjectId('5f1ed7a562de5888b3f12f1b'), ObjectId('5f1ed7c362de5888b3f12f1d'), ObjectId('5f1ed7ee62de5888b3f12f21'), ObjectId('5f1ed83762de5888b3f12f25'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f1ed90062de5888b3f12f3c'), ObjectId('5f1ed92a62de5888b3f12f40'), ObjectId('5f1ed94062de5888b3f12f42'), ObjectId('5f1ed98b62de5888b3f12f48'), ObjectId('5f1ed9a162de5888b3f12f4a'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('5f1eda3262de5888b3f12f5f'), ObjectId('5f1eda4862de5888b3f12f61')]
# )
# check_ids([ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f183dde464603f10dce0da2'), ObjectId('5f183dfe464603f10dce0da4'), ObjectId('5f183e14464603f10dce0da6'), ObjectId('5f183e53464603f10dce0dab'), ObjectId('5f183e89464603f10dce0dae'), ObjectId('5f183e9d464603f10dce0db0'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f183f13464603f10dce0dba'), ObjectId('5f183eb3464603f10dce0db2'), ObjectId('5f183f28464603f10dce0dbc'), ObjectId('5f183efd464603f10dce0db8'), ObjectId('5f183ee7464603f10dce0db6'), ObjectId('5f183e29464603f10dce0da8'), ObjectId('5f186b7cb448d46665f7ff02'), ObjectId('5f18750a182dbb7a59a62642'), ObjectId('5f187522182dbb7a59a62644'), ObjectId('5f18756b182dbb7a59a62649'), ObjectId('5f187595182dbb7a59a6264d'), ObjectId('5f1875c9182dbb7a59a62650'), ObjectId('5f187556182dbb7a59a62647'), ObjectId('5f187580182dbb7a59a6264b'), ObjectId('5f18840a35a2278f64f9e5f2'), ObjectId('5f18841f35a2278f64f9e5f4'), ObjectId('5f18843e35a2278f64f9e5f6'), ObjectId('5f18962935a2278f64f9e647'), ObjectId('5f189e1d35a2278f64f9e676'), ObjectId('5f18ed6535a2278f64f9e6bf'), ObjectId('5f18ec3135a2278f64f9e6a7'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f18ec7035a2278f64f9e6ac'), ObjectId('5f18ec8435a2278f64f9e6ae'), ObjectId('5f18eca435a2278f64f9e6b0'), ObjectId('5f18ecbb35a2278f64f9e6b2'), ObjectId('5f18ecd035a2278f64f9e6b4'), ObjectId('5f18ece535a2278f64f9e6b6'), ObjectId('5f18ecfa35a2278f64f9e6b8'), ObjectId('5f18ed0f35a2278f64f9e6ba'), ObjectId('5f18ed5035a2278f64f9e6bd'), ObjectId('5f18ed8f35a2278f64f9e6ce'), ObjectId('5f19077f5fe76f8f85f401fa'), ObjectId('5f197a573efb8669e251a4f6'), ObjectId('5f197b283efb8669e251a500'), ObjectId('5f19c87c09e1c3c703025666'), ObjectId('5f19c8a709e1c3c70302566a'), ObjectId('5f19c95d09e1c3c70302567a'), ObjectId('5f19c9a609e1c3c703025680'), ObjectId('5f19ca3509e1c3c70302568c'), ObjectId('5f19ca4a09e1c3c70302568e'), ObjectId('5f19ca9409e1c3c703025694'), ObjectId('5f19c8f009e1c3c703025670'), ObjectId('5f19cabe09e1c3c703025698'), ObjectId('5f19c8bc09e1c3c70302566c'), ObjectId('5f19c98709e1c3c70302567e'), ObjectId('5f19ca5e09e1c3c703025690'), ObjectId('5f19d55909e1c3c7030256ab'), ObjectId('5f19d58409e1c3c7030256af'), ObjectId('5f19d59a09e1c3c7030256b1'), ObjectId('5f19d5af09e1c3c7030256b3'), ObjectId('5f19d61009e1c3c7030256bb'), ObjectId('5f19d68709e1c3c7030256c5'), ObjectId('5f19d6b209e1c3c7030256c9'), ObjectId('5f19d6df09e1c3c7030256cd'), ObjectId('5f19d72109e1c3c7030256d3'), ObjectId('5f19d56f09e1c3c7030256ad'), ObjectId('5f19d78d09e1c3c7030256dd'), ObjectId('5f19d54209e1c3c7030256a9'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f19d70b09e1c3c7030256d1'), ObjectId('5f1e94db027fb1582fb3874a'), ObjectId('5f1e9574027fb1582fb38758'), ObjectId('5f1e997862de5888b3f12e3e'), ObjectId('5f1e99ee62de5888b3f12e46'), ObjectId('5f1e9be462de5888b3f12e5b'), ObjectId('5f1e9c3b62de5888b3f12e63'), ObjectId('5f1e9cb062de5888b3f12e6d'), ObjectId('5f1eac7f62de5888b3f12ea3'), ObjectId('5f1eacf362de5888b3f12ea7'), ObjectId('5f1ead1d62de5888b3f12eab'), ObjectId('5f1ead5462de5888b3f12eaf'), ObjectId('5f1eadd362de5888b3f12eb3'), ObjectId('5f1eae8662de5888b3f12ec8'), ObjectId('5f1eaef362de5888b3f12ed2'), ObjectId('5f1ecdec62de5888b3f12ee7'), ObjectId('5f1ece0162de5888b3f12ee9'), ObjectId('5f1ece2062de5888b3f12eeb'), ObjectId('5f1ece9262de5888b3f12ef1'), ObjectId('5f1ecf5362de5888b3f12f04'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f1ece6962de5888b3f12eef'), ObjectId('5f1ed77162de5888b3f12f17'), ObjectId('5f1ed7a562de5888b3f12f1b'), ObjectId('5f1ed7c362de5888b3f12f1d'), ObjectId('5f1ed7ee62de5888b3f12f21'), ObjectId('5f1ed83762de5888b3f12f25'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f1ed90062de5888b3f12f3c'), ObjectId('5f1ed9a162de5888b3f12f4a'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('5f1eda3262de5888b3f12f5f'), ObjectId('5f1eda4862de5888b3f12f61'), ObjectId('5f1ed92a62de5888b3f12f40'), ObjectId('5f1ed94062de5888b3f12f42'), ObjectId('5f1ed98b62de5888b3f12f48')]
# )
# all_ids = [ObjectId('5f6436fe8af3a4af8c749ef9'), ObjectId('5f6437128af3a4af8c749efb'), ObjectId('5f6437328af3a4af8c749efd'), ObjectId('5f6437528af3a4af8c749eff'), ObjectId('5f6437688af3a4af8c749f01'), ObjectId('5f645f754c677bfa552c5bd2'), ObjectId('5f645f944c677bfa552c5bd4'), ObjectId('5f645fe04c677bfa552c5be2'), ObjectId('5f6460134c677bfa552c5be5'), ObjectId('5f6460344c677bfa552c5be7'), ObjectId('5f646d804c677bfa552c5bf5'), ObjectId('5f646d9f4c677bfa552c5bf7'), ObjectId('5f646db54c677bfa552c5bf9'), ObjectId('5f646dee4c677bfa552c5c07'), ObjectId('5f646e034c677bfa552c5c09'), ObjectId('5f646e194c677bfa552c5c0b'), ObjectId('5f682551a7cef498a185c2a4'), ObjectId('5f682585a7cef498a185c2a6'), ObjectId('5f68359a9d6d5b0536dfd377'), ObjectId('5f6835ba9d6d5b0536dfd379'), ObjectId('5f6835da9d6d5b0536dfd37b'), ObjectId('5f6835fa9d6d5b0536dfd37d'), ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f183dde464603f10dce0da2'), ObjectId('5f183dfe464603f10dce0da4'), ObjectId('5f183e14464603f10dce0da6'), ObjectId('5f183e29464603f10dce0da8'), ObjectId('5f183e53464603f10dce0dab'), ObjectId('5f183e89464603f10dce0dae'), ObjectId('5f183e9d464603f10dce0db0'), ObjectId('5f183eb3464603f10dce0db2'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f183ee7464603f10dce0db6'), ObjectId('5f183efd464603f10dce0db8'), ObjectId('5f183f13464603f10dce0dba'), ObjectId('5f183f28464603f10dce0dbc'), ObjectId('5f186b7cb448d46665f7ff02'), ObjectId('5f18750a182dbb7a59a62642'), ObjectId('5f187522182dbb7a59a62644'), ObjectId('5f187556182dbb7a59a62647'), ObjectId('5f18756b182dbb7a59a62649'), ObjectId('5f187580182dbb7a59a6264b'), ObjectId('5f187595182dbb7a59a6264d'), ObjectId('5f1875c9182dbb7a59a62650'), ObjectId('5f18840a35a2278f64f9e5f2'), ObjectId('5f18841f35a2278f64f9e5f4'), ObjectId('5f18843e35a2278f64f9e5f6'), ObjectId('5f18962935a2278f64f9e647'), ObjectId('5f189e1d35a2278f64f9e676'), ObjectId('5f18ec3135a2278f64f9e6a7'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f18ec7035a2278f64f9e6ac'), ObjectId('5f18ec8435a2278f64f9e6ae'), ObjectId('5f18eca435a2278f64f9e6b0'), ObjectId('5f18ecbb35a2278f64f9e6b2'), ObjectId('5f18ecd035a2278f64f9e6b4'), ObjectId('5f18ece535a2278f64f9e6b6'), ObjectId('5f18ecfa35a2278f64f9e6b8'), ObjectId('5f18ed0f35a2278f64f9e6ba'), ObjectId('5f18ed5035a2278f64f9e6bd'), ObjectId('5f18ed6535a2278f64f9e6bf'), ObjectId('5f18ed8f35a2278f64f9e6ce'), ObjectId('5f19077f5fe76f8f85f401fa'), ObjectId('5f197a573efb8669e251a4f6'), ObjectId('5f197b283efb8669e251a500'), ObjectId('5f19c87c09e1c3c703025666'), ObjectId('5f19c8a709e1c3c70302566a'), ObjectId('5f19c8bc09e1c3c70302566c'), ObjectId('5f19c8f009e1c3c703025670'), ObjectId('5f19c95d09e1c3c70302567a'), ObjectId('5f19c98709e1c3c70302567e'), ObjectId('5f19c9a609e1c3c703025680'), ObjectId('5f19ca3509e1c3c70302568c'), ObjectId('5f19ca4a09e1c3c70302568e'), ObjectId('5f19ca5e09e1c3c703025690'), ObjectId('5f19ca9409e1c3c703025694'), ObjectId('5f19cabe09e1c3c703025698'), ObjectId('5f19d54209e1c3c7030256a9'), ObjectId('5f19d55909e1c3c7030256ab'), ObjectId('5f19d56f09e1c3c7030256ad'), ObjectId('5f19d58409e1c3c7030256af'), ObjectId('5f19d59a09e1c3c7030256b1'), ObjectId('5f19d5af09e1c3c7030256b3'), ObjectId('5f19d61009e1c3c7030256bb'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f19d68709e1c3c7030256c5'), ObjectId('5f19d6b209e1c3c7030256c9'), ObjectId('5f19d6df09e1c3c7030256cd'), ObjectId('5f19d70b09e1c3c7030256d1'), ObjectId('5f19d72109e1c3c7030256d3'), ObjectId('5f19d78d09e1c3c7030256dd'), ObjectId('5f1e94db027fb1582fb3874a'), ObjectId('5f1e9574027fb1582fb38758'), ObjectId('5f1e997862de5888b3f12e3e'), ObjectId('5f1e99ee62de5888b3f12e46'), ObjectId('5f1e9be462de5888b3f12e5b'), ObjectId('5f1e9c3b62de5888b3f12e63'), ObjectId('5f1e9cb062de5888b3f12e6d'), ObjectId('5f1eac7f62de5888b3f12ea3'), ObjectId('5f1eacf362de5888b3f12ea7'), ObjectId('5f1ead1d62de5888b3f12eab'), ObjectId('5f1ead5462de5888b3f12eaf'), ObjectId('5f1eadd362de5888b3f12eb3'), ObjectId('5f1eae8662de5888b3f12ec8'), ObjectId('5f1eaef362de5888b3f12ed2'), ObjectId('5f1ecdec62de5888b3f12ee7'), ObjectId('5f1ece0162de5888b3f12ee9'), ObjectId('5f1ece2062de5888b3f12eeb'), ObjectId('5f1ece6962de5888b3f12eef'), ObjectId('5f1ece9262de5888b3f12ef1'), ObjectId('5f1ecf5362de5888b3f12f04'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f1ed77162de5888b3f12f17'), ObjectId('5f1ed7a562de5888b3f12f1b'), ObjectId('5f1ed7c362de5888b3f12f1d'), ObjectId('5f1ed7ee62de5888b3f12f21'), ObjectId('5f1ed83762de5888b3f12f25'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f1ed90062de5888b3f12f3c'), ObjectId('5f1ed92a62de5888b3f12f40'), ObjectId('5f1ed94062de5888b3f12f42'), ObjectId('5f1ed98b62de5888b3f12f48'), ObjectId('5f1ed9a162de5888b3f12f4a'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('5f1eda3262de5888b3f12f5f'), ObjectId('5f1eda4862de5888b3f12f61'), ObjectId('5f6b551776b9c3d24f773d0a'), ObjectId('5f6b556e76b9c3d24f773d19'), ObjectId('5f6b55b276b9c3d24f773d28'), ObjectId('5f6b55dc76b9c3d24f773d2b'), ObjectId('5f6c4b1978da94daec47bcc3'), ObjectId('5f6db6e97e23326b374cc46d'), ObjectId('5f6db71c7e23326b374cc46f'), ObjectId('5f6db7bc7e23326b374cc472'), ObjectId('5f6db8bf7e23326b374cc490'), ObjectId('5f6dbc147e23326b374cc4d2'), ObjectId('5f6dbc547e23326b374cc4d4'), ObjectId('5f6dbcf37e23326b374cc4e5'), ObjectId('5f6dbd117e23326b374cc4e7'), ObjectId('5f6dbd317e23326b374cc4e9'), ObjectId('5f6ddd5c144e831840676828'), ObjectId('5f6dddb9144e83184067682b'), ObjectId('5f6dddda144e83184067682d'), ObjectId('5f6dde8e144e831840676832'), ObjectId('5f6ddeb6144e831840676834'), ObjectId('5f6ddf0b144e831840676837'), ObjectId('5f6ddf35144e831840676839'), ObjectId('5f6ddf60144e83184067683b'), ObjectId('5f6ddf94144e83184067683d'), ObjectId('5f6ddfb4144e83184067683f'), ObjectId('5f6de01b144e831840676842'), ObjectId('5f6de03a144e831840676844'), ObjectId('5f6de095144e831840676853'), ObjectId('5f6de0e1144e831840676857'), ObjectId('5f6de0f8144e831840676859'), ObjectId('5f6de111144e83184067685b'), ObjectId('5f6de148144e83184067685e'), ObjectId('5f6de160144e831840676860'), ObjectId('5f6de1c3144e831840676864'), ObjectId('5f6de1f6144e831840676867'), ObjectId('5f6de2b2144e83184067686e'), ObjectId('5f6de2d2144e831840676870'), ObjectId('5f6de354144e831840676881'), ObjectId('5f6de383144e831840676884'), ObjectId('5f6de541144e831840676892'), ObjectId('5f6de5dc144e8318406768a4'), ObjectId('5f6de61d144e8318406768a8'), ObjectId('5f6de658144e8318406768ab'), ObjectId('5f6de715144e8318406768b3'), ObjectId('5f6de825144e8318406768bd'), ObjectId('5f6dea93144e8318406768dd'), ObjectId('5f6deb3b144e8318406768e4'), ObjectId('5f6deca7144e8318406768f9'), ObjectId('5f6ded59144e8318406768fe'), ObjectId('5f6deda2144e831840676901'), ObjectId('5f6deec2144e831840676914'), ObjectId('5f6def24144e831840676918'), ObjectId('5f6def4b144e83184067691a'), ObjectId('5f6def7b144e83184067691d'), ObjectId('5f6def95144e83184067691f'), ObjectId('5f6df0b0144e831840676929'), ObjectId('5f6df104144e83184067692c'), ObjectId('5f6df196144e83184067693d'), ObjectId('5f6df1b7144e83184067693f'), ObjectId('5f6df1ee144e831840676941'), ObjectId('5f6df20e144e831840676943'), ObjectId('5f6df244144e831840676946'), ObjectId('5f6df25b144e831840676948'), ObjectId('5f6df275144e83184067694a'), ObjectId('5f6df291144e83184067694c'), ObjectId('5f6df2ff144e831840676950'), ObjectId('5f6f42ee45dea3de8461691f'), ObjectId('5f6f432745dea3de84616921'), ObjectId('5f6f4fcb41c09be1b8045811'), ObjectId('5f6f683b2606fbee80f75246'), ObjectId('5f6f68852606fbee80f75249'), ObjectId('5f6f68a22606fbee80f7524b'), ObjectId('5f6f68bb2606fbee80f7524d'), ObjectId('5f6f68d62606fbee80f7524f'), ObjectId('5f709a5d0269a3cd9caf4fc6'), ObjectId('5f709a870269a3cd9caf4fc8'), ObjectId('5f709ae10269a3cd9caf4fcc'), ObjectId('5f709be90269a3cd9caf4fd4'), ObjectId('5f709c4e0269a3cd9caf4fd8'), ObjectId('5f709ce30269a3cd9caf4fdd'), ObjectId('5f709d0b0269a3cd9caf4fdf'), ObjectId('5f709d930269a3cd9caf4fe4'), ObjectId('5f709dd10269a3cd9caf4fe7'), ObjectId('5f709e1d0269a3cd9caf4fea'), ObjectId('5f709e7a0269a3cd9caf4fed'), ObjectId('5f709ec20269a3cd9caf4ff0'), ObjectId('5f709f0e0269a3cd9caf4ff3'), ObjectId('5f709fa50269a3cd9caf4ff8'), ObjectId('5f709fcd0269a3cd9caf4ffa'), ObjectId('5f70a0520269a3cd9caf4fff'), ObjectId('5f70a1020269a3cd9caf5004'), ObjectId('5f70a1250269a3cd9caf5006'), ObjectId('5f70a1440269a3cd9caf5008'), ObjectId('5f70a1620269a3cd9caf500a'), ObjectId('5f70a1cf0269a3cd9caf500d'), ObjectId('5f70a1ea0269a3cd9caf500f'), ObjectId('5f70a2170269a3cd9caf5011'), ObjectId('5f70a24c0269a3cd9caf5013'), ObjectId('5f70a3470269a3cd9caf5019'), ObjectId('5f70a3990269a3cd9caf501c'), ObjectId('5f70a3ba0269a3cd9caf501e'), ObjectId('5f70a4170269a3cd9caf502d'), ObjectId('5f70c3c00269a3cd9caf502f'), ObjectId('5f70c3d90269a3cd9caf5031'), ObjectId('5f70c4b60269a3cd9caf503a'), ObjectId('5f70c5090269a3cd9caf503e'), ObjectId('5f70c52d0269a3cd9caf5040'), ObjectId('5f70c56d0269a3cd9caf5043'), ObjectId('5f70c6050269a3cd9caf5048'), ObjectId('5f70c61e0269a3cd9caf504a'), ObjectId('5f70c65e0269a3cd9caf504d'), ObjectId('5f70c6910269a3cd9caf504f'), ObjectId('5f70c7290269a3cd9caf5054'), ObjectId('5f70c7430269a3cd9caf5056'), ObjectId('5f70c7660269a3cd9caf5058'), ObjectId('5f70c7bf0269a3cd9caf505c'), ObjectId('5f70c7df0269a3cd9caf505e'), ObjectId('5f70c86a0269a3cd9caf5063'), ObjectId('5f70c8970269a3cd9caf5065'), ObjectId('5f70c9480269a3cd9caf506b'), ObjectId('5f70ca3e0269a3cd9caf5074'), ObjectId('5f70ca580269a3cd9caf5076'), ObjectId('5f70ca750269a3cd9caf5078'), ObjectId('5f70ca8e0269a3cd9caf507a'), ObjectId('5f70cb4d0269a3cd9caf5080'), ObjectId('5f70cbb50269a3cd9caf5084'), ObjectId('5f70cbce0269a3cd9caf5086'), ObjectId('5f70cc670269a3cd9caf5098'), ObjectId('5f70cd450269a3cd9caf50a1'), ObjectId('5f70ce2a0269a3cd9caf50a9'), ObjectId('5f70ce780269a3cd9caf50ac'), ObjectId('5f70cf020269a3cd9caf50b1'), ObjectId('5f70d1240269a3cd9caf50c3'), ObjectId('5f70d15e0269a3cd9caf50c6'), ObjectId('5f70d1990269a3cd9caf50c8'), ObjectId('5f70d1ae0269a3cd9caf50ca'), ObjectId('5f70d1db0269a3cd9caf50cd'), ObjectId('5f70d2410269a3cd9caf50d2'), ObjectId('5f70d2f70269a3cd9caf50d9'), ObjectId('5f70d4410269a3cd9caf50f0'), ObjectId('5f70d4600269a3cd9caf50f2'), ObjectId('5f70d60b0269a3cd9caf5101'), ObjectId('5f70d6a70269a3cd9caf5109'), ObjectId('5f70d72b0269a3cd9caf510e'), ObjectId('5f70d7aa0269a3cd9caf5114'), ObjectId('5f70d80d0269a3cd9caf5119'), ObjectId('5f70d8460269a3cd9caf511c'), ObjectId('5f70d8a00269a3cd9caf5120'), ObjectId('5f70d9100269a3cd9caf5124'), ObjectId('5f70d9270269a3cd9caf5126'), ObjectId('5f70d93d0269a3cd9caf5128'), ObjectId('5f70db280269a3cd9caf5138'), ObjectId('5f70dcd50269a3cd9caf5152'), ObjectId('5f70de1d0269a3cd9caf515e'), ObjectId('5f70dfe00269a3cd9caf516d'), ObjectId('5f70e01f0269a3cd9caf5170'), ObjectId('5f70e08a0269a3cd9caf5175'), ObjectId('5f70e1130269a3cd9caf517b'), ObjectId('5f70e12b0269a3cd9caf517d'), ObjectId('5f70e16f0269a3cd9caf5180'), ObjectId('5f70e2160269a3cd9caf5187'), ObjectId('5f70e2560269a3cd9caf518a'), ObjectId('5f70e2c60269a3cd9caf518e'), ObjectId('5f70e3730269a3cd9caf5195'), ObjectId('5f70e3ae0269a3cd9caf5198'), ObjectId('5f70e3dd0269a3cd9caf519a'), ObjectId('5f70e4a30269a3cd9caf51a2'), ObjectId('5f70e52a0269a3cd9caf51b4'), ObjectId('5f70e5400269a3cd9caf51b6'), ObjectId('5f70e5dd0269a3cd9caf51bd'), ObjectId('5f70e6770269a3cd9caf51c3'), ObjectId('5f70e74f0269a3cd9caf51cc'), ObjectId('5f70e7b40269a3cd9caf51d1'), ObjectId('5f70e85b0269a3cd9caf51d9'), ObjectId('5f70e9d60269a3cd9caf51e7'), ObjectId('5f70ea2d0269a3cd9caf51eb'), ObjectId('5f70ebbb0269a3cd9caf51f7'), ObjectId('5f70ebf00269a3cd9caf51f9'), ObjectId('5f70ec280269a3cd9caf51fc'), ObjectId('5f70ec530269a3cd9caf51fe'), ObjectId('5f70ecff0269a3cd9caf5211'), ObjectId('5f70ed210269a3cd9caf5213'), ObjectId('5f70eda40269a3cd9caf5217'), ObjectId('5f70edd90269a3cd9caf5219'), ObjectId('5f70ef740269a3cd9caf5228'), ObjectId('5f70ef8d0269a3cd9caf522a'), ObjectId('5f70efbe0269a3cd9caf522c'), ObjectId('5f70f02b0269a3cd9caf5231'), ObjectId('5f70f1180269a3cd9caf523a'), ObjectId('5f70f16c0269a3cd9caf523e'), ObjectId('5f70f1840269a3cd9caf5240'), ObjectId('5f70f2510269a3cd9caf5249'), ObjectId('5f70f28c0269a3cd9caf524c'), ObjectId('5f70f2c20269a3cd9caf524e'), ObjectId('5f70f3280269a3cd9caf5252'), ObjectId('5f70f3480269a3cd9caf5254'), ObjectId('5f70f3d80269a3cd9caf5259'), ObjectId('5f70f3f10269a3cd9caf525b'), ObjectId('5f70f4090269a3cd9caf525d'), ObjectId('5f70f4210269a3cd9caf525f'), ObjectId('5f70f4490269a3cd9caf5261'), ObjectId('5f70f4b60269a3cd9caf5266'), ObjectId('5f70f5590269a3cd9caf5278'), ObjectId('5f70f58d0269a3cd9caf527b'), ObjectId('5f70f5a20269a3cd9caf527d'), ObjectId('5f70f5c10269a3cd9caf527f'), ObjectId('5f70f6270269a3cd9caf5283'), ObjectId('5f70f6820269a3cd9caf5287'), ObjectId('5f70f7340269a3cd9caf528e'), ObjectId('5f70f74c0269a3cd9caf5290'), ObjectId('5f70f7c80269a3cd9caf5294'), ObjectId('5f70f8830269a3cd9caf529b'), ObjectId('5f70f8e20269a3cd9caf529f'), ObjectId('5f70f8f90269a3cd9caf52a1'), ObjectId('5f70f9330269a3cd9caf52a4'), ObjectId('5f70f94d0269a3cd9caf52a6'), ObjectId('5f70f9640269a3cd9caf52a8'), ObjectId('5f70f9910269a3cd9caf52ab'), ObjectId('5f70fa840269a3cd9caf52b5'), ObjectId('5f70fac70269a3cd9caf52b8'), ObjectId('5f70fb380269a3cd9caf52bc'), ObjectId('5f70fb8c0269a3cd9caf52bf'), ObjectId('5f70fba60269a3cd9caf52c1'), ObjectId('5f70fbd30269a3cd9caf52c3'), ObjectId('5f70fc260269a3cd9caf52c6'), ObjectId('5f70fc3d0269a3cd9caf52c8'), ObjectId('5f70fc760269a3cd9caf52cb')]
# # adding_ig(all_ids)
# # simplified_update([ObjectId('5f183e29464603f10dce0da8')])
# assets= [ObjectId('5f76ec8f087161005148ece3'), ObjectId('5f76cb2b087161005148eb9f'), ObjectId('5f6437688af3a4af8c749f01'), ObjectId('5f76c4b1087161005148eb6b'), ObjectId('5f76e7ac087161005148eca9'), ObjectId('5f76e7fe087161005148ecad'), ObjectId('5f76e69a087161005148eca0'), ObjectId('5f76d1f0087161005148ebe0'), ObjectId('5f76d1a1087161005148ebdc'), ObjectId('5f76f8be087161005148ed47'), ObjectId('5f759f47087161005148e8c9'), ObjectId('5f76d14d087161005148ebd8'), ObjectId('5f70d93d0269a3cd9caf5128'), ObjectId('5f76df57087161005148ec60'), ObjectId('5f76f5f1087161005148ed31'), ObjectId('5f76f854087161005148ed44'), ObjectId('5f76b30c087161005148eaea'), ObjectId('5f75b8b5087161005148e9bf'), ObjectId('5f76b114087161005148eae1'), ObjectId('5f76dec8087161005148ec5c'), ObjectId('5f76f487087161005148ed24'), ObjectId('5f70ca3e0269a3cd9caf5074'), ObjectId('5f76f633087161005148ed33'), ObjectId('5f76c0f5087161005148eb4f'), ObjectId('5f7701de087161005148ed85'), ObjectId('5f76e417087161005148ec8a'), ObjectId('5f76b472087161005148eaf2'), ObjectId('5f76dafc087161005148ec35'), ObjectId('5f19d55909e1c3c7030256ab'), ObjectId('5f76d28e087161005148ebe6'), ObjectId('5f76dea4087161005148ec5a'), ObjectId('5f76edca087161005148ecee'), ObjectId('5f68359a9d6d5b0536dfd377'), ObjectId('5f19c8f009e1c3c703025670'), ObjectId('5f76e265087161005148ec7c'), ObjectId('5f76ecb8087161005148ece5'), ObjectId('5f6835fa9d6d5b0536dfd37d'), ObjectId('5f76c486087161005148eb69'), ObjectId('5f76cf06087161005148ebc8'), ObjectId('5f770a5b087161005148edbf'), ObjectId('5f758107087161005148e7b5'), ObjectId('5f76ec3e087161005148ece0'), ObjectId('5f76e5a4087161005148ec97'), ObjectId('5f76c428087161005148eb66'), ObjectId('5f76a470087161005148eaa6'), ObjectId('5f770236087161005148ed89'), ObjectId('5f76db20087161005148ec37'), ObjectId('5f76e0fb087161005148ec6f'), ObjectId('5f76e1a8087161005148ec77'), ObjectId('5f76b342087161005148eaec'), ObjectId('5f76cbc6087161005148eba4'), ObjectId('5f76ec10087161005148ecde'), ObjectId('5f76e290087161005148ec7e'), ObjectId('5f76d79b087161005148ec0e'), ObjectId('5f76ef07087161005148ecfa'), ObjectId('5f76a332087161005148ea9f'), ObjectId('5f76e042087161005148ec68'), ObjectId('5f75bb46087161005148e9d3'), ObjectId('5f75684c087161005148e6b3'), ObjectId('5f75b696087161005148e9af'), ObjectId('5f76f3dd087161005148ed20'), ObjectId('5f75a410087161005148e8ef'), ObjectId('5f76ae75087161005148ead1'), ObjectId('5f6835ba9d6d5b0536dfd379'), ObjectId('5f758438087161005148e7d2'), ObjectId('5f76bac7087161005148eb18'), ObjectId('5f76efb0087161005148ed00'), ObjectId('5f76d9bf087161005148ec1f'), ObjectId('5f76bb08087161005148eb1a'), ObjectId('5f76e891087161005148ecb4'), ObjectId('5f76bec1087161005148eb3c'), ObjectId('5f76ce73087161005148ebc3'), ObjectId('5f76f010087161005148ed03'), ObjectId('5f76e016087161005148ec66'), ObjectId('5f76ee87087161005148ecf4'), ObjectId('5f6437528af3a4af8c749eff'), ObjectId('5f76b0d3087161005148eadf'), ObjectId('5f76bc7b087161005148eb2e'), ObjectId('5f75ab4b087161005148e93f'), ObjectId('5f76a714087161005148eab4'), ObjectId('5f757af0087161005148e76f'), ObjectId('5f75b835087161005148e9ba'), ObjectId('5f75a551087161005148e904'), ObjectId('5f76c1ed087161005148eb55'), ObjectId('5f76eead087161005148ecf6'), ObjectId('5f76d6df087161005148ec08'), ObjectId('5f76fd8c087161005148ed6b'), ObjectId('5f76c830087161005148eb87'), ObjectId('5f76c939087161005148eb8e'), ObjectId('5f75bc04087161005148e9da'), ObjectId('5f76d603087161005148ebff'), ObjectId('5f76af76087161005148ead7'), ObjectId('5f76adda087161005148eace'), ObjectId('5f76b8b2087161005148eb0c'), ObjectId('5f75a954087161005148e92c'), ObjectId('5f76cfae087161005148ebcd'), ObjectId('5f76e0ab087161005148ec6c'), ObjectId('5f76e15d087161005148ec73'), ObjectId('5f76d3c4087161005148ebef'), ObjectId('5f76e949087161005148ecba'), ObjectId('5f76eb43087161005148ecd7'), ObjectId('5f76f104087161005148ed0c'), ObjectId('5f770a2f087161005148edbd'), ObjectId('5f76f28f087161005148ed16'), ObjectId('5f75ae6b087161005148e958'), ObjectId('5f76db77087161005148ec3a'), ObjectId('5f76b70a087161005148eb01'), ObjectId('5f76ba22087161005148eb14'), ObjectId('5f76a522087161005148eaaa'), ObjectId('5f76e8f5087161005148ecb7'), ObjectId('5f76eeda087161005148ecf8'), ObjectId('5f76e7d8087161005148ecab'), ObjectId('5f76e49a087161005148ec8f'), ObjectId('5f75bb1c087161005148e9d1'), ObjectId('5f19ca5e09e1c3c703025690'), ObjectId('5f76ed74087161005148ecea'), ObjectId('5f76f225087161005148ed13'), ObjectId('5f76de1a087161005148ec56'), ObjectId('5f76f353087161005148ed1c'), ObjectId('5f76f767087161005148ed3b'), ObjectId('5f76bf47087161005148eb40'), ObjectId('5f76da03087161005148ec22'), ObjectId('5f76d174087161005148ebda'), ObjectId('5f76e642087161005148ec9d'), ObjectId('5f76d35f087161005148ebec'), ObjectId('5f76e3e8087161005148ec88'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('5f7705ce087161005148ed9f'), ObjectId('5f7582bc087161005148e7c3'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f75b34b087161005148e988'), ObjectId('5f70c86a0269a3cd9caf5063'), ObjectId('5f76c9fe087161005148eb96'), ObjectId('5f76b99a087161005148eb10'), ObjectId('5f76f58d087161005148ed2f'), ObjectId('5f76f15f087161005148ed0f'), ObjectId('5f76ece4087161005148ece7'), ObjectId('5f76f544087161005148ed2b'), ObjectId('5f76c30a087161005148eb5d'), ObjectId('5f76f6be087161005148ed36'), ObjectId('5f709be90269a3cd9caf4fd4'), ObjectId('5f76cae4087161005148eb9d'), ObjectId('5f70c7df0269a3cd9caf505e'), ObjectId('5f757a68087161005148e76a'), ObjectId('5f76dc20087161005148ec40'), ObjectId('5f76e9fc087161005148eccb'), ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f76e3b2087161005148ec86'), ObjectId('5f76ab3b087161005148eac4'), ObjectId('5f76e844087161005148ecb1'), ObjectId('5f76d717087161005148ec0a'), ObjectId('5f76cb54087161005148eba1'), ObjectId('5f75893f087161005148e800'), ObjectId('5f76df82087161005148ec62'), ObjectId('5f76d060087161005148ebd2'), ObjectId('5f76e5f0087161005148ec99'), ObjectId('5f70d60b0269a3cd9caf5101'), ObjectId('5f76c572087161005148eb71'), ObjectId('5f76d1c4087161005148ebde'), ObjectId('5f7577b0087161005148e74f'), ObjectId('5f76ce4f087161005148ebc1'), ObjectId('5f76e454087161005148ec8c'), ObjectId('5f76c18d087161005148eb52'), ObjectId('5f76ea22087161005148eccd'), ObjectId('5f76eda5087161005148ecec'), ObjectId('5f76bb54087161005148eb1c'), ObjectId('5f76ddfe087161005148ec54'), ObjectId('5f1ecf5362de5888b3f12f04'), ObjectId('5f76d65e087161005148ec03'), ObjectId('5f76b9dd087161005148eb12'), ObjectId('5f76b749087161005148eb03'), ObjectId('5f76bf6e087161005148eb42'), ObjectId('5f770534087161005148ed9a'), ObjectId('5f76da81087161005148ec31'), ObjectId('5f76ee12087161005148ecf0'), ObjectId('5f76b61c087161005148eafb'), ObjectId('5f770688087161005148eda5'), ObjectId('5f76e33b087161005148ec82'), ObjectId('5f76bd6c087161005148eb32'), ObjectId('5f76e6f1087161005148eca3'), ObjectId('5f19d59a09e1c3c7030256b1'), ObjectId('5f77086d087161005148edb1'), ObjectId('5f76d6af087161005148ec06'), ObjectId('5f6de2d2144e831840676870'), ObjectId('5f76aea8087161005148ead3'), ObjectId('5f76f323087161005148ed1a'), ObjectId('5f76dc89087161005148ec44'), ObjectId('5f76ebea087161005148ecdc'), ObjectId('5f76d919087161005148ec19'), ObjectId('5f76e99d087161005148ecc8'), ObjectId('5f76c35c087161005148eb60'), ObjectId('5f76f7ba087161005148ed3f'), ObjectId('5f76c062087161005148eb4b'), ObjectId('5f76ff6d087161005148ed75'), ObjectId('5f76afdb087161005148ead9'), ObjectId('5f709ec20269a3cd9caf4ff0'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f76a7ca087161005148eab7'), ObjectId('5f76a58e087161005148eaae'), ObjectId('5f76b698087161005148eafe'), ObjectId('5f76af3b087161005148ead5'), ObjectId('5f75bbcf087161005148e9d8'), ObjectId('5f76d4c5087161005148ebf7'), ObjectId('5f76d82f087161005148ec12'), ObjectId('5f76f03b087161005148ed05'), ObjectId('5f76bbc6087161005148eb1f'), ObjectId('5f76f56b087161005148ed2d'), ObjectId('5f76f908087161005148ed49'), ObjectId('5f76c03d087161005148eb49'), ObjectId('5f76cd00087161005148ebba'), ObjectId('5f77016e087161005148ed81'), ObjectId('5f76bd93087161005148eb34'), ObjectId('5f76f78d087161005148ed3d'), ObjectId('5f75b5ac087161005148e9a2'), ObjectId('5f76c773087161005148eb81'), ObjectId('5f76ceb7087161005148ebc5'), ObjectId('5f76d895087161005148ec15'), ObjectId('5f76eb1b087161005148ecd5'), ObjectId('5f75983d087161005148e88e'), ObjectId('5f76b04d087161005148eadb'), ObjectId('5f76b82d087161005148eb08'), ObjectId('5f76bf94087161005148eb44'), ObjectId('5f76c6c6087161005148eb7c'), ObjectId('5f76c7a4087161005148eb83'), ObjectId('5f76b878087161005148eb0a'), ObjectId('5f76d632087161005148ec01'), ObjectId('5f76dcf2087161005148ec49'), ObjectId('5f76f4e2087161005148ed28'), ObjectId('5f76c3b8087161005148eb63'), ObjectId('5f76c988087161005148eb92'), ObjectId('5f76c246087161005148eb58'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f76e12b087161005148ec71'), ObjectId('5f18841f35a2278f64f9e5f4'), ObjectId('5f19d54209e1c3c7030256a9'), ObjectId('5f76b784087161005148eb05'), ObjectId('5f76b20a087161005148eae6'), ObjectId('5f76dde3087161005148ec52'), ObjectId('5f76b08c087161005148eadd'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f76dd3c087161005148ec4c'), ObjectId('5f76d265087161005148ebe4'), ObjectId('5f76ef33087161005148ecfc'), ObjectId('5f76e616087161005148ec9b'), ObjectId('5f770205087161005148ed87'), ObjectId('5f76b5d7087161005148eaf9'), ObjectId('5f76c5be087161005148eb74'), ObjectId('5f76a55d087161005148eaac'), ObjectId('5f75b9c8087161005148e9c6'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f76eaca087161005148ecd2'), ObjectId('5f76ba6c087161005148eb16'), ObjectId('5f756a60087161005148e6c5'), ObjectId('5f76c503087161005148eb6e'), ObjectId('5f76f821087161005148ed42'), ObjectId('5f76cce2087161005148ebb8'), ObjectId('5f76b4b9087161005148eaf4'), ObjectId('5f76d59f087161005148ebfc'), ObjectId('5f76dba7087161005148ec3c'), ObjectId('5f76a8f1087161005148eabd'), ObjectId('5f76b18a087161005148eae3'), ObjectId('5f76dca5087161005148ec46'), ObjectId('5f76e81e087161005148ecaf'), ObjectId('5f76e184087161005148ec75'), ObjectId('5f76ada5087161005148eacc'), ObjectId('5f76e4e9087161005148ec92'), ObjectId('5f76d414087161005148ebf2'), ObjectId('5f76a3b4087161005148eaa2'), ObjectId('5f75b933087161005148e9c2'), ObjectId('5f76e746087161005148eca6'), ObjectId('5f76b4f1087161005148eaf6'), ObjectId('5f76c66d087161005148eb79'), ObjectId('5f76c962087161005148eb90'), ObjectId('5f76d99a087161005148ec1d'), ObjectId('5f19c98709e1c3c70302567e'), ObjectId('5f6ddf0b144e831840676837'), ObjectId('5f76f0c1087161005148ed09'), ObjectId('5f76f4b7087161005148ed26'), ObjectId('5f76e526087161005148ec94')]
# ndis = [ObjectId('5f759112087161005148e847'), ObjectId('5f759644087161005148e872'), ObjectId('5f75b490087161005148e994'), ObjectId('5f75a2c1087161005148e8e4'), ObjectId('5f757b5f087161005148e774'), ObjectId('5f7594c8087161005148e865'), ObjectId('5f757c05087161005148e77c'), ObjectId('5f75ab1e087161005148e93d'), ObjectId('5f757570087161005148e736'), ObjectId('5f757ee2087161005148e794'), ObjectId('5f709ec20269a3cd9caf4ff0'), ObjectId('5f757243087161005148e70d'), ObjectId('5f75751a087161005148e732'), ObjectId('5f758324087161005148e7c5'), ObjectId('5f756b98087161005148e6cf'), ObjectId('5f7574de087161005148e72e'), ObjectId('5f7566da087161005148e6a8'), ObjectId('5f758e08087161005148e82f'), ObjectId('5f756edf087161005148e6eb'), ObjectId('5f757f85087161005148e79a'), ObjectId('5f75a551087161005148e904'), ObjectId('5f756a60087161005148e6c5'), ObjectId('5f75a613087161005148e90d'), ObjectId('5f7569f5087161005148e6c1'), ObjectId('5f758030087161005148e7a1'), ObjectId('5f75ae44087161005148e956'), ObjectId('5f7581ef087161005148e7bb'), ObjectId('5f75bf72087161005148e9fb'), ObjectId('5f75ca29087161005148ea4b'), ObjectId('5f756958087161005148e6bb'), ObjectId('5f7598d6087161005148e897'), ObjectId('5f75b882087161005148e9bd'), ObjectId('5f756cb8087161005148e6d8'), ObjectId('5f756a8c087161005148e6c7'), ObjectId('5f75c020087161005148ea00'), ObjectId('5f75a7e0087161005148e91c'), ObjectId('5f75be3c087161005148e9e7'), ObjectId('5f756708087161005148e6aa'), ObjectId('5f75af0b087161005148e95c'), ObjectId('5f7596ec087161005148e879'), ObjectId('5f758f57087161005148e839'), ObjectId('5f75bbcf087161005148e9d8'), ObjectId('5f759c13087161005148e8b2'), ObjectId('5f75972e087161005148e87c'), ObjectId('5f75c3e6087161005148ea1e'), ObjectId('5f75bb46087161005148e9d3'), ObjectId('5f75b1c7087161005148e97b'), ObjectId('5f75a3ed087161005148e8ed'), ObjectId('5f7592f0087161005148e857'), ObjectId('5f75adcd087161005148e952'), ObjectId('5f75b933087161005148e9c2'), ObjectId('5f757be1087161005148e77a'), ObjectId('5f7586b4087161005148e7ec'), ObjectId('5f75b330087161005148e986'), ObjectId('5f756605087161005148e6a2'), ObjectId('5f75826d087161005148e7bf'), ObjectId('5f759e42087161005148e8c2'), ObjectId('5f75b515087161005148e999'), ObjectId('5f758ab9087161005148e80c'), ObjectId('5f75700e087161005148e6f7'), ObjectId('5f756f45087161005148e6ef'), ObjectId('5f7565b7087161005148e6a0'), ObjectId('5f75c521087161005148ea29'), ObjectId('5f757674087161005148e742'), ObjectId('5f75b8b5087161005148e9bf'), ObjectId('5f757a68087161005148e76a'), ObjectId('5f75a410087161005148e8ef'), ObjectId('5f757857087161005148e758'), ObjectId('5f756c72087161005148e6d6'), ObjectId('5f75b316087161005148e984'), ObjectId('5f759f47087161005148e8c9'), ObjectId('5f75c5fd087161005148ea30'), ObjectId('5f75ab4b087161005148e93f'), ObjectId('5f7564f4087161005148e69c'), ObjectId('5f1ecdec62de5888b3f12ee7'), ObjectId('5f757bb3087161005148e778'), ObjectId('5f6f432745dea3de84616921'), ObjectId('5f75ca53087161005148ea4d'), ObjectId('5f757c4b087161005148e77e'), ObjectId('5f75881d087161005148e7f9'), ObjectId('5f757213087161005148e70b'), ObjectId('5f75bd43087161005148e9e2'), ObjectId('5f757a23087161005148e767'), ObjectId('5f758696087161005148e7ea'), ObjectId('5f758528087161005148e7dc'), ObjectId('5f7585c7087161005148e7e0'), ObjectId('5f7573a7087161005148e71a'), ObjectId('5f75ba51087161005148e9ca'), ObjectId('5f75805f087161005148e7a3'), ObjectId('5f75703c087161005148e6f9'), ObjectId('5f1ece2062de5888b3f12eeb'), ObjectId('5f757309087161005148e715'), ObjectId('5f756bd4087161005148e6d1'), ObjectId('5f758374087161005148e7c9'), ObjectId('5f75ac8e087161005148e949'), ObjectId('5f757e19087161005148e78c'), ObjectId('5f75ad68087161005148e94e'), ObjectId('5f709f0e0269a3cd9caf4ff3'), ObjectId('5f757769087161005148e74c'), ObjectId('5f75a0a1087161005148e8d3'), ObjectId('5f75b7e5087161005148e9b7'), ObjectId('5f756906087161005148e6b9'), ObjectId('5f75c7bc087161005148ea3b'), ObjectId('5f75ca87087161005148ea4f'), ObjectId('5f756f18087161005148e6ed'), ObjectId('5f75961f087161005148e870'), ObjectId('5f7570ff087161005148e701'), ObjectId('5f757e3b087161005148e78e'), ObjectId('5f75af97087161005148e961'), ObjectId('5f7569be087161005148e6bf'), ObjectId('5f75719c087161005148e707'), ObjectId('5f75a22d087161005148e8df'), ObjectId('5f75789a087161005148e75c'), ObjectId('5f757f59087161005148e798'), ObjectId('5f75b249087161005148e97e'), ObjectId('5f759ba5087161005148e8ae'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f758de7087161005148e82d'), ObjectId('5f7575ad087161005148e738'), ObjectId('5f75aa92087161005148e936'), ObjectId('5f756e7b087161005148e6e7'), ObjectId('5f759399087161005148e85b'), ObjectId('5f6dddda144e83184067682d'), ObjectId('5f75c7ec087161005148ea3d'), ObjectId('5f757643087161005148e73e'), ObjectId('5f758c3f087161005148e816'), ObjectId('5f75aafd087161005148e93b'), ObjectId('5f75907d087161005148e843'), ObjectId('5f75a802087161005148e91e'), ObjectId('5f75a18f087161005148e8da'), ObjectId('5f757a01087161005148e765'), ObjectId('5f75adac087161005148e950'), ObjectId('5f7588c3087161005148e7fd'), ObjectId('5f75781d087161005148e754'), ObjectId('5f758676087161005148e7e8'), ObjectId('5f756b59087161005148e6cd'), ObjectId('5f758c67087161005148e818'), ObjectId('5f758780087161005148e7f3'), ObjectId('5f757836087161005148e756'), ObjectId('5f75a485087161005148e8fe'), ObjectId('5f7568cf087161005148e6b7'), ObjectId('5f7593cd087161005148e85d'), ObjectId('5f75bcb7087161005148e9df'), ObjectId('5f70e85b0269a3cd9caf51d9'), ObjectId('5f758dae087161005148e82b'), ObjectId('5f758459087161005148e7d4'), ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f7576bd087161005148e745'), ObjectId('5f75a259087161005148e8e1'), ObjectId('5f70c65e0269a3cd9caf504d'), ObjectId('5f756f79087161005148e6f1'), ObjectId('5f757e71087161005148e790'), ObjectId('5f758419087161005148e7d0'), ObjectId('5f75aab1087161005148e938'), ObjectId('5f75a5cd087161005148e90a'), ObjectId('5f75c979087161005148ea46'), ObjectId('5f758723087161005148e7f1'), ObjectId('5f75b9c8087161005148e9c6'), ObjectId('5f75654d087161005148e69e'), ObjectId('5f75677c087161005148e6ac'), ObjectId('5f75706e087161005148e6fb'), ObjectId('5f75b9f6087161005148e9c8'), ObjectId('5f7598a0087161005148e893'), ObjectId('5f757279087161005148e70f'), ObjectId('5f75aa09087161005148e932'), ObjectId('5f759db2087161005148e8bc'), ObjectId('5f75ab78087161005148e941'), ObjectId('5f757af0087161005148e76f'), ObjectId('5f6de1f6144e831840676867'), ObjectId('5f75749e087161005148e72c'), ObjectId('5f759535087161005148e869'), ObjectId('5f75983d087161005148e88e'), ObjectId('5f19ca4a09e1c3c70302568e'), ObjectId('5f75a745087161005148e918'), ObjectId('5f758299087161005148e7c1'), ObjectId('5f75a982087161005148e92e'), ObjectId('5f758438087161005148e7d2'), ObjectId('5f758006087161005148e79f'), ObjectId('5f759167087161005148e84b'), ObjectId('5f757b3b087161005148e772'), ObjectId('5f75a885087161005148e923'), ObjectId('5f709c4e0269a3cd9caf4fd8'), ObjectId('5f7584c9087161005148e7d8'), ObjectId('5f70ed210269a3cd9caf5213'), ObjectId('5f7571e3087161005148e709'), ObjectId('5f7567de087161005148e6b0'), ObjectId('5f759f9b087161005148e8cc'), ObjectId('5f75bacd087161005148e9cd'), ObjectId('5f75a8c0087161005148e927'), ObjectId('5f757fdb087161005148e79d'), ObjectId('5f75709a087161005148e6fd'), ObjectId('5f758508087161005148e7da'), ObjectId('5f758107087161005148e7b5'), ObjectId('5f75765b087161005148e740'), ObjectId('5f7593fa087161005148e85f'), ObjectId('5f75a82e087161005148e920'), ObjectId('5f75a8de087161005148e929'), ObjectId('5f758962087161005148e802'), ObjectId('5f7583f3087161005148e7ce'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f756eac087161005148e6e9'), ObjectId('5f757545087161005148e734'), ObjectId('5f756984087161005148e6bd'), ObjectId('5f6460344c677bfa552c5be7'), ObjectId('5f757372087161005148e718'), ObjectId('5f75b604087161005148e9a7'), ObjectId('5f7587d8087161005148e7f6'), ObjectId('5f756fd9087161005148e6f5'), ObjectId('5f75b3dd087161005148e98e'), ObjectId('5f75c4d6087161005148ea26'), ObjectId('5f7577b0087161005148e74f'), ObjectId('5f758ae7087161005148e80e'), ObjectId('5f759b5e087161005148e8ab'), ObjectId('5f75c059087161005148ea03'), ObjectId('5f75b67c087161005148e9ad'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f75bc04087161005148e9da'), ObjectId('5f759cc6087161005148e8b6'), ObjectId('5f758b3d087161005148e810'), ObjectId('5f70a3ba0269a3cd9caf501e'), ObjectId('5f70ec280269a3cd9caf51fc'), ObjectId('5f70ca580269a3cd9caf5076'), ObjectId('5f75687a087161005148e6b5'), ObjectId('5f75bb93087161005148e9d6'), ObjectId('5f7570cb087161005148e6ff'), ObjectId('5f75b5ac087161005148e9a2'), ObjectId('5f75787a087161005148e75a'), ObjectId('5f758a6b087161005148e809'), ObjectId('5f757d70087161005148e787'), ObjectId('5f75a954087161005148e92c'), ObjectId('5f682585a7cef498a185c2a6'), ObjectId('5f757733087161005148e749'), ObjectId('5f7574ff087161005148e730'), ObjectId('5f75893f087161005148e800'), ObjectId('5f70f28c0269a3cd9caf524c'), ObjectId('5f7596c5087161005148e877'), ObjectId('5f7583c4087161005148e7cc'), ObjectId('5f756fab087161005148e6f3'), ObjectId('5f75950e087161005148e867'), ObjectId('5f75b58c087161005148e9a0'), ObjectId('5f759df9087161005148e8bf'), ObjectId('5f7591ae087161005148e84d'), ObjectId('5f70cc670269a3cd9caf5098'), ObjectId('5f75a1af087161005148e8dc'), ObjectId('5f75baf3087161005148e9cf'), ObjectId('5f70efbe0269a3cd9caf522c'), ObjectId('5f756e20087161005148e6e3'), ObjectId('5f756a2c087161005148e6c3'), ObjectId('5f1ed7ee62de5888b3f12f21'), ObjectId('5f75966e087161005148e874'), ObjectId('5f75b364087161005148e98a'), ObjectId('5f758f80087161005148e83b'), ObjectId('5f75a8a2087161005148e925'), ObjectId('5f75b34b087161005148e988'), ObjectId('5f75c0d1087161005148ea08'), ObjectId('5f75acfb087161005148e94c'), ObjectId('5f75b620087161005148e9a9'), ObjectId('5f758d50087161005148e828'), ObjectId('5f759fce087161005148e8ce'), ObjectId('5f759281087161005148e854'), ObjectId('5f757ab4087161005148e76d'), ObjectId('5f756c03087161005148e6d3'), ObjectId('5f757f1b087161005148e796'), ObjectId('5f75899f087161005148e804'), ObjectId('5f75958c087161005148e86c'), ObjectId('5f7566ab087161005148e6a6'), ObjectId('5f757136087161005148e703'), ObjectId('5f75b54f087161005148e99c'), ObjectId('5f75c747087161005148ea37'), ObjectId('5f75a340087161005148e8e8'), ObjectId('5f757165087161005148e705'), ObjectId('5f7590d6087161005148e845'), ObjectId('5f758708087161005148e7ef'), ObjectId('5f758648087161005148e7e6'), ObjectId('5f75985d087161005148e890'), ObjectId('5f75b56b087161005148e99e'), ObjectId('5f75c19e087161005148ea0d'), ObjectId('5f758084087161005148e7a5'), ObjectId('5f758b5d087161005148e812'), ObjectId('5f75976e087161005148e87e'), ObjectId('5f758615087161005148e7e4'), ObjectId('5f756deb087161005148e6e1'), ObjectId('5f75834f087161005148e7c7'), ObjectId('5f75b05a087161005148e966'), ObjectId('5f75c417087161005148ea20'), ObjectId('5f75b29a087161005148e980'), ObjectId('5f7582bc087161005148e7c3'), ObjectId('5f75ae6b087161005148e958'), ObjectId('5f756e4d087161005148e6e5'), ObjectId('5f75a578087161005148e906'), ObjectId('5f75b6bb087161005148e9b1'), ObjectId('5f75a5a8087161005148e908'), ObjectId('5f75b835087161005148e9ba'), ObjectId('5f7585eb087161005148e7e2'), ObjectId('5f75c1be087161005148ea0f'), ObjectId('5f75ae03087161005148e954'), ObjectId('5f6437328af3a4af8c749efd'), ObjectId('5f759ac1087161005148e8a5'), ObjectId('5f75a6a9087161005148e913'), ObjectId('5f75684c087161005148e6b3'), ObjectId('5f756d0c087161005148e6da'), ObjectId('5f7591df087161005148e84f'), ObjectId('5f756d41087161005148e6dc'), ObjectId('5f7598bc087161005148e895'), ObjectId('5f75a62f087161005148e90f'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f7567aa087161005148e6ae'), ObjectId('5f757cd7087161005148e782'), ObjectId('5f759137087161005148e849'), ObjectId('5f75746f087161005148e72a'), ObjectId('5f75b5ea087161005148e9a5'), ObjectId('5f758e28087161005148e831'), ObjectId('5f75af75087161005148e95f'), ObjectId('5f7580a4087161005148e7a7'), ObjectId('5f759492087161005148e863'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f75bc63087161005148e9dc'), ObjectId('5f70a2170269a3cd9caf5011'), ObjectId('5f7578da087161005148e75e'), ObjectId('5f757d4e087161005148e785'), ObjectId('5f7572a8087161005148e711'), ObjectId('5f758ee4087161005148e836'), ObjectId('5f757b86087161005148e776'), ObjectId('5f75900c087161005148e840'), ObjectId('5f75bb1c087161005148e9d1'), ObjectId('5f756d76087161005148e6de'), ObjectId('5f756677087161005148e6a4'), ObjectId('5f756abd087161005148e6c9'), ObjectId('5f6db7bc7e23326b374cc472'), ObjectId('5f7572dc087161005148e713'), ObjectId('5f75b696087161005148e9af')]
#
# ids_first = [ObjectId('5f19d55909e1c3c7030256ab'), ObjectId('5f7b937ff5bb1adde1413e72'), ObjectId('5f757733087161005148e749'), ObjectId('5f75b5ac087161005148e9a2'), ObjectId('5f1ed9a162de5888b3f12f4a'), ObjectId('5f18ed5035a2278f64f9e6bd'), ObjectId('5f1ed98b62de5888b3f12f48'), ObjectId('5f7b9e6cf5bb1adde1413f02'), ObjectId('5f7b67aff5bb1adde1413dd3'), ObjectId('5f70a2170269a3cd9caf5011'), ObjectId('5f183f13464603f10dce0dba'), ObjectId('5f6437688af3a4af8c749f01'), ObjectId('5f18ec4635a2278f64f9e6a9'), ObjectId('5f7b66d6f5bb1adde1413dc8'), ObjectId('5f76ea22087161005148eccd'), ObjectId('5f7b8fb5f5bb1adde1413e40'), ObjectId('5f7b9865f5bb1adde1413eb3'), ObjectId('5f645f754c677bfa552c5bd2'), ObjectId('5f76c773087161005148eb81'), ObjectId('5f75b6bb087161005148e9b1'), ObjectId('5f7b902ff5bb1adde1413e45'), ObjectId('5f75983d087161005148e88e'), ObjectId('5f7ba504f5bb1adde1413f5a'), ObjectId('5f758438087161005148e7d2'), ObjectId('5f6835da9d6d5b0536dfd37b'), ObjectId('5f7ba3abf5bb1adde1413f3e'), ObjectId('5f7ba94df5bb1adde1413f7f'), ObjectId('5f19d6df09e1c3c7030256cd'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('5f76ba6c087161005148eb16'), ObjectId('5f758107087161005148e7b5'), ObjectId('5f75893f087161005148e800'), ObjectId('5f645f944c677bfa552c5bd4'), ObjectId('5f7b9241f5bb1adde1413e5f'), ObjectId('5f756abd087161005148e6c9'), ObjectId('5f7bb0fdf5bb1adde1413fcd'), ObjectId('5f19c98709e1c3c70302567e'), ObjectId('5f7ba2baf5bb1adde1413f31'), ObjectId('5f183e14464603f10dce0da6'), ObjectId('5f19c8bc09e1c3c70302566c'), ObjectId('5f76bf47087161005148eb40'), ObjectId('5f7b9276f5bb1adde1413e62'), ObjectId('5f19cabe09e1c3c703025698'), ObjectId('5f770a2f087161005148edbd'), ObjectId('5f1ece2062de5888b3f12eeb'), ObjectId('5f70eda40269a3cd9caf5217'), ObjectId('5f19c87c09e1c3c703025666'), ObjectId('5f7ba0eef5bb1adde1413f19'), ObjectId('5f7baae8f5bb1adde1413f8b'), ObjectId('5f7b64aef5bb1adde1413da9'), ObjectId('5f7ba054f5bb1adde1413f12'), ObjectId('5f7570ff087161005148e701'), ObjectId('5f759cc6087161005148e8b6'), ObjectId('5f19d6b209e1c3c7030256c9'), ObjectId('5f7baff0f5bb1adde1413fc3'), ObjectId('5f76e290087161005148ec7e'), ObjectId('5f7b90d3f5bb1adde1413e4e'), ObjectId('5f7ba204f5bb1adde1413f27'), ObjectId('5f7ba6bff5bb1adde1413f6b'), ObjectId('5f758528087161005148e7dc'), ObjectId('5f6437128af3a4af8c749efb'), ObjectId('5f76d59f087161005148ebfc'), ObjectId('5f7b6409f5bb1adde1413da0'), ObjectId('5f7b6465f5bb1adde1413da6'), ObjectId('5f7592f0087161005148e857'), ObjectId('5f6460344c677bfa552c5be7'), ObjectId('5f7b9d59f5bb1adde1413ef4'), ObjectId('5f75ae6b087161005148e958'), ObjectId('5f7b9db8f5bb1adde1413ef8'), ObjectId('5f6835ba9d6d5b0536dfd379'), ObjectId('5f76b784087161005148eb05'), ObjectId('5f7b69b0f5bb1adde1413dea'), ObjectId('5f76aea8087161005148ead3'), ObjectId('5f7b65fef5bb1adde1413dbc'), ObjectId('5f183efd464603f10dce0db8'), ObjectId('5f1ecdec62de5888b3f12ee7'), ObjectId('5f7b8f0bf5bb1adde1413e37'), ObjectId('5f6f4fcb41c09be1b8045811'), ObjectId('5f1ed7ee62de5888b3f12f21'), ObjectId('5f7b930bf5bb1adde1413e6a'), ObjectId('5f19d59a09e1c3c7030256b1'), ObjectId('5f7b8db4f5bb1adde1413e2b'), ObjectId('5f7b6524f5bb1adde1413db1'), ObjectId('5f7b8d46f5bb1adde1413e27'), ObjectId('5f7b9320f5bb1adde1413e6c'), ObjectId('5f70a3ba0269a3cd9caf501e'), ObjectId('5f7b665af5bb1adde1413dc2'), ObjectId('5f7b8a75f5bb1adde1413dfb'), ObjectId('5f75958c087161005148e86c'), ObjectId('5f7ba776f5bb1adde1413f70'), ObjectId('5f76ee87087161005148ecf4'), ObjectId('5f1eadd362de5888b3f12eb3'), ObjectId('5f7b9e83f5bb1adde1413f04'), ObjectId('5f7ba265f5bb1adde1413f2d'), ObjectId('5f7bb5bef5bb1adde1413fff'), ObjectId('5f7b643df5bb1adde1413da3'), ObjectId('5f7b97a5f5bb1adde1413ea9'), ObjectId('5f7ba617f5bb1adde1413f65'), ObjectId('5f19d5af09e1c3c7030256b3'), ObjectId('5f7ba341f5bb1adde1413f37'), ObjectId('5f76d6df087161005148ec08'), ObjectId('5f77086d087161005148edb1'), ObjectId('5f70c86a0269a3cd9caf5063'), ObjectId('5f7b9b6cf5bb1adde1413ed7'), ObjectId('5f1ed90062de5888b3f12f3c'), ObjectId('5f76ff6d087161005148ed75'), ObjectId('5f7b6854f5bb1adde1413ddc'), ObjectId('5f75719c087161005148e707'), ObjectId('5f7b8b50f5bb1adde1413e0f'), ObjectId('5f7ba21af5bb1adde1413f29'), ObjectId('5f7582bc087161005148e7c3'), ObjectId('5f70ca580269a3cd9caf5076'), ObjectId('5f19d78d09e1c3c7030256dd'), ObjectId('5f7b67e3f5bb1adde1413dd6'), ObjectId('5f7b8c4af5bb1adde1413e1b'), ObjectId('5f76adda087161005148eace'), ObjectId('5f709c4e0269a3cd9caf4fd8'), ObjectId('5f75961f087161005148e870'), ObjectId('5f75b9f6087161005148e9c8'), ObjectId('5f7b8bdff5bb1adde1413e16'), ObjectId('5f7b8c1df5bb1adde1413e19'), ObjectId('5f6437528af3a4af8c749eff'), ObjectId('5f7b9a50f5bb1adde1413ec9'), ObjectId('5f1eaef362de5888b3f12ed2'), ObjectId('5f756a60087161005148e6c5'), ObjectId('5f7b96b6f5bb1adde1413e9d'), ObjectId('5f7ba119f5bb1adde1413f1d'), ObjectId('5f7b9465f5bb1adde1413e85'), ObjectId('5f75881d087161005148e7f9'), ObjectId('5f183d9b464603f10dce0d9e'), ObjectId('5f76bd93087161005148eb34'), ObjectId('5f7bac35f5bb1adde1413f9c'), ObjectId('5f7bac60f5bb1adde1413fa0'), ObjectId('5f75aafd087161005148e93b'), ObjectId('5f7ba5c7f5bb1adde1413f62'), ObjectId('5f7bb407f5bb1adde1413feb'), ObjectId('5f19d54209e1c3c7030256a9'), ObjectId('5f76f4b7087161005148ed26'), ObjectId('5f19d65209e1c3c7030256c1'), ObjectId('5f7b9b3ff5bb1adde1413ed5'), ObjectId('5f7b9534f5bb1adde1413e8d'), ObjectId('5f75ad68087161005148e94e'), ObjectId('5f757243087161005148e70d'), ObjectId('5f7b68eef5bb1adde1413de2'), ObjectId('5f76f8be087161005148ed47'), ObjectId('5f7ba53df5bb1adde1413f5d'), ObjectId('5f7b8a01f5bb1adde1413df5'), ObjectId('5f19d58409e1c3c7030256af'), ObjectId('5f7b9f38f5bb1adde1413f0b'), ObjectId('5f1ece0162de5888b3f12ee9'), ObjectId('5f7b978ff5bb1adde1413ea7'), ObjectId('5f7b6697f5bb1adde1413dc5'), ObjectId('5f75b56b087161005148e99e'), ObjectId('5f7b928cf5bb1adde1413e64'), ObjectId('5f76a332087161005148ea9f'), ObjectId('5f7bb4faf5bb1adde1413ff6'), ObjectId('5f76a7ca087161005148eab7'), ObjectId('5f18ece535a2278f64f9e6b6'), ObjectId('5f19ca9409e1c3c703025694'), ObjectId('5f76c486087161005148eb69'), ObjectId('5f7b9ed6f5bb1adde1413f07'), ObjectId('5f7b984ef5bb1adde1413eb1'), ObjectId('5f7b69eef5bb1adde1413dee'), ObjectId('5f7bb093f5bb1adde1413fc8'), ObjectId('5f183e89464603f10dce0dae'), ObjectId('5f1e99ee62de5888b3f12e46'), ObjectId('5f7b9e09f5bb1adde1413efc'), ObjectId('5f1ecf5362de5888b3f12f04'), ObjectId('5f7b9215f5bb1adde1413e5b'), ObjectId('5f7b89c4f5bb1adde1413df2'), ObjectId('5f6de160144e831840676860'), ObjectId('5f75bb46087161005148e9d3'), ObjectId('5f7babdff5bb1adde1413f97'), ObjectId('5f76c5be087161005148eb74'), ObjectId('5f19d70b09e1c3c7030256d1'), ObjectId('5f7b94c8f5bb1adde1413e89'), ObjectId('5f19ca5e09e1c3c703025690'), ObjectId('5f7b960cf5bb1adde1413e98'), ObjectId('5f183dde464603f10dce0da2'), ObjectId('5f7bac4af5bb1adde1413f9e'), ObjectId('5f70d60b0269a3cd9caf5101'), ObjectId('5f7bb593f5bb1adde1413ffd'), ObjectId('5f1ecf8662de5888b3f12f06'), ObjectId('5f709be90269a3cd9caf4fd4'), ObjectId('5f70fa840269a3cd9caf52b5'), ObjectId('5f7b8b9ef5bb1adde1413e13'), ObjectId('5f7ba3ebf5bb1adde1413f43'), ObjectId('5f7b9070f5bb1adde1413e48'), ObjectId('5f18eca435a2278f64f9e6b0'), ObjectId('5f709f0e0269a3cd9caf4ff3'), ObjectId('5f7ba3c1f5bb1adde1413f40'), ObjectId('5f7b8d02f5bb1adde1413e23'), ObjectId('5f18841f35a2278f64f9e5f4'), ObjectId('5f7b6612f5bb1adde1413dbe'), ObjectId('5f7b9a87f5bb1adde1413ecc'), ObjectId('5f76a470087161005148eaa6'), ObjectId('5f7b8e14f5bb1adde1413e2f'), ObjectId('5f7596c5087161005148e877'), ObjectId('5f7b922bf5bb1adde1413e5d'), ObjectId('5f6ddf0b144e831840676837'), ObjectId('5f7ba37ff5bb1adde1413f3b'), ObjectId('5f7ba355f5bb1adde1413f39'), ObjectId('5f758ee4087161005148e836'), ObjectId('5f7b934bf5bb1adde1413e6f'), ObjectId('5f7ba90cf5bb1adde1413f7d'), ObjectId('5f7b980df5bb1adde1413eae'), ObjectId('5f76d174087161005148ebda'), ObjectId('5f19d56f09e1c3c7030256ad'), ObjectId('5f70c65e0269a3cd9caf504d'), ObjectId('5f183e29464603f10dce0da8'), ObjectId('5f75b882087161005148e9bd'), ObjectId('5f1e9cb062de5888b3f12e6d'), ObjectId('5f76c7a4087161005148eb83'), ObjectId('5f7b699cf5bb1adde1413de8'), ObjectId('5f18ec8435a2278f64f9e6ae'), ObjectId('5f7ba85ef5bb1adde1413f77'), ObjectId('5f7bb5f3f5bb1adde1414002'), ObjectId('5f7bab76f5bb1adde1413f92'), ObjectId('5f7b98c6f5bb1adde1413eb8'), ObjectId('5f18750a182dbb7a59a62642'), ObjectId('5f7b9750f5bb1adde1413ea3'), ObjectId('5f7b9f8bf5bb1adde1413f0e'), ObjectId('5f7b692cf5bb1adde1413de5'), ObjectId('5f75684c087161005148e6b3'), ObjectId('5f75b8b5087161005148e9bf'), ObjectId('5f7b95a1f5bb1adde1413e93'), ObjectId('5f7b9abdf5bb1adde1413ecf'), ObjectId('5f7ba190f5bb1adde1413f22'), ObjectId('5f75b696087161005148e9af'), ObjectId('5f7b65a1f5bb1adde1413db8'), ObjectId('5f7b8f95f5bb1adde1413e3e'), ObjectId('5f7572dc087161005148e713'), ObjectId('5f7b9e34f5bb1adde1413eff'), ObjectId('5f7ba73ff5bb1adde1413f6e'), ObjectId('5f75bacd087161005148e9cd'), ObjectId('5f7b8f72f5bb1adde1413e3c'), ObjectId('5f75700e087161005148e6f7'), ObjectId('5f7ba9e0f5bb1adde1413f84'), ObjectId('5f7bab60f5bb1adde1413f90'), ObjectId('5f7bab11f5bb1adde1413f8d'), ObjectId('5f7b8ad9f5bb1adde1413e0a'), ObjectId('5f7b90eaf5bb1adde1413e50'), ObjectId('5f76b82d087161005148eb08'), ObjectId('5f76bf94087161005148eb44'), ObjectId('5f76c4b1087161005148eb6b'), ObjectId('5f7b954df5bb1adde1413e8f'), ObjectId('5f7b9afff5bb1adde1413ed2'), ObjectId('5f1ed8eb62de5888b3f12f3a'), ObjectId('5f7b6503f5bb1adde1413daf'), ObjectId('5f7b90bdf5bb1adde1413e4c'), ObjectId('5f7b8a61f5bb1adde1413df9'), ObjectId('5f7b6754f5bb1adde1413dcf'), ObjectId('5f76d28e087161005148ebe6'), ObjectId('5f75b5ea087161005148e9a5'), ObjectId('5f7b98fdf5bb1adde1413ebc'), ObjectId('5f7ba075f5bb1adde1413f14'), ObjectId('5f1eae8662de5888b3f12ec8'), ObjectId('5f7b6735f5bb1adde1413dcd'), ObjectId('5f7ba66cf5bb1adde1413f68'), ObjectId('5f7ba805f5bb1adde1413f74'), ObjectId('5f7ba4c2f5bb1adde1413f57'), ObjectId('5f7ba104f5bb1adde1413f1b'), ObjectId('5f19ca4a09e1c3c70302568e'), ObjectId('5f7b64c2f5bb1adde1413dab'), ObjectId('5f7b658cf5bb1adde1413db6'), ObjectId('5f7b98dcf5bb1adde1413eba'), ObjectId('5f757e19087161005148e78c'), ObjectId('5f7bb160f5bb1adde1413fd2'), ObjectId('5f7ba40af5bb1adde1413f45'), ObjectId('5f75bbcf087161005148e9d8'), ObjectId('5f75b933087161005148e9c2'), ObjectId('5f7b6820f5bb1adde1413dd9'), ObjectId('5f183ec8464603f10dce0db4'), ObjectId('5f7574de087161005148e72e'), ObjectId('5f682585a7cef498a185c2a6'), ObjectId('5f7bb4c2f5bb1adde1413ff3')]
# simplified_update(ndis)
# add_to_simplified_export_queue(id_lll)
# simplified_export_via_queue()


# get_entries_project(ObjectId('602a9761b480ee114d7db900'))
iiiddd = [ObjectId('602c57ad1a03b37ed3a726cc'), ObjectId('602f7f047ba8308c59e0f48f'), ObjectId('602aff781a03b37ed3a72018'), ObjectId('602e835da4a518be2f97c02c'), ObjectId('602e8a2ca4a518be2f97c057'), ObjectId('602e225da4a518be2f97bddb'), ObjectId('602e283ca4a518be2f97be03'), ObjectId('602e5874a4a518be2f97bf2b'), ObjectId('602f23c27ba8308c59e0f27e'), ObjectId('602e46dda4a518be2f97becb'), ObjectId('602e061ca4a518be2f97bd0b'), ObjectId('602f49497ba8308c59e0f35f'), ObjectId('602e0c25a4a518be2f97bd39'), ObjectId('602e4c9fa4a518be2f97bee7'), ObjectId('602e61c3a4a518be2f97bf5e'), ObjectId('602e1a57a4a518be2f97bdaa'), ObjectId('602f2f527ba8308c59e0f2c9'), ObjectId('602e1175a4a518be2f97bd5f'), ObjectId('602f2c097ba8308c59e0f2b2'), ObjectId('602dd734a62dddfc07249d41'), ObjectId('602f47c27ba8308c59e0f356'), ObjectId('602b20bf1a03b37ed3a720dd'), ObjectId('602f35ef7ba8308c59e0f2f2'), ObjectId('602e1b0da4a518be2f97bdae'), ObjectId('602f2f8c7ba8308c59e0f2cb'), ObjectId('602dd882a62dddfc07249d4a'), ObjectId('602f15f97ba8308c59e0f225'), ObjectId('602c05941a03b37ed3a725c7'), ObjectId('602e0b33a4a518be2f97bd32'), ObjectId('602b4b0a1a03b37ed3a721ee'), ObjectId('602e3de9a4a518be2f97be90'), ObjectId('602e3e8ea4a518be2f97be94'), ObjectId('602e8a6fa4a518be2f97c059'), ObjectId('602f40517ba8308c59e0f32e'), ObjectId('602e0894a4a518be2f97bd1e'), ObjectId('602dd80ca62dddfc07249d46'), ObjectId('602e37f6a4a518be2f97be67'), ObjectId('602f83107ba8308c59e0f4a7'), ObjectId('602e89e9a4a518be2f97c055'), ObjectId('602f75c07ba8308c59e0f466'), ObjectId('602e3a4ca4a518be2f97be7a'), ObjectId('602e0ecaa4a518be2f97bd4d'), ObjectId('602e1364a4a518be2f97bd6f'), ObjectId('602e8441a4a518be2f97c032'), ObjectId('602e68baa4a518be2f97bf8c'), ObjectId('602f26597ba8308c59e0f292'), ObjectId('602e7a8fa4a518be2f97bffa'), ObjectId('602e4ab9a4a518be2f97bedc'), ObjectId('602f21d17ba8308c59e0f272'), ObjectId('602e3785a4a518be2f97be63'), ObjectId('602e2b64a4a518be2f97be19'), ObjectId('602e4301a4a518be2f97beb4'), ObjectId('602f6db07ba8308c59e0f435'), ObjectId('602f94197ba8308c59e0f4f4'), ObjectId('602e2ca7a4a518be2f97be23'), ObjectId('602f5f5c7ba8308c59e0f3e3'), ObjectId('602f67cd7ba8308c59e0f411'), ObjectId('602f23fd7ba8308c59e0f280'), ObjectId('602f3c267ba8308c59e0f31a'), ObjectId('602e58b0a4a518be2f97bf2d'), ObjectId('602e37bda4a518be2f97be65'), ObjectId('602f44787ba8308c59e0f342'), ObjectId('602e525ba4a518be2f97bf0d'), ObjectId('602e3f09a4a518be2f97be98'), ObjectId('602dd6b1a62dddfc07249d3e'), ObjectId('602e5389a4a518be2f97bf14'), ObjectId('602f21237ba8308c59e0f26c'), ObjectId('602e20a3a4a518be2f97bdd2'), ObjectId('602f2d807ba8308c59e0f2bb'), ObjectId('602e7487a4a518be2f97bfd2'), ObjectId('602e2ef5a4a518be2f97be35'), ObjectId('602f72507ba8308c59e0f456'), ObjectId('602aa5e41a03b37ed3a71dfe'), ObjectId('602e0ccba4a518be2f97bd3e'), ObjectId('602e6873a4a518be2f97bf8a'), ObjectId('602f34c27ba8308c59e0f2e9'), ObjectId('602e2e66a4a518be2f97be2e'), ObjectId('602f60627ba8308c59e0f3e9'), ObjectId('602e3596a4a518be2f97be58'), ObjectId('602f2e9e7ba8308c59e0f2c5'), ObjectId('602f4b847ba8308c59e0f36b'), ObjectId('602f5bad7ba8308c59e0f3c9'), ObjectId('602f584d7ba8308c59e0f3b3'), ObjectId('602f31967ba8308c59e0f2d7'), ObjectId('602e82daa4a518be2f97c029'), ObjectId('602e20f4a4a518be2f97bdd4'), ObjectId('602e76b4a4a518be2f97bfdf'), ObjectId('602e1016a4a518be2f97bd56'), ObjectId('602f811a7ba8308c59e0f49c'), ObjectId('602e24bfa4a518be2f97bdea'), ObjectId('602f21967ba8308c59e0f270'), ObjectId('602f2dba7ba8308c59e0f2bd'), ObjectId('602e0fcfa4a518be2f97bd54'), ObjectId('602e7541a4a518be2f97bfd6'), ObjectId('602f7e557ba8308c59e0f48b'), ObjectId('602f21667ba8308c59e0f26e'), ObjectId('602f16ef7ba8308c59e0f22b'), ObjectId('602e5064a4a518be2f97befd'), ObjectId('602e2bb9a4a518be2f97be1b'), ObjectId('602e6b48a4a518be2f97bfa0'), ObjectId('602c2d931a03b37ed3a726b2'), ObjectId('602e07f0a4a518be2f97bd18'), ObjectId('602c0b741a03b37ed3a725e9'), ObjectId('602f19767ba8308c59e0f23e'), ObjectId('602a9ee91a03b37ed3a71dc4'), ObjectId('602e5ee2a4a518be2f97bf4f'), ObjectId('602f7de57ba8308c59e0f487'), ObjectId('602f1d5e7ba8308c59e0f253'), ObjectId('603087b8d17a83ddf637e113'), ObjectId('602e51daa4a518be2f97bf06'), ObjectId('602aa98b1a03b37ed3a71e1a'), ObjectId('602f62b77ba8308c59e0f3f3'), ObjectId('60308069d17a83ddf637e0f4'), ObjectId('602f632f7ba8308c59e0f3f6'), ObjectId('602e3989a4a518be2f97be74'), ObjectId('602f67927ba8308c59e0f40f'), ObjectId('602e5bada4a518be2f97bf3c'), ObjectId('602f51cb7ba8308c59e0f38e'), ObjectId('602e72a8a4a518be2f97bfc4'), ObjectId('602f33a97ba8308c59e0f2e2'), ObjectId('602f2cbc7ba8308c59e0f2b7'), ObjectId('602ab9191a03b37ed3a71e7b'), ObjectId('602f773c7ba8308c59e0f469'), ObjectId('602e66cba4a518be2f97bf7e'), ObjectId('602e25d5a4a518be2f97bdf3'), ObjectId('602e6a28a4a518be2f97bf96'), ObjectId('602f184f7ba8308c59e0f235'), ObjectId('602f82cc7ba8308c59e0f4a5'), ObjectId('602e3feda4a518be2f97be9f'), ObjectId('602f30297ba8308c59e0f2cf'), ObjectId('602e39fba4a518be2f97be78'), ObjectId('602f2e677ba8308c59e0f2c3'), ObjectId('602f85107ba8308c59e0f4b2'), ObjectId('602b2ebc1a03b37ed3a72136'), ObjectId('602e267ca4a518be2f97bdf7'), ObjectId('602e758aa4a518be2f97bfd8'), ObjectId('602e894ea4a518be2f97c050'), ObjectId('602e86afa4a518be2f97c042'), ObjectId('602f238c7ba8308c59e0f27c'), ObjectId('602e5e9ea4a518be2f97bf4d'), ObjectId('602f684a7ba8308c59e0f414'), ObjectId('602e5747a4a518be2f97bf25'), ObjectId('602f64127ba8308c59e0f3fc'), ObjectId('602e12f1a4a518be2f97bd6b'), ObjectId('602b1f9c1a03b37ed3a720d6'), ObjectId('602e0d83a4a518be2f97bd44'), ObjectId('602e245ba4a518be2f97bde7'), ObjectId('602e2c2ba4a518be2f97be1f'), ObjectId('602e4066a4a518be2f97bea3'), ObjectId('602e5d1fa4a518be2f97bf45'), ObjectId('602e17fda4a518be2f97bd94'), ObjectId('602e1281a4a518be2f97bd67'), ObjectId('602f83497ba8308c59e0f4a9'), ObjectId('602e23d8a4a518be2f97bde3'), ObjectId('602f18ca7ba8308c59e0f239'), ObjectId('602e6a98a4a518be2f97bf9a'), ObjectId('602f37127ba8308c59e0f2fa'), ObjectId('602f22097ba8308c59e0f274'), ObjectId('602f1bc77ba8308c59e0f24c'), ObjectId('602e732ea4a518be2f97bfc8'), ObjectId('602f31147ba8308c59e0f2d4'), ObjectId('602e0dc6a4a518be2f97bd46'), ObjectId('602e19a9a4a518be2f97bda0'), ObjectId('602e2bf7a4a518be2f97be1d'), ObjectId('602f9c2c7ba8308c59e0f51f'), ObjectId('60307e3cd17a83ddf637e0ea'), ObjectId('602f364b7ba8308c59e0f2f5'), ObjectId('602e0bb2a4a518be2f97bd35'), ObjectId('602e44b8a4a518be2f97bebe'), ObjectId('602cc8f64512a34739136436'), ObjectId('602f52537ba8308c59e0f391'), ObjectId('60307cb3d17a83ddf637e0e1'), ObjectId('602e16a2a4a518be2f97bd88'), ObjectId('602e6adba4a518be2f97bf9c'), ObjectId('602f7d6d7ba8308c59e0f484'), ObjectId('602e43f2a4a518be2f97beb9'), ObjectId('602e113aa4a518be2f97bd5d'), ObjectId('602f593a7ba8308c59e0f3b9'), ObjectId('602e880aa4a518be2f97c049'), ObjectId('602e11aea4a518be2f97bd61'), ObjectId('602f551c7ba8308c59e0f3a1'), ObjectId('602e4dfba4a518be2f97bef1'), ObjectId('602f69f77ba8308c59e0f420'), ObjectId('602e4c1da4a518be2f97bee4'), ObjectId('602e736aa4a518be2f97bfca'), ObjectId('602e0980a4a518be2f97bd24'), ObjectId('602f368b7ba8308c59e0f2f7'), ObjectId('602e0828a4a518be2f97bd1a'), ObjectId('602f95e97ba8308c59e0f4fd'), ObjectId('602e35dca4a518be2f97be5a'), ObjectId('602e3088a4a518be2f97be3e'), ObjectId('602f16367ba8308c59e0f227'), ObjectId('602f7f387ba8308c59e0f491'), ObjectId('602f468b7ba8308c59e0f34c'), ObjectId('602e4db6a4a518be2f97beef'), ObjectId('602e45efa4a518be2f97bec5'), ObjectId('602e3ec6a4a518be2f97be96'), ObjectId('602e3b00a4a518be2f97be7f'), ObjectId('602e6e44a4a518be2f97bfa9'), ObjectId('602ad8d61a03b37ed3a71f3f'), ObjectId('602e1e1ba4a518be2f97bdc0'), ObjectId('602a9b671a03b37ed3a71da8'), ObjectId('602e4e33a4a518be2f97bef3'), ObjectId('602f4f0f7ba8308c59e0f380'), ObjectId('602f202e7ba8308c59e0f265'), ObjectId('602e30c5a4a518be2f97be40'), ObjectId('602f707e7ba8308c59e0f446'), ObjectId('602f70e87ba8308c59e0f44c'), ObjectId('602e0c96a4a518be2f97bd3c'), ObjectId('602e1781a4a518be2f97bd90'), ObjectId('602e4125a4a518be2f97bea7'), ObjectId('602f6e637ba8308c59e0f43a'), ObjectId('602e52d7a4a518be2f97bf10'), ObjectId('602f694a7ba8308c59e0f41b'), ObjectId('602e14bba4a518be2f97bd7b'), ObjectId('602f71a37ba8308c59e0f450'), ObjectId('602e6bb8a4a518be2f97bfa2'), ObjectId('602e76eda4a518be2f97bfe1'), ObjectId('602e174ba4a518be2f97bd8e'), ObjectId('602e6689a4a518be2f97bf7c'), ObjectId('602f91d37ba8308c59e0f4ea'), ObjectId('602f5b577ba8308c59e0f3c7'), ObjectId('602e0beba4a518be2f97bd37'), ObjectId('602e5fdda4a518be2f97bf55'), ObjectId('602f42347ba8308c59e0f337'), ObjectId('602f1dd57ba8308c59e0f256'), ObjectId('602e13d6a4a518be2f97bd73'), ObjectId('602e1575a4a518be2f97bd80'), ObjectId('602e19d7a4a518be2f97bda2'), ObjectId('602ac84d1a03b37ed3a71edc'), ObjectId('602e722aa4a518be2f97bfc0'), ObjectId('602e7c8da4a518be2f97c005'), ObjectId('602e7feda4a518be2f97c019'), ObjectId('602e16d7a4a518be2f97bd8a'), ObjectId('602f59ac7ba8308c59e0f3bc'), ObjectId('602f56fe7ba8308c59e0f3a9'), ObjectId('602e24f4a4a518be2f97bdec'), ObjectId('602f8ea57ba8308c59e0f4df'), ObjectId('602e352fa4a518be2f97be55'), ObjectId('602f6aee7ba8308c59e0f426'), ObjectId('602e489fa4a518be2f97bed0'), ObjectId('602f69857ba8308c59e0f41d'), ObjectId('602aac631a03b37ed3a71e30'), ObjectId('602e241ca4a518be2f97bde5'), ObjectId('602e3b3ca4a518be2f97be81'), ObjectId('602b47b31a03b37ed3a721d4'), ObjectId('602f3ade7ba8308c59e0f310'), ObjectId('602a9e221a03b37ed3a71dbe'), ObjectId('602e1d67a4a518be2f97bdbb'), ObjectId('602f15447ba8308c59e0f221'), ObjectId('602f6fef7ba8308c59e0f443'), ObjectId('602c13431a03b37ed3a7261b'), ObjectId('602e6551a4a518be2f97bf76'), ObjectId('602f25227ba8308c59e0f289'), ObjectId('602e2533a4a518be2f97bdee'), ObjectId('602b3ee01a03b37ed3a7219c'), ObjectId('602f24e77ba8308c59e0f287'), ObjectId('602f35ae7ba8308c59e0f2f0'), ObjectId('602e6a62a4a518be2f97bf98'), ObjectId('602e70e3a4a518be2f97bfb9'), ObjectId('602e5996a4a518be2f97bf32'), ObjectId('602f1c027ba8308c59e0f24e'), ObjectId('602e3834a4a518be2f97be69'), ObjectId('602e3c3ea4a518be2f97be88'), ObjectId('602f51907ba8308c59e0f38c'), ObjectId('602f25cf7ba8308c59e0f28e'), ObjectId('602e7b65a4a518be2f97bfff'), ObjectId('602e203fa4a518be2f97bdce'), ObjectId('602f2b4c7ba8308c59e0f2ae'), ObjectId('602e1449a4a518be2f97bd77'), ObjectId('602f23547ba8308c59e0f27a'), ObjectId('602e8fcda4a518be2f97c07a'), ObjectId('602f2e327ba8308c59e0f2c1'), ObjectId('602f65007ba8308c59e0f401'), ObjectId('602e275aa4a518be2f97bdfe'), ObjectId('602f7faa7ba8308c59e0f494'), ObjectId('602e1cada4a518be2f97bdb6'), ObjectId('602e4470a4a518be2f97bebc'), ObjectId('602f74c27ba8308c59e0f461'), ObjectId('602e7441a4a518be2f97bfd0'), ObjectId('602f37577ba8308c59e0f2fc'), ObjectId('602f44ce7ba8308c59e0f344'), ObjectId('602e9118a4a518be2f97c082'), ObjectId('602f5e737ba8308c59e0f3db'), ObjectId('602e6fcaa4a518be2f97bfb2'), ObjectId('602e2f77a4a518be2f97be39'), ObjectId('602e287ea4a518be2f97be05'), ObjectId('602e06d0a4a518be2f97bd11'), ObjectId('602e61fca4a518be2f97bf60'), ObjectId('602e6837a4a518be2f97bf88'), ObjectId('602e7e05a4a518be2f97c00f'), ObjectId('602e5e54a4a518be2f97bf4b'), ObjectId('602e8582a4a518be2f97c039'), ObjectId('602e3b80a4a518be2f97be83'), ObjectId('602e2360a4a518be2f97bde0'), ObjectId('602f6f267ba8308c59e0f43f'), ObjectId('602e2ce0a4a518be2f97be25'), ObjectId('602e0860a4a518be2f97bd1c'), ObjectId('602e0695a4a518be2f97bd0f'), ObjectId('602f1a3e7ba8308c59e0f243'), ObjectId('602e7409a4a518be2f97bfce'), ObjectId('602aae191a03b37ed3a71e3b'), ObjectId('602e0f06a4a518be2f97bd4f'), ObjectId('602e3f42a4a518be2f97be9a'), ObjectId('602e792da4a518be2f97bff1'), ObjectId('602aecce1a03b37ed3a71fb3'), ObjectId('602e6806a4a518be2f97bf86'), ObjectId('602e1f64a4a518be2f97bdc8'), ObjectId('602e0e5aa4a518be2f97bd4a'), ObjectId('602e763aa4a518be2f97bfdc'), ObjectId('602f85927ba8308c59e0f4b5'), ObjectId('602e5c6da4a518be2f97bf40'), ObjectId('602e0a30a4a518be2f97bd2a'), ObjectId('602e6436a4a518be2f97bf6e'), ObjectId('602f60277ba8308c59e0f3e7'), ObjectId('602e5557a4a518be2f97bf1c'), ObjectId('602e4be2a4a518be2f97bee2'), ObjectId('602e4998a4a518be2f97bed6'), ObjectId('602aa0c61a03b37ed3a71dd4'), ObjectId('602aa3d11a03b37ed3a71dec'), ObjectId('60307b88d17a83ddf637e0db'), ObjectId('602e065aa4a518be2f97bd0d'), ObjectId('602e4024a4a518be2f97bea1'), ObjectId('602f24a97ba8308c59e0f285'), ObjectId('602e2f2ea4a518be2f97be37'), ObjectId('602f669c7ba8308c59e0f40a'), ObjectId('602e3fb5a4a518be2f97be9d'), ObjectId('602e8670a4a518be2f97c040'), ObjectId('602f18877ba8308c59e0f237'), ObjectId('602f71e07ba8308c59e0f452'), ObjectId('602f381d7ba8308c59e0f300'), ObjectId('602b08a01a03b37ed3a72048'), ObjectId('602e076fa4a518be2f97bd14'), ObjectId('602e4a54a4a518be2f97beda'), ObjectId('60307d58d17a83ddf637e0e5'), ObjectId('602f1e107ba8308c59e0f258'), ObjectId('602e908ea4a518be2f97c07f'), ObjectId('602c86c84512a347391362d9'), ObjectId('602f1ebe7ba8308c59e0f25d')]
iikkk = [ObjectId('6007f32a3814a82c06aaf8d4'), ObjectId('6014de85257797b4df4f69f7'), ObjectId('6006d68fd5de1807a294550d'), ObjectId('6014e159257797b4df4f6a05'), ObjectId('60154d6a0f84134c0183346a'), ObjectId('601656b8e39e130b03b93c65'), ObjectId('6012f18edb453cf448615ff8'), ObjectId('60130055db453cf44861604b'), ObjectId('5faed4bb360efadbf82234ed'), ObjectId('6016655de39e130b03b93cb8'), ObjectId('6006b105d5de1807a294541b'), ObjectId('6006d923d5de1807a294551b'), ObjectId('6012f44ddb453cf44861600b'), ObjectId('6006f835d5de1807a29455bf'), ObjectId('6012718aac544dbb81439d98'), ObjectId('5fb0c24b3ed5000dbe36369d'), ObjectId('5fb168ba11c52f727e4d7cac'), ObjectId('6016500ae39e130b03b93c3a'), ObjectId('6006d9f9d5de1807a2945520'), ObjectId('5f76efb0087161005148ed00'), ObjectId('6007b4ed3814a82c06aaf78a'), ObjectId('6007e5133814a82c06aaf88d'), ObjectId('6012e60bdb453cf448615fb1'), ObjectId('6012ff94db453cf448616046'), ObjectId('5f18841f35a2278f64f9e5f4'), ObjectId('600e378a46a82bde67126f1e'), ObjectId('60164c31e39e130b03b93c23'), ObjectId('6007b55f3814a82c06aaf78e'), ObjectId('600797173814a82c06aaf6d5'), ObjectId('600792ed3814a82c06aaf6b1'), ObjectId('60167231e39e130b03b93ced'), ObjectId('5f757fdb087161005148e79d'), ObjectId('600797923814a82c06aaf6d9'), ObjectId('5fbef0125aa9fb7bcc45b2c5'), ObjectId('601130df117f0109bed4c673'), ObjectId('60069db375b30b32693fd31e'), ObjectId('6016366670de0262f0f86c88'), ObjectId('600807693814a82c06aaf936'), ObjectId('6015319e0f84134c018333ef'), ObjectId('6016187d70de0262f0f86bdb'), ObjectId('60164e81e39e130b03b93c30'), ObjectId('6013008fdb453cf44861604d'), ObjectId('6006f43fd5de1807a29455ae'), ObjectId('6006b70dd5de1807a2945442'), ObjectId('5fc1e14625bc11cafba19c7e'), ObjectId('6012fb01db453cf448616029'), ObjectId('60130111db453cf448616050'), ObjectId('6012fc9adb453cf448616036'), ObjectId('60164a43e39e130b03b93c1a'), ObjectId('6006db1ed5de1807a2945526'), ObjectId('601270cfac544dbb81439d92'), ObjectId('60127241ac544dbb81439d9c'), ObjectId('5faebdeb360efadbf8223476'), ObjectId('5f6de160144e831840676860'), ObjectId('5f756eac087161005148e6e9'), ObjectId('601622f770de0262f0f86c1f'), ObjectId('6012fb75db453cf44861602c'), ObjectId('6012899c9ea5278d02447680'), ObjectId('60126f8cac544dbb81439d8b'), ObjectId('6012f7e9db453cf448616015'), ObjectId('6007f6c73814a82c06aaf8f3'), ObjectId('60154b300f84134c01833460'), ObjectId('5fb1581a11c52f727e4d7c54'), ObjectId('60071f1cd5de1807a29456ac'), ObjectId('60071c60d5de1807a294569b'), ObjectId('6006b1bbd5de1807a2945420'), ObjectId('600707a6d5de1807a2945610'), ObjectId('5fd474852f853dafc3b6604d'), ObjectId('600724dad5de1807a29456cf'), ObjectId('6016292a70de0262f0f86c47'), ObjectId('6007e7f23814a82c06aaf89d'), ObjectId('5f646d9f4c677bfa552c5bf7'), ObjectId('60162f8a70de0262f0f86c65'), ObjectId('5fbfac09ae5bd72e523fe91f'), ObjectId('5f76dd3c087161005148ec4c'), ObjectId('5f756cb8087161005148e6d8'), ObjectId('6006cf5cd5de1807a29454dc'), ObjectId('6007b2803814a82c06aaf77b'), ObjectId('5fae63224dc945e46b4bf0ef'), ObjectId('5f70c65e0269a3cd9caf504d'), ObjectId('5fbfa072ae5bd72e523fe8d6'), ObjectId('6006e7c8d5de1807a2945570'), ObjectId('6006cd5ed5de1807a29454ce'), ObjectId('5f75b9c8087161005148e9c6'), ObjectId('6006f303d5de1807a29455a7'), ObjectId('5fbfa89aae5bd72e523fe911'), ObjectId('5fbf7a40fd5d00ca0885e6a9'), ObjectId('5faf4a8b360efadbf822376b'), ObjectId('6006d4d9d5de1807a2945506'), ObjectId('6006b1e7d5de1807a2945422'), ObjectId('5fb2a72f2bb7c6fe10d26257'), ObjectId('6014e57a257797b4df4f6a1b'), ObjectId('5f70eda40269a3cd9caf5217'), ObjectId('6016197270de0262f0f86be0'), ObjectId('60071075d5de1807a294564b'), ObjectId('6008030e3814a82c06aaf921'), ObjectId('6006b020d5de1807a2945415'), ObjectId('6015529d0f84134c01833482'), ObjectId('6006ca88d5de1807a29454bf'), ObjectId('6006ad3bd5de1807a2945403'), ObjectId('6006bfa3d5de1807a2945477'), ObjectId('5fcf8918d0252312e936bcf2'), ObjectId('6006ebf7d5de1807a2945582'), ObjectId('601549890f84134c01833457'), ObjectId('6015203b0f84134c01833397'), ObjectId('60070b5ad5de1807a2945626'), ObjectId('6012fd8adb453cf44861603b'), ObjectId('60153bfd0f84134c01833419'), ObjectId('6002249757b7b96fc0f16423'), ObjectId('60069e5575b30b32693fd322'), ObjectId('60164caee39e130b03b93c26'), ObjectId('6007f68f3814a82c06aaf8f1'), ObjectId('6007b4a13814a82c06aaf788'), ObjectId('601634f370de0262f0f86c81'), ObjectId('5f91b192f8e3ed277a4a18cd'), ObjectId('5f1ed9fe62de5888b3f12f5b'), ObjectId('60072b98d5de1807a29456f8'), ObjectId('6014e11e257797b4df4f6a03'), ObjectId('60164f9be39e130b03b93c37'), ObjectId('60154a810f84134c0183345c'), ObjectId('601646b5e39e130b03b93c07'), ObjectId('6012f27cdb453cf448615fff'), ObjectId('60126d9bac544dbb81439d7c'), ObjectId('6012f829db453cf448616017'), ObjectId('5f76d895087161005148ec15'), ObjectId('6014dd52257797b4df4f69f1'), ObjectId('600792263814a82c06aaf6ac'), ObjectId('5fbf8237fd5d00ca0885e6d7'), ObjectId('5fff5b91f47d263fe89a8678'), ObjectId('5fb269e92bb7c6fe10d2611f'), ObjectId('60163c3370de0262f0f86caf'), ObjectId('6014d8f6257797b4df4f69dd'), ObjectId('601650c8e39e130b03b93c3f'), ObjectId('5f9153a4f8e3ed277a4a1735'), ObjectId('5fbfa005ae5bd72e523fe8d2'), ObjectId('5fff7702f47d263fe89a8719'), ObjectId('60078fb13814a82c06aaf69d'), ObjectId('5fe3da3630c34b0c88037373'), ObjectId('5f769b79087161005148ea7f'), ObjectId('601621b870de0262f0f86c19'), ObjectId('60069e1275b30b32693fd320'), ObjectId('6006e2dad5de1807a294555c'), ObjectId('6006c7abd5de1807a29454ac'), ObjectId('6006b3ecd5de1807a294542c'), ObjectId('6006b9e0d5de1807a2945451'), ObjectId('60165c41e39e130b03b93c7f'), ObjectId('5f91bc85f8e3ed277a4a191c'), ObjectId('6016179170de0262f0f86bd6'), ObjectId('60069f7f75b30b32693fd32a'), ObjectId('6006ec9dd5de1807a2945586'), ObjectId('5fcfb9056130de0191807181'), ObjectId('5f770a2f087161005148edbd'), ObjectId('6014e32d257797b4df4f6a0f'), ObjectId('5fd3ec1159296cf0a6e7b5be'), ObjectId('6006cb5ad5de1807a29454c2'), ObjectId('601644dae39e130b03b93bfb'), ObjectId('5fc2f801fac3c94429d3ec2f'), ObjectId('5f7b8fb5f5bb1adde1413e40'), ObjectId('60164eb7e39e130b03b93c32'), ObjectId('5fb022523ed5000dbe36331b'), ObjectId('6007ff0a3814a82c06aaf90c'), ObjectId('5faf4123360efadbf822373d'), ObjectId('601662afe39e130b03b93c9d'), ObjectId('601547790f84134c0183344e'), ObjectId('601540350f84134c01833421'), ObjectId('6012f623db453cf448616012'), ObjectId('6016466de39e130b03b93c05'), ObjectId('5f769a66087161005148ea76'), ObjectId('600806453814a82c06aaf930'), ObjectId('60069ce975b30b32693fd318'), ObjectId('6006adfcd5de1807a2945407'), ObjectId('60072529d5de1807a29456d1'), ObjectId('6006c865d5de1807a29454b1'), ObjectId('5faf22b3360efadbf822368d'), ObjectId('5fe29dbfea432c8f124c622f'), ObjectId('6007bc8f3814a82c06aaf7b6'), ObjectId('5fc507cf94eeb38a2dbfb589'), ObjectId('5f91baeff8e3ed277a4a1913'), ObjectId('6006f0d3d5de1807a294559b'), ObjectId('5fe22860ea432c8f124c604a'), ObjectId('601632b770de0262f0f86c76'), ObjectId('6007994c3814a82c06aaf6e1'), ObjectId('60161aca70de0262f0f86be7'), ObjectId('601525440f84134c018333b0'), ObjectId('6006af76d5de1807a2945411'), ObjectId('5fbfb0b9ae5bd72e523fe939'), ObjectId('6007b93f3814a82c06aaf7a5'), ObjectId('6014d38f739557d75a8c638a'), ObjectId('5ffeff14f47d263fe89a8464'), ObjectId('5fe2bc42ef6c237eaef055b0'), ObjectId('601624a670de0262f0f86c26'), ObjectId('6007e8a43814a82c06aaf8a1'), ObjectId('6006f049d5de1807a2945597'), ObjectId('601633aa70de0262f0f86c7a'), ObjectId('5faee293360efadbf822352d'), ObjectId('6016564ce39e130b03b93c62'), ObjectId('5faf5199360efadbf8223799'), ObjectId('6007b5293814a82c06aaf78c'), ObjectId('60071f99d5de1807a29456af'), ObjectId('60161e6b70de0262f0f86bf9'), ObjectId('6016207670de0262f0f86c06'), ObjectId('60161f2970de0262f0f86bfd'), ObjectId('601542930f84134c0183342c'), ObjectId('60162ffc70de0262f0f86c68'), ObjectId('5fb25b5d2bb7c6fe10d260ce'), ObjectId('6007935e3814a82c06aaf6b5'), ObjectId('5fcf8552d0252312e936bcd6'), ObjectId('60072741d5de1807a29456dc'), ObjectId('6015546f0f84134c0183348c'), ObjectId('60164543e39e130b03b93bfe'), ObjectId('60166396e39e130b03b93ca3'), ObjectId('5fcfe2b96130de019180726b'), ObjectId('5f76da03087161005148ec22'), ObjectId('5fd49cb62f853dafc3b66132'), ObjectId('5faf1001360efadbf8223626'), ObjectId('60126cb6ac544dbb81439d75'), ObjectId('6006e13ed5de1807a2945546'), ObjectId('6006c309d5de1807a2945495'), ObjectId('601624e770de0262f0f86c28'), ObjectId('6006e749d5de1807a294556d'), ObjectId('600726c2d5de1807a29456d9'), ObjectId('6016320e70de0262f0f86c72'), ObjectId('6014e7ef257797b4df4f6a2a'), ObjectId('6006dea3d5de1807a2945537'), ObjectId('5fd4539c2f853dafc3b65f86'), ObjectId('6006c28ed5de1807a2945493'), ObjectId('60079d6e3814a82c06aaf6f7'), ObjectId('60126f19ac544dbb81439d87'), ObjectId('60164279e39e130b03b93bed'), ObjectId('601642b1e39e130b03b93bef'), ObjectId('5fe0b44f324548b7323aba9b'), ObjectId('60126f50ac544dbb81439d89'), ObjectId('6012710eac544dbb81439d94'), ObjectId('5f76d632087161005148ec01'), ObjectId('6006f7f9d5de1807a29455bd'), ObjectId('60165f4fe39e130b03b93c8d'), ObjectId('60164d9fe39e130b03b93c2b'), ObjectId('5f76cce2087161005148ebb8'), ObjectId('5fd3916c59296cf0a6e7b3a9'), ObjectId('5fb0ae663ed5000dbe36362e'), ObjectId('60078e0c3814a82c06aaf693'), ObjectId('5fae617b4dc945e46b4bf0da'), ObjectId('5fae136cffaa7d52304bcd9c'), ObjectId('6007f6073814a82c06aaf8e1'), ObjectId('5faeb5bf360efadbf822343a'), ObjectId('5ff2e0172048eab960c81d29'), ObjectId('6007e1023814a82c06aaf86f'), ObjectId('601539290f84134c0183340d'), ObjectId('6006b6cbd5de1807a2945440'), ObjectId('6012e4bbdb453cf448615f9a'), ObjectId('5fd465292f853dafc3b65fed'), ObjectId('6007ea2a3814a82c06aaf8a9'), ObjectId('60127290ac544dbb81439dab'), ObjectId('5fb145c111c52f727e4d7bf4'), ObjectId('6007e6bd3814a82c06aaf896'), ObjectId('6014dba9257797b4df4f69e8'), ObjectId('6016203970de0262f0f86c04'), ObjectId('60151cdf0f84134c01833389'), ObjectId('6012fbebdb453cf448616030'), ObjectId('5fb013753ed5000dbe3632c6'), ObjectId('6014e4f0257797b4df4f6a18'), ObjectId('6006d25ed5de1807a29454f8'), ObjectId('6014e76d257797b4df4f6a26'), ObjectId('5fbf851dfd5d00ca0885e6ea'), ObjectId('60162cc670de0262f0f86c58'), ObjectId('60079b1f3814a82c06aaf6e9'), ObjectId('60126e21ac544dbb81439d80'), ObjectId('5fcefab8d0252312e936b998'), ObjectId('6006af0ad5de1807a294540d'), ObjectId('6006ed8bd5de1807a294558b'), ObjectId('5f7b928cf5bb1adde1413e64'), ObjectId('5fbf0d580e31bd261a165995'), ObjectId('60161c7b70de0262f0f86bf0'), ObjectId('5f769859087161005148ea68'), ObjectId('6006becad5de1807a2945470'), ObjectId('6007b90a3814a82c06aaf7a3'), ObjectId('6012fc28db453cf448616032'), ObjectId('6012f3d8db453cf448616007'), ObjectId('6014e069257797b4df4f69ff'), ObjectId('6012f1c4db453cf448615ffa'), ObjectId('6007e9e43814a82c06aaf8a7'), ObjectId('6012e4fcdb453cf448615f9c'), ObjectId('5fbf7f00fd5d00ca0885e6c5'), ObjectId('5fae51304dc945e46b4bf08e'), ObjectId('60166360e39e130b03b93ca1'), ObjectId('60078dc63814a82c06aaf691'), ObjectId('60166608e39e130b03b93cbc'), ObjectId('6006e1bed5de1807a2945549'), ObjectId('5fb214e1c0ceec0a6ef0631c'), ObjectId('5f758438087161005148e7d2'), ObjectId('601524c50f84134c018333ad'), ObjectId('60072ae2d5de1807a29456f3'), ObjectId('600797563814a82c06aaf6d7'), ObjectId('60071a83d5de1807a294568d'), ObjectId('5f91ba4ff8e3ed277a4a1910'), ObjectId('6006f10ed5de1807a294559d'), ObjectId('600793ca3814a82c06aaf6b8'), ObjectId('6006cd25d5de1807a29454cc'), ObjectId('5fcf3fbcd0252312e936bb18'), ObjectId('600793283814a82c06aaf6b3'), ObjectId('5faf08ca360efadbf82235f9'), ObjectId('60130181db453cf448616054'), ObjectId('6014e725257797b4df4f6a24'), ObjectId('6016504be39e130b03b93c3c'), ObjectId('6007ed6a3814a82c06aaf8ba'), ObjectId('6016431fe39e130b03b93bf2'), ObjectId('6012fbacdb453cf44861602e'), ObjectId('60166ef5e39e130b03b93cdd'), ObjectId('60164631e39e130b03b93c03'), ObjectId('5faf628b360efadbf82237f4'), ObjectId('60126e9dac544dbb81439d84'), ObjectId('60126d02ac544dbb81439d77'), ObjectId('60127078ac544dbb81439d90'), ObjectId('5fd38afb59296cf0a6e7b383'), ObjectId('6012f2f7db453cf448616002'), ObjectId('5fbee0385aa9fb7bcc45b275'), ObjectId('6006c207d5de1807a2945490'), ObjectId('5faee984360efadbf8223556'), ObjectId('6014e220257797b4df4f6a0a'), ObjectId('6006af43d5de1807a294540f'), ObjectId('6016486be39e130b03b93c11'), ObjectId('5fbf88438d69d6d7a1797dee'), ObjectId('5fbea94d5aa9fb7bcc45b164'), ObjectId('6006b42ad5de1807a294542e'), ObjectId('6006d305d5de1807a29454fc'), ObjectId('60126d64ac544dbb81439d7a'), ObjectId('6006c527d5de1807a29454a0'), ObjectId('60127152ac544dbb81439d96'), ObjectId('5f76e1a8087161005148ec77'), ObjectId('6016262070de0262f0f86c2e'), ObjectId('5f19ca4a09e1c3c70302568e'), ObjectId('6007f2a93814a82c06aaf8d1'), ObjectId('60078d303814a82c06aaf68d'), ObjectId('60152a7c0f84134c018333c8'), ObjectId('5fcee1b3d0252312e936b8f4'), ObjectId('600dab88d543fddfd6301947'), ObjectId('5fd3843959296cf0a6e7b364'), ObjectId('6006f2c3d5de1807a29455a5'), ObjectId('6012e482db453cf448615f98'), ObjectId('60161c4570de0262f0f86bee'), ObjectId('60161fc770de0262f0f86c01'), ObjectId('6006d39fd5de1807a2945500'), ObjectId('6012f8bcdb453cf44861601a'), ObjectId('6012f9b1db453cf44861601f'), ObjectId('6014dfee257797b4df4f69fc'), ObjectId('5fbf0bae0e31bd261a16598d'), ObjectId('6006b5cfd5de1807a2945439'), ObjectId('5f76bd6c087161005148eb32'), ObjectId('6006b8ead5de1807a294544b'), ObjectId('6016478ae39e130b03b93c0c'), ObjectId('60071b73d5de1807a2945693'), ObjectId('5fae2197ffaa7d52304bcdf8'), ObjectId('6006ac4fd5de1807a29453fd'), ObjectId('5f76ebea087161005148ecdc'), ObjectId('6006d52dd5de1807a2945508'), ObjectId('6014dd28257797b4df4f69ef'), ObjectId('5f76f104087161005148ed0c'), ObjectId('60152e100f84134c018333e0'), ObjectId('6006ccabd5de1807a29454ca'), ObjectId('6006cbafd5de1807a29454c4'), ObjectId('5f76db77087161005148ec3a'), ObjectId('6006d8fad5de1807a2945519'), ObjectId('6006dc19d5de1807a294552b'), ObjectId('5fe09a38324548b7323aba00'), ObjectId('6006f580d5de1807a29455b6'), ObjectId('6012fc62db453cf448616034'), ObjectId('5fd39bf459296cf0a6e7b3eb'), ObjectId('6012fa5bdb453cf448616024'), ObjectId('600723f3d5de1807a29456c9'), ObjectId('6007ebc53814a82c06aaf8b2'), ObjectId('60126de8ac544dbb81439d7e'), ObjectId('6014e1a5257797b4df4f6a07'), ObjectId('600791433814a82c06aaf6a6'), ObjectId('6006b17fd5de1807a294541e'), ObjectId('601616aa70de0262f0f86bd1'), ObjectId('6006c1d0d5de1807a294548e'), ObjectId('6006c8a4d5de1807a29454b3'), ObjectId('6006b60cd5de1807a294543b'), ObjectId('6007b4303814a82c06aaf785'), ObjectId('5fe0a9c2324548b7323aba60'), ObjectId('6006bf2cd5de1807a2945473'), ObjectId('6006dfebd5de1807a294553e'), ObjectId('6006b650d5de1807a294543d'), ObjectId('6006c417d5de1807a294549a'), ObjectId('5f91a395f8e3ed277a4a1864'), ObjectId('5f70e5dd0269a3cd9caf51bd'), ObjectId('6006cd95d5de1807a29454d0'), ObjectId('5fbf7c7ffd5d00ca0885e6b3'), ObjectId('601520e60f84134c0183339b'), ObjectId('60163af770de0262f0f86ca9'), ObjectId('5f76b18a087161005148eae3'), ObjectId('60071eaed5de1807a29456a9'), ObjectId('60130140db453cf448616052'), ObjectId('5f76ef33087161005148ecfc'), ObjectId('6015542a0f84134c0183348a'), ObjectId('6012f1ffdb453cf448615ffc'), ObjectId('5fe0c93c324548b7323abb0d'), ObjectId('600721a6d5de1807a29456bd'), ObjectId('5fb2592b2bb7c6fe10d260c2'), ObjectId('60126c44ac544dbb81439d73'), ObjectId('5f76a332087161005148ea9f'), ObjectId('600800b33814a82c06aaf914'), ObjectId('6014e3ef257797b4df4f6a13'), ObjectId('5faec3b6360efadbf822348d'), ObjectId('6007abcc3814a82c06aaf74b'), ObjectId('6012e534db453cf448615f9e'), ObjectId('5f76ddfe087161005148ec54'), ObjectId('5f76af3b087161005148ead5'), ObjectId('6014e6e4257797b4df4f6a22'), ObjectId('601550100f84134c01833476'), ObjectId('6007b6b13814a82c06aaf796'), ObjectId('6012f416db453cf448616009'), ObjectId('6006ceebd5de1807a29454d9'), ObjectId('6012f9fbdb453cf448616021'), ObjectId('6014db38257797b4df4f69e5'), ObjectId('5f7b10dfc0092b71a2c6dac1'), ObjectId('6007b0783814a82c06aaf76f'), ObjectId('60164243e39e130b03b93beb'), ObjectId('60071d49d5de1807a29456a0'), ObjectId('6006c95dd5de1807a29454b8'), ObjectId('5fb01d0e3ed5000dbe363305'), ObjectId('5fb1769711c52f727e4d7d01'), ObjectId('60080aa03814a82c06aaf947'), ObjectId('6012facedb453cf448616027'), ObjectId('6014e7a9257797b4df4f6a28'), ObjectId('5fbf786afd5d00ca0885e69d'), ObjectId('5fb00d603ed5000dbe3632a9'), ObjectId('60069d3775b30b32693fd31a'), ObjectId('6012fe64db453cf448616040'), ObjectId('5faf18b5360efadbf822365b'), ObjectId('6012fdf2db453cf44861603e'), ObjectId('60126e59ac544dbb81439d82'), ObjectId('601629da70de0262f0f86c4b'), ObjectId('6006c5e2d5de1807a29454a4'), ObjectId('6012ffd8db453cf448616048')]

#
# print(len(iiiddd))
# add_to_s_c_export_queue(iikkk)
# add_to_s_c_export_queue([ObjectId('602aff781a03b37ed3a72018'),ObjectId('602f3ade7ba8308c59e0f310'),
#                          ObjectId('602b20bf1a03b37ed3a720dd'),ObjectId('602c05941a03b37ed3a725c7'),
#                          ObjectId('602c57ad1a03b37ed3a726cc')])