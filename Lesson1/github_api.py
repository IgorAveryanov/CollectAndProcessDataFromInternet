import requests
import json

url = 'https://api.github.com'
user = 'IgorAveryanov'

response = requests.get(f'{url}/users/{user}/repos')

with open('github_repo_list.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, indent=4)

for repo in response.json():
    print(repo['name'])
