import ast
import re

def clean_add(add_list):
    cleaned_add = []
    for each_ad in add_list:
        if(' Act ' in each_ad or ' act ' in each_ad):
            continue
        if (' Sa ' in each_ad or ' sa ' in each_ad):
            continue
        if (' Wa ' in each_ad or ' wa ' in each_ad):
            continue
        if (' tas ' in each_ad or ' Tas ' in each_ad):
            continue
        w_ori_list = each_ad.split(" ")
        w_list = each_ad.lower().split(" ")
        if('level' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('level'):])
            each_ad = cl_ad
        if ('post' in w_list and 'box' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('post'):])
            each_ad = cl_ad
        if ('po' in w_list and 'box' in w_list):
            cl_ad = (" ").join(w_ori_list[w_list.index('po'):])
            each_ad = cl_ad

        each_ad = each_ad.replace('\\n','')
        each_ad = each_ad.replace('\n', '')
        each_ad = each_ad.replace('\\', '')
        each_ad = each_ad.replace('+', '')
        each_ad = each_ad.replace('<br','')
        each_ad = each_ad.replace('/>', '')
        cleaned_add.append(each_ad)
    return cleaned_add


# add_list = ['119 of 1995, Trade Practices Act 1974', '427 City Road<br />  South Melbourne VIC 3205', '1968 - Act no 63 of 1968, Trade Marks Act 1995']
# clean_add(add_list)








def is_valid_tp(tp):
    ll = ''.join(filter(str.isdigit, tp))
    if(len(tp)>20):
        return False
    if('.' in tp):
        return False
    if ('12345678' in tp):
        return False
    elif (len(ll) == 10 and (ll[0] == '1' or ll[0] == '0')):
        return True
    elif (len(ll) == 11 and ll[0:2] == '61'):
        return True
    elif (len(ll) == 12 and ll[0:2] == '61'):
        return True
    elif ((len(ll) == 10 or len(ll) == 9) and (ll[0] == '0')):
        return True
    elif ((len(ll) == 10 or len(ll) == 11 or len(ll) == 12) and (ll[0:2] == '64')):
        return True
    else:return False
# # print(len('1   2   3   4   5   6   7   ...  171'))
# each_tp = '(1300 22 4636'
# if (each_tp.count('(') == 1 and each_tp.count(')') == 0):
#     each_tp = each_tp.replace('(', "")
# print(each_tp)
# print(is_valid_tp(each_tp))
# print(is_valid_tp('192.168.1.111'))
# print(is_valid_tp('(6411224422'))
# f = open('tp.txt','r')
# r_l = f.readlines()
# for k in r_l:
#     k = ast.literal_eval(k)
#     for l in k:
#         print(l,is_valid_tp(l))
        # ll =  ''.join(filter(str.isdigit, l))
        #
        # if(len(ll)==10 and (ll[0]=='1' or ll[0]=='0')):
        #     print(l+"****"+ll)
        # elif (len(ll) == 11 and ll[0] == '6'):
        #     print(l+"****"+ll)
        # elif (len(ll) == 12 and ll[0:2] == '61'):
        #     print(l+"****"+ll)
        #
        # elif ((len(ll) == 10 or len(ll) == 9 )and (ll[0] == '0')):
        #     print(l + "****" + ll)
        # elif ((len(ll) == 10 or len(ll) == 11 or len(ll) == 12) and (ll[0:2] == '64')):
        #     print(l + "****" + ll)
        #
        #
        # else:print(l)

def add_parser(text):
    extracted_addresses = []
    addregexau = re.compile(
        r"(?i)(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d+))(\b(?:(?!\s{5,}).){1,60})\b(New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|VIC|NSW|ACT|QLD|NT|SA|TAS|WA|Pymble).?[,\s|.\s|,.|\s]*(\b(\d{4})).?[,\s|.\s|,.|\s]*(\b(Australia|Au))?")
    addregexau1 = re.compile(
        r"(?i)(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d+))(\b(?:(?!\s{5,}).){1,60})\b(New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|VIC|NSW|ACT|QLD|NT|SA|TAS|WA|Pymble).?[,\s|.\s|,.|\s]*(\b(Australia|Au))?[,\s|.\s|,.|\s]*(\b(\d{4})).?")

    searchau = re.findall(addregexau, text)
    searchau1 = re.findall(addregexau1, text)
    searchau=searchau+searchau1
    for each in searchau:
        add_l = []
        add_r = list(each)
        for each_r in add_r:
            if (each_r.strip() not in add_l):
                # print(each_r,len(each_r.strip()))
                add_l.append(each_r.strip())
        # print(add_l)
        add_f = (" ").join(add_l).strip()
        extracted_addresses.append(add_f)
        # print("au", add_r)

    addregexnz = re.compile(
        r"(?i)(\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d+))(\b(?:(?!\s{5,}).){1,60})\b(Northland|Auckland|Waikato|Bay of Plenty|Gisborne|Hawke's Bay|Taranaki|Manawatu-Whanganui|Wellington|Tasman|Nelson|Marlborough|West Coast|Canterbury|Otago|Southland).?[,\s|.\s|,.|\s]*(\b(\d{4})).?[,\s|.\s|,.|\s]*(\b(New zealand|Newzealand|Nz))?")
    searchnz = addregexnz.findall(text)
    for each in searchnz:
        add_ln = []
        add_rn = list(each)
        for each_rn in add_rn:
            if (each_rn.strip() not in add_ln):
                add_ln.append(each_rn.strip())
        # print(add_l)
        add_fn = (" ").join(add_ln).strip()
        extracted_addresses.append(add_fn)
        # print("nz", add_nz)

    return extracted_addresses

text = """
['16 ,046  11. Typsy Education , Hospitality , Video Armadale , Victoria Australia', '13 ,193  8. Cluey Learning Education Sydney , New South Wales Australia', '13 ,687  10. Cluey Learning Education Sydney , New South Wales Australia', '14 . Artesian VC 165 4 Sydney , New South Wales Australia', '10 ,085  5. Zookal E-Commerce , Education , Rental Sydney , New South Wales Australia', '10 ,085  6. Zookal E-Commerce , Education , Rental Sydney , New South Wales Australia', '2017 ) Melbourne , Victoria Australia', '701 4. Moodle E-Learning , Education , Open Source Perth , Western Australia Australia', '701 3. Moodle E-Learning , Education , Open Source Perth , Western Australia Australia', '1 . Dave Spicer Founder School of Music Online Brisbane , Queensland Australia', '292 6. OpenLearning EdTech , Education , Software Sydney , New South Wales Australia', '292 7. OpenLearning EdTech , Education , Software Sydney , New South Wales Australia', '2 . InsideSherpa E-Learning , Education , Employment Sydney , New South Wales Australia', '10 . Schrole Group Education , Professional Services Osborne , New South Wales Australia', '12 . Schrole Group Education , Professional Services Osborne , New South Wales Australia', '16 ,046  9. Typsy Education , Hospitality , Video Armadale , Victoria Australia', '409 UX in Higher Education Melbourne August 2017 Melbourne , Victoria Australia Au', '3 . InsideSherpa E-Learning , Education , Employment Sydney , New South Wales Australia', '366 2. Samir Bhana Founder School of Music Online Brisbane , Queensland Australia']



"""
p = add_parser(text)
for j in p:
    print(j)