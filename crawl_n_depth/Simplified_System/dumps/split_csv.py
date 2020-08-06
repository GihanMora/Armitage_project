import ast
import csv

with open('merged_file.csv', encoding='utf8') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    with open('fixed_file.csv', mode='w', encoding='utf8',
              newline='') as results_file:  # store search results in to a csv file
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        attributes_a = ['id','search_text', 'title', 'link', 'description', 'comp_name',
                        'address','address_source', 'email','email_source', 'telephone_number','tp_source', 'keywords', 'contact_person','contact_person_source', 'type_or_sector','type_or_sector_source',
                        'founded_year','founded_year_source',
                        'revenue','revenue_source', 'funding','funding_source', 'headquarters','hq_source', 'No_of_employees','Number_of_employees_source', 'company_status','company_state_source']
        results_writer.writerow(attributes_a)

        for row in csv_reader:
            writing_row = []
            writing_row.extend(row[:6])
            if(row[6]!='None'):
                add_s = ast.literal_eval(row[6])
                writing_row.extend(add_s)
            else:writing_row.extend(['None','None'])
            if (row[7] != 'None'):
                eml_s = ast.literal_eval(row[7])
                writing_row.extend(eml_s)
            else:
                writing_row.extend(['None', 'None'])
            if (row[8] != 'None'):
                tp_s = ast.literal_eval(row[8])
                writing_row.extend(tp_s)
            else:
                writing_row.extend(['None', 'None'])
            writing_row.append(row[9])
            if (row[10] != 'None'):
                cp_s = ast.literal_eval(row[10])
                writing_row.extend(cp_s)
            else:
                writing_row.extend(['None', 'None'])
            if (row[11] != 'None'):
                type_s = ast.literal_eval(row[11])
                writing_row.extend(type_s)
            else:
                writing_row.extend(['None', 'None'])
            if (row[12] != 'None'):
                fy_s = ast.literal_eval(row[12])
                writing_row.extend(fy_s)
            else:
                writing_row.extend(['None', 'None'])
            if (row[13] != 'None'):
                rv_s = ast.literal_eval(row[13])
                writing_row.extend(rv_s)
            else:
                writing_row.extend(['None', 'None'])
            if (row[14] != 'None'):
                f_s = ast.literal_eval(row[14])
                writing_row.extend(f_s)
            else:
                writing_row.extend(['None', 'None'])
            if (row[15] != 'None'):
                hq_s = ast.literal_eval(row[15])
                writing_row.extend(hq_s)
            else:
                writing_row.extend(['None', 'None'])
            if (row[16] != 'None'):
                ne_s = ast.literal_eval(row[16])
                writing_row.extend(ne_s)
            else:
                writing_row.extend(['None', 'None'])
            if (row[17] != 'None'):
                st_s = ast.literal_eval(row[17])
                writing_row.extend(st_s)
            else:
                writing_row.extend(['None', 'None'])
            writing_row.extend(row[18:])

            results_writer.writerow(writing_row)
        results_file.close()


