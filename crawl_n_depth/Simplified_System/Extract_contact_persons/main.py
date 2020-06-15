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
        # #grabbing contact persons from opencorporates
        # # time.sleep(10)
        # get_cp_dnb(id_n,mode)
        # # grabbing_contact_persons_from_linkedin
        # time.sleep(10)
        get_li_emp(id_n,mode)
        time.sleep(10)
# re_fix_cp = [ObjectId('5eb657e754ee9cbe1a7388c8'),ObjectId('5eb6688cf9acda3a876322e4'),ObjectId('5eb680d98c70c48229cd26b6'),ObjectId('5ed38efe1838c05e0c6fb6e4'),ObjectId('5ed394144eb75866dfdcdc0d'),ObjectId('5ed39d3781f6df0d82e6bfda'),ObjectId('5ed3add3461496c2716f7235'),ObjectId('5ed3b2383758cc50c8bdd137')]
# re_fix_cp = [ObjectId('5eb6363894bd0b097f9c2734'), ObjectId('5eb657e754ee9cbe1a7388c8'), ObjectId('5eb6688cf9acda3a876322e4'), ObjectId('5eb680d98c70c48229cd26b6'), ObjectId('5eb6776343946ae8fd1e7cc5'), ObjectId('5eb6968b400af16b271e7cc5'), ObjectId('5eb70d32fe79fe7ae11e7cc5'), ObjectId('5eb78a4a081724025f640212'), ObjectId('5eb7c02811ad0e77a8454c26'), ObjectId('5eb81dc6312f24e51eaa1666'), ObjectId('5eb81e3d312f24e51eaa166b'), ObjectId('5eb81e4f312f24e51eaa166c'), ObjectId('5eb846d473cb9c981121f86d'), ObjectId('5eb85afdfdc73635ab21f86d'), ObjectId('5eb86dfe3b429177a721f86d'), ObjectId('5eb871bfb7374d40cf21f86d'), ObjectId('5eb879f2b83e5d3a8e21f86d'), ObjectId('5eb889f4ff01ae732f21f86d'), ObjectId('5eb89febd32a61b6c321f86d'), ObjectId('5eb8a4a6ae599bdfa921f86d'), ObjectId('5eb8b262c08e90f27321f86d'), ObjectId('5eb8c9b046a9eb0b8621f86d'), ObjectId('5eb8eb8f7e96c2e52021f86d'), ObjectId('5eb903bd297b7ab6ea21f86d'), ObjectId('5eb90b6ff57c66a55021f86d'), ObjectId('5eb93a35286bebbd3721f86d'), ObjectId('5eb93e5a0f155b463f21f86d'), ObjectId('5eb959a6a700a8698721f86d'), ObjectId('5eb98f63c77b06851a21f86d'), ObjectId('5eb994d95eab3ba67221f86d'), ObjectId('5eb9a6ddfce4130a7921f86d'), ObjectId('5eb9b517d4ae71db7f21f86d'), ObjectId('5eb9bb86c18b4ececb21f86d'), ObjectId('5eba2b4bc2a93be6f36aa0f6'), ObjectId('5eba3e291a4d4152146aa0f6'), ObjectId('5eba41451c03037ed46aa0f6'), ObjectId('5eba4709e77bc924246aa0f6'), ObjectId('5eba5b4b0f90c581b16aa0f6'), ObjectId('5eba6cd088ad4c0ff46aa0f6'), ObjectId('5ebab9bc034f665cc26aa0f6'), ObjectId('5ebb2bf6eef7c615c56aa0f6'), ObjectId('5ebb981f578345eba46aa0f6'), ObjectId('5ebbb03674dee939a46aa0f6'), ObjectId('5ebbc4dd2563b3460d6aa0f6'), ObjectId('5ebbdd4d7655a83e6297178d'), ObjectId('5ebbfe2692b1ee138897178d'), ObjectId('5ebc3d0f0f1bbea78f97178d'), ObjectId('5ebc3fe0843419ca2497178d'), ObjectId('5ebc4dc1a821835a79bb9565'), ObjectId('5ebc91d972a50ff18ebb9565'), ObjectId('5ebca4cc099c653561bb9565'), ObjectId('5ebcae4585e6061bd0bb9565'), ObjectId('5ebd26b2031e847836bb9565'), ObjectId('5ebd2f1fd143dae4b2bb9565'), ObjectId('5ebd32b7fd1b187544bb9565'), ObjectId('5ebd3a22f321cdd207d1b7ab'), ObjectId('5ebd3d8fdda69510b998bd17'), ObjectId('5ebdcaad9cf085d4ca23510e'), ObjectId('5ebdcc63b52e86ccbb23510e'), ObjectId('5ebde6341572b9f0a223510e'), ObjectId('5ebded47254503787123510e'), ObjectId('5ebdfeddbbcc93a8d223510e'), ObjectId('5ebe1d5f229dc61a2c23510e'), ObjectId('5ebe28e9361dd7cb3c23510e'), ObjectId('5ebe4e433674355bc023510e'), ObjectId('5ebe50421cf82abcf923510e'), ObjectId('5ebe5ebede558cbbb223510e'), ObjectId('5ec2529091262b4135d08ffd'), ObjectId('5ec2581cce74147a42d08ffd'), ObjectId('5ec25d3620ca9d30b4d08ffd'), ObjectId('5ec278aa7c9f8148cbd08ffd'), ObjectId('5ec2800bb7d0988a19d08ffd'), ObjectId('5ec2811a0358b118e9d08ffd'), ObjectId('5ec282a717f1a373ded08ffd'), ObjectId('5ec2aa04af3b98009ad08ffd'), ObjectId('5ec2bd51c1fad7d413d08ffd'), ObjectId('5ec2caa5f6a74cc792d08ffd'), ObjectId('5ec2dfd22cd3eef557d08ffd')]

to_fix_edu = [ObjectId('5eb64cfc8c94747a21f39855'),ObjectId('5eb6b61fabf00d5fdb2d05a3'),ObjectId('5eb6b71e5cd9b7b54c7d9961'),ObjectId('5eb6b9158f232307ce0bdc13'),ObjectId('5eb6b9dbb8b6b03010c4dcc6'),ObjectId('5eb6bbbee2f17c3f3238cec8'),ObjectId('5eb6bca1b68e7672cd0ef210'),ObjectId('5eb6bdb1e7b6cc4614eb0edb'),ObjectId('5eb6beca47492aa1e0553de4'),ObjectId('5eb6bfc707fd60d7d77844de')]


# extract_contact_persons(to_fix_edu,'query')