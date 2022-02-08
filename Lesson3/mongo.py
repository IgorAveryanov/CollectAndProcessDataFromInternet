# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
# которая будет добавлять только новые вакансии в вашу базу.

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo import errors
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)

db = client['hh_vacancies']

vacancies = db.vacancies

url = 'https://hh.ru'
params = {
    'area': '1',
    'search_field': 'name',
    'text': 'python',
    'items_on_page': '20',
    'page': '0'}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/83.0.4254.19'}

response = requests.get(url + '/search/vacancy', params=params, headers=headers)
dom = BeautifulSoup(response.text, 'html.parser')
last_page = int(dom.find('a', {'data-qa': 'pager-next'}).previous_sibling.find('a', {'class': 'bloko-button'}).find(
    'span').getText())

for page in range(0, last_page + 1):

    params['page'] = str(page)
    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancy_data = dom.find_all('div', {'class': 'vacancy-serp-item'})
    id = 20 * page + 1  # id-счетчик вакансии в базе будет обновляться с каждой новой страницей по этой формуле

    for vacancy in vacancy_data:

        vacancy_dict = {}
        vacancy_dict['_id'] = id
        vacancy_dict['title'] = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText()
        vacancy_dict['link'] = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']

        try:
            salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText().replace(
                '\u202f', '').replace('–', '').split()
        except:
            salary = None

        if not salary:
            vacancy_dict['salary_min'] = None
            vacancy_dict['salary_max'] = None
            vacancy_dict['currency'] = None
        elif salary[0] == 'от':
            vacancy_dict['salary_min'] = int(salary[1])
            vacancy_dict['salary_max'] = None
            vacancy_dict['currency'] = salary[2]
        elif salary[0] == 'до':
            vacancy_dict['salary_min'] = None
            vacancy_dict['salary_max'] = int(salary[1])
            vacancy_dict['currency'] = salary[2]
        else:
            vacancy_dict['salary_min'] = int(salary[0])
            vacancy_dict['salary_max'] = int(salary[1])
            vacancy_dict['currency'] = salary[2]

        vacancy_dict['site'] = url

        try:
            vacancies.insert_one(vacancy_dict)
        except errors.DuplicateKeyError:
            # print(f'Вакансия с id={vacancy_dict["_id"]} уже существует в базе')
            continue

        id += 1

# for vacancy in vacancies.find({}):
#     pprint(vacancy)


# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты). То есть цифра вводится одна, а запрос проверяет оба поля

search_salary = 100000

for vacancy in vacancies.find({'salary.currency': 'руб.',
                               '$or': [{'salary_min': {'$gt': search_salary}},
                                       {'salary_max': {'$gt': search_salary}}]}):
    pprint(vacancy)

