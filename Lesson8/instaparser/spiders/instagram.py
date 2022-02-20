import scrapy
import json
import re
import os
from dotenv import load_dotenv
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from urllib.parse import urlencode
from copy import deepcopy
load_dotenv('D:\docs\GB\Scrapy_proects\hw_8_Instaparser\instaparser\spiders\.env')


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = os.getenv('LOGIN')
    inst_password = os.getenv('PASSWORD')
    users_parse = ['badspacecomics',
                   'maciejkuciara']
    api_headers = {'User-Agent': 'Instagram 155.0.0.37.107'}
    follow_url = 'https://i.instagram.com/api/v1/friendships/'

    def parse(self, response):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'enc_password': self.inst_password,
                                           'username': self.inst_login},
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user in self.users_parse:
                yield response.follow(
                    f'/{user}/',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user})

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'count': 12}
        status = ['followers', 'following']
        for stat in status:
            url_follow = f'{self.follow_url}{user_id}/{stat}/?{urlencode(variables)}'
            callback = self.followers_parse if stat == 'followers' else self.following_parse
            yield response.follow(url_follow,
                                  callback=callback,
                                  headers=self.api_headers,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables)})

    def followers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        big_list = j_data.get('big_list')
        if big_list:
            variables['max_id'] = j_data.get('next_max_id')
            url_followers = f'{self.follow_url}{user_id}/followers/?{urlencode(variables)}'
            yield response.follow(url_followers,
                                  callback=self.followers_parse,
                                  headers=self.api_headers,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables)})

        followers = j_data.get('users')
        for follower in followers:
            item = InstaparserItem(
                username=username,
                _id=follower.get('pk'),
                name=follower.get('username'),
                full_name=follower.get('full_name'),
                photo=follower.get('profile_pic_url'),
                in_followers=True
            )
            yield item

    def following_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        big_list = j_data.get('big_list')
        if big_list:
            variables['max_id'] = j_data.get('next_max_id')
            url_followings = f'{self.follow_url}{user_id}/following/?{urlencode(variables)}'
            yield response.follow(url_followings,
                                  callback=self.following_parse,
                                  headers=self.api_headers,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables)})

        followings = j_data.get('users')
        for following in followings:
            item = InstaparserItem(
                username=username,
                _id=following.get('pk'),
                name=following.get('username'),
                full_name=following.get('full_name'),
                photo=following.get('profile_pic_url'),
                in_following=True
            )
            yield item

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
