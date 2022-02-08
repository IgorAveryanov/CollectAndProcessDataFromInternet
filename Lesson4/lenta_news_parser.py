# 1. Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru,
# yandex-новости. Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# 2. Сложить собранные новости в БД
# Минимум один сайт, максимум - все три


import requests
from pymongo import MongoClient
from lxml import html
from pprint import pprint

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/97.0.4692.99 Safari/537.36'}

client = MongoClient('127.0.0.1', 27017)
db = client['news_db']
lenta_news = db.lenta_news
lenta_news.drop()

url = 'https://lenta.ru/'
response = requests.get(url, headers=headers)

dom = html.fromstring(response.text)
items = dom.xpath('//div/a[contains(@class,"card-") and contains(@class,"_topnews")]')

for item in items:
    site = 'lenta.ru'
    name = item.xpath('.//*[contains(@class,"_title")]/text()')[0]
    link = url + item.get('href')
    date = '.'.join([s for s in item.get('href').split('/') if s.isdigit()])
    
    news = {
        'site': site,
        'name': name,
        'link': link,
        'date': date,
    }

    try:
        lenta_news.insert_one(news)
    except:
        continue

for doc in lenta_news.find({}):
    pprint(doc)
