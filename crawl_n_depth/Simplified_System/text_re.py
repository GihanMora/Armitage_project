import re


text = "Our offices Sydney 5 Blackfriars Street Chippendale NSW 2008 Australia Melbourne Ground Floor 430 Little Collins Street Melbourne VIC 3000 Australia Perth Suite 2, Churchill Court 234 Churchill Avenue Subiaco WA 6008 Australia Canberra Building 5 1 Dairy Rd Fyshwick ACT 2609 Australia 2and2"

addregexau = re.compile(r"(?i)(\\b(PO BOX|post box)[,\s|.\s|,.|\s]*)?(\b(\d+))(\b(?:(?!\s{2,}).){1,60})\b(New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|VIC|NSW|ACT|QLD|NT|SA|TAS|WA).?[,\s|.\s|,.|\s]*(\b\d{4}).?[,\s|.\s|,.|\s]*(\b(Australia|Au))?")
searchau = re.findall(addregexau,text)
for each in searchau:
    add_l = []
    add_r =list(each)
    for each_r in add_r:
        if(each_r not in add_l):
            add_l.append(each_r)
    # print(add_l)
    add_f = (" ").join(add_l).strip()
    print(add_f)
# if (len(searchau)):
#     add_r = (" ").join(list(searchau[0]))
#     add_r = add_r.strip()
#     print(add_r)