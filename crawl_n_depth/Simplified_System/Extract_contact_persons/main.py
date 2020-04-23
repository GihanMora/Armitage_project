from bson import ObjectId
from scrape_comp_profiles import get_cp_dnb,get_cp_oc
from scrape_linkedin_employees import get_li_emp

id_list = [ObjectId('5ea16524448198da7f949494'),ObjectId('5ea16529448198da7f949495')]


#grabbing contact persons from dnb
get_cp_dnb(id_list[0])


#grabbing contact persons from opencorporates
get_cp_oc(id_list[0])

#grabbing_contact_persons_from_linkedin
get_li_emp(id_list[0])