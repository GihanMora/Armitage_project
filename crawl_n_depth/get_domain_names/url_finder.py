import clearbit
import urllib.request

from requests import session

payload = {
    'action':'Login',
    'Email': 'gihangamage2015@gmail.com',
    'Password': 'Gihan1@uom'
}


clearbit.key = 'sk_86d456666d55d0d2d86c74ccd7d6b639'

with session() as c:
    c.post('https://dashboard.clearbit.com', data=payload)
    response = c.get('https://company.clearbit.com/v1/domains/find?name=bseni')
    print(response.text)