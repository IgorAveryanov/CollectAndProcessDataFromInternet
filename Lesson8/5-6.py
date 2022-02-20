from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['insta_follow']


name = 'techskills_2022'

followers = [follower for follower in db[name].find({'in_followers': True}, {'name': 1})]
print(followers)

followings = [following for following in db[name].find({'in_following': True}, {'name': 1})]
print(followings)
