# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        client.drop_database('vacancies0402')
        self.mongobase = client.vacancies0402

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            salary = self.process_hhru_salary(item.get('salary'))
        else:
            salary = self.process_sjru_salary(item.get('salary'))
        item['salary_min'], item['salary_max'], item['cur'] = salary
        del item['salary']
        collection = self.mongobase[spider.name]
        collection.insert_one(item)
        return item

    @staticmethod
    def process_hhru_salary(dirty_salary):
        if 'от' in dirty_salary[0]:
            cur = dirty_salary[-2]
            min_salary = dirty_salary[1].replace('\xa0', '')
            if 'до' in dirty_salary[2]:
                max_salary = dirty_salary[3].replace('\xa0', '')
            else:
                max_salary = None
        elif 'до' in dirty_salary[0]:
            cur = dirty_salary[-2]
            min_salary = None
            max_salary = dirty_salary[1].replace('\xa0', '')
        else:
            min_salary, max_salary, cur = None, None, None

        return min_salary, max_salary, cur

    @staticmethod
    def process_sjru_salary(dirty_salary):
        min_salary, max_salary, cur = None, None, 'руб'
        if dirty_salary[0] == 'от':
            min_salary = int(''.join(filter(str.isdigit, dirty_salary[2].replace('\xa0', ''))))
        elif dirty_salary[0] == 'до':
            max_salary = int(''.join(filter(str.isdigit, dirty_salary[2].replace('\xa0', ''))))
        elif len(dirty_salary) > 3:
            min_salary = int(''.join(filter(str.isdigit, dirty_salary[0].replace('\xa0', ''))))
            max_salary = int(''.join(filter(str.isdigit, dirty_salary[4].replace('\xa0', ''))))
        else:
            cur = None

        return min_salary, max_salary, cur
