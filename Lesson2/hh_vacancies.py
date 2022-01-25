# Необходимо собрать информацию о вакансиях на вводимую должность
# (используем input или через аргументы получаем должность) с сайтов HH(обязательно) и/или Superjob(по желанию).
# Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
#     1. Наименование вакансии.
#     2. Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
#     3. Ссылку на саму вакансию.
#     4. Сайт, откуда собрана вакансия (можно указать статично для hh - hh.ru, для superjob - superjob.ru)
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью
# dataFrame через pandas. Сохраните в json либо csv.

import requests
import pandas as pd
from bs4 import BeautifulSoup

vacancy_list = []
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

    for vacancy in vacancy_data:

        vacancy_dict = {}
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

        vacancy_list.append(vacancy_dict)


df = pd.DataFrame(vacancy_list)
df.to_csv('vacancies.csv', encoding="utf-8-sig")
print(df.shape)
print(df.head())