adds = ['5 Blackfriars St, Chippendale NSW 2008, Australia','5 1 Dairy Rd Fyshwick ACT 2609', '430 Little Collins Street Melbourne VIC 3000', '5 1 Dairy Rd Fyshwick ACT 2609 Australia', '883 974.  Our offices Sydney 5 Blackfriars Street Chippendale NSW 2008', '5 Blackfriars StreetChippendale, NSW 2008', '5 Blackfriars Street","addressLine2":"Chippendale, NSW 2008', 'Suite  2 , Churchill Court 234 Churchill Avenue Subiaco WA 6008', '430 Little Collins Street Melbourne VIC 3000 Australia', '234 Churchill Avenue Subiaco WA 6008 Australia', '5 Blackfriars Street Chippendale NSW 2008 Australia', 'Suite  2 , Churchill Court 234 Churchill Avenue Subiaco WA 6008 Australia', '5 Blackfriars Street Chippendale NSW 2008', '883 974.  Our offices Sydney 5 Blackfriars Street Chippendale NSW 2008 Australia','5 BLACKFRIARS STREET CHIPPENDALE, NEW SOUTH WALES, 2008 Australia','5 Blackfriars Street Chippendale, New South Wales, 2008 Australia']

def get_address_vector(address):
    lowered = address.lower()
    c_rv = lowered.replace(",", " ")
    vector = (c_rv.split())
    return vector

ads_s1 = [[each_i,'s1'] for each_i in adds[:5]]
ads_s2 = [[each_i,'s2'] for each_i in adds[5:10]]
ads_s3 = [[each_i,'s3'] for each_i in adds[10:]]
adds = ads_s1+ads_s2+ads_s3
adds = [['a b c d e','s3'],['a b c d','s1'],['a b c d p q','s2']]
print(adds)
def get_confidence(adds):
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
            print(each_ad_a,"score "+str(len(commons))+" "+str(len(av_sources)-1))
