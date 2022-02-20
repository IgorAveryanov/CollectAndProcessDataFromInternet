# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    username = scrapy.Field()
    _id = scrapy.Field()
    name = scrapy.Field()
    full_name = scrapy.Field()
    photo = scrapy.Field()
    in_followers = scrapy.Field()
    in_following = scrapy.Field()

