import requests
import json

token = ''
user_id = '2423492'

url = 'https://api.vk.com/method/groups.get'
params = {'v': '5.131',
          'access_token': token,
          'user_id': user_id,
          'extended': 1}

response = requests.get(url, params=params)

with open('vk_groups.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, indent=4)

print(f'Список сообществ пользователя {user_id}:')
for community in response.json().get('response').get('items'):
    print(f"\t{community.get('name')}")
