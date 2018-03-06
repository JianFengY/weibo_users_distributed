# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class WeiboUsersItem(Item):
    id = Field()  # 用户ID
    screen_name = Field()  # 用户名
    profile_image_url = Field()  # 头像地址
    profile_url = Field()  # 个人主页，地址是包括fid等东西的，其实有ID就能构造个人主页
    follow_count = Field()  # 关注数
    followers_count = Field()  # 粉丝数
    gender = Field()  # 性别
    description = Field()  # 简介
