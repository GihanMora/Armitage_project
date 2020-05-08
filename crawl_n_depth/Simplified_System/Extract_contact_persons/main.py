#update sys path if you need to run this seperately

import time
import sys
from bson import ObjectId
sys.path.insert(0, 'F:/Armitage_project/crawl_n_depth/')
from bson import ObjectId
from Simplified_System.Extract_contact_persons.scrape_comp_profiles import get_cp_dnb,get_cp_oc
from Simplified_System.Extract_contact_persons.scrape_linkedin_employees import get_li_emp

# id_list = [ObjectId('5ea16524448198da7f949494'),ObjectId('5ea16529448198da7f949495')]
# id_list = [  ObjectId('5ea68b4976a95ce09edcbe0a'), ObjectId('5ea68b5e76a95ce09edcbe0b'), ObjectId('5ea68b7376a95ce09edcbe0c'), ObjectId('5ea68b9b76a95ce09edcbe0d'), ObjectId('5ea68bb176a95ce09edcbe0e'), ObjectId('5ea690d71ded0362e3f25021'), ObjectId('5ea691191ded0362e3f25022'), ObjectId('5ea691481ded0362e3f25024'), ObjectId('5ea69e062f7730c4b15480f3'), ObjectId('5ea69e1b2f7730c4b15480f4'), ObjectId('5ea69e342f7730c4b15480f5'), ObjectId('5ea6ca1da27a31ef12ce1206'), ObjectId('5ea6ca37a27a31ef12ce1207'), ObjectId('5ea6ca6aa27a31ef12ce1208')]



def extract_contact_persons(id_list,mode):
    for id_n in id_list:
        #grabbing contact persons from dnb

        # get_cp_oc(id_n, mode)
        #grabbing contact persons from opencorporates
        # time.sleep(10)
        get_cp_dnb(id_n,mode)
        #grabbing_contact_persons_from_linkedin
        # time.sleep(10)
        # get_li_emp(id_n,mode)
        time.sleep(10)

# extract_contact_persons([ObjectId('5eb515eee7e6f6c4669eff4b')],'query')