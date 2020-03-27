import csv
import pandas as pd
def make_csvs():
    with open("csvfiles_ABR/Public01.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        types_set = []
        first_line =[]
        for i,line in enumerate(reader):
            line = line[0].split(',')
            if(i==0): first_line=line
            if line[2] not in types_set:
                types_set.append(line[2])
        print(types_set)
        for each in types_set[1:]:
            f = open('classified_fast/'+str(each).replace("/","_")+".csv","w",newline='', encoding='utf-8')
            writer = csv.writer(f)
            writer.writerow(first_line)

make_csvs()
with open("csvfiles_ABR/Public01.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for i,line in enumerate(reader):
            print(i)
            line = line[0].split(',')
            if(i==0): continue
            f = open('classified_fast/' + str(line[2]).replace("/", "_") + ".csv", "a+",newline='', encoding='utf-8')
            writer = csv.writer(f)
            writer.writerow(line)

# df = pd.read_csv("csvfiles_ABR/Public01.csv")
# print(df.head())
#
# for i in range(len(df)):
#     # print('aa',df.values[i])
#     # print('bb',df['ABN'][i],df['EntityTypeInd'][i],df['EntityTypeText'][i],df['NonIndividualNameText'][i],df['GivenName'][i],
#     #  df['FamilyName'][i],df['State'][i],df['Postcode'][i],df['ASICNumber'][i],df['OtherEntity'][i])
#     # if(i==10):break
#     line = df.values[i]
#     print(str(line[2]).replace("/", "_").replace(" ","_") )
#     f = open('classified/' + str(line[2]).replace("/", "_") + ".csv", "a+", newline='', encoding='utf-8')
#     writer = csv.writer(f)
#     writer.writerow(line)