# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import json
import re
import random

from weibo_users.items import WeiboUsersItem


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['m.weibo.cn']
    start_urls = ['https://m.weibo.cn']

    # 初始用户
    start_user = '2100773364'

    # 这个URL有用户信息也有发的微博，page可以用来获取微博
    # user_info_url = 'https://m.weibo.cn/api/container/getIndex?containerid=107603{user_id}&page={page}'
    # 用户信息
    user_info_url = 'https://m.weibo.cn/api/container/getIndex?containerid=107603{user_id}'
    # 关注人列表
    follows_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{user_id}&page={page}'
    # 粉丝列表
    fans_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{user_id}&since_id={since_id}'

    def start_requests(self):
        """初始调用"""
        # 获取初始用户信息
        yield Request(self.user_info_url.format(user_id=self.start_user), callback=self.parse_user_info)
        # 获取初始用户关注列表
        yield Request(self.follows_url.format(user_id=self.start_user, page=1), callback=self.parse_follows)
        # 获取初始用户粉丝列表
        yield Request(self.fans_url.format(user_id=self.start_user, since_id=1), callback=self.parse_fans)

    def parse_user_info(self, response):
        """获取用户信息"""
        cards = json.loads(response.text).get('data').get('cards')
        if cards:
            result = cards[0].get('mblog').get('user')
            if result:
                item = WeiboUsersItem()
                for field in item.fields:
                    if field in result.keys():
                        item[field] = result.get(field)
                yield item

                # 对每个用户再获取他们的关注列表
                yield Request(self.follows_url.format(user_id=item['id'], page=1), callback=self.parse_follows)
                # 对每个用户再获取他们的粉丝列表
                yield Request(self.fans_url.format(user_id=item['id'], since_id=1), callback=self.parse_follows)

    def parse_follows(self, response):
        """获取关注列表"""
        cards = json.loads(response.text).get('data').get('cards')
        if cards:  # 判断是否获取完全部关注人
            for card in cards:
                if card.get('title') and '全部关注' in card.get('title'):
                    result = card.get('card_group')
                    for item in result:
                        # 调用parse_user_info()获取用户信息
                        if item.get('user').get('id'):
                            yield Request(self.user_info_url.format(user_id=item.get('user').get('id')),
                                          callback=self.parse_user_info)
            # 获取下一页关注的人
            page = re.search('since_id=(\d+)', response.url)
            next_page = int(page.group(1)) + 1 if page else 2
            yield Request(self.follows_url.format(user_id=self.start_user, page=str(next_page)),
                          callback=self.parse_follows)

    def parse_fans(self, response):
        """获取粉丝列表"""
        cards = json.loads(response.text).get('data').get('cards')
        if cards:  # 判断是否获取完全部粉丝
            result = cards[0].get('card_group')
            for item in result:
                # 调用parse_user_info()获取用户信息
                yield Request(self.user_info_url.format(user_id=item.get('user').get('id')),
                              callback=self.parse_user_info)
            # 获取下一页粉丝
            since_id = re.search('since_id=(\d+)', response.url)
            next_since_id = int(since_id.group(1)) + 1 if since_id else 2
            yield Request(self.fans_url.format(user_id=self.start_user, since_id=next_since_id),
                          callback=self.parse_fans)
