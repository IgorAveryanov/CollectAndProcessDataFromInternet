# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from pymongo import errors


class InstaparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.insta_follow

    def process_item(self, item, spider):
        collection = self.mongobase[item.get("username")]
        del item['username']

        try:
            collection.insert_one(item)
        except errors.DuplicateKeyError:
            if item.get('in_followers'):
                collection.update_one({'_id': item.get('_id')},
                                      {'$set': {'in_followers': True}})
            else:
                collection.update_one({'_id': item.get('_id')},
                                      {'$set': {'in_following': True}})
        return item


class InstaPhotoPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            try:
                yield scrapy.Request(item['photo'])
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        item['photo'] = results[0][1] if results[0][0] else None
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        file_name = f'{item.get("name")}_{item.get("_id")}'
        return f'{file_name}.jpg'
