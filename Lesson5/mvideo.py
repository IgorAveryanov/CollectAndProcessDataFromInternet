# Написать программу, которая собирает товары «В тренде» с сайта техники mvideo и складывает данные в БД.
# Сайт можно выбрать и свой. Главный критерий выбора: динамически загружаемые товары

from pymongo import MongoClient
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

client = MongoClient('localhost', 27017)
mongo_base = client['mvideo']
collection = mongo_base['in_trend']

chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
driver.implicitly_wait(10)

driver.get('https://www.mvideo.ru/')

assert 'М.Видео' in driver.title

label = driver.find_element(By.XPATH, "//a[@class='logo ng-tns-c279-2 ng-star-inserted'][@title='Главная']")

while True:
    try:
        elem = driver.find_element(By.XPATH, "//button[@class='tab-button ng-star-inserted']//span[@class='title']")
        break
    except exceptions.NoSuchElementException:
        label.send_keys(Keys.PAGE_DOWN)
elem.click()

products = driver.find_elements(By.XPATH,
                                '//mvid-carousel[@class="carusel ng-star-inserted"]//mvid-product-cards-group//div['
                                'contains(@class, "product-mini-card__image")]//a')
links = []

for product in products:
    link = product.get_attribute('href')
    links.append(link)

for link in links:
    product = {}
    product['link'] = link
    driver.implicitly_wait(10)
    driver.get(link)
    product['name'] = driver.find_element(By.XPATH, '//h1').get_attribute('innerHTML')
    product['price'] = driver.find_element(By.XPATH,
                                           '//mvideoru-product-details-card//span[@class="price__main-value"]').get_attribute(
        'innerHTML').replace('&nbsp', '').replace(';', '').replace('₽', '')

    collection.update_one({'link': product['link']}, {'$set': product}, upsert=True)

driver.quit()
