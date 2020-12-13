from ..linkedin_profile_picker.get_n_search_results import getGoogleLinksForSearchText


names = ['Damminda Alahakon']


def get_li_url(name_i):
    query = 'site:au.linkedin.com '+ name_i
    sr = getGoogleLinksForSearchText(query, 3, 'normal')
    filtered_li = []
    for p in sr:
        # print(p['link'])
        if 'linkedin.com' in p['link']:
            filtered_li.append(p['link'])
    if (len(filtered_li)):
        return filtered_li[0]
    else:
        print("No linkedin contacts found!, Try again")
        return ['Not found']


for name_i in names:
    li_url = get_li_url(name_i)
    print(li_url)