# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AuthorItem(scrapy.Item):
    name        = scrapy.Field()
    join_date   = scrapy.Field()
    total_posts = scrapy.Field()

class ThreadItem(scrapy.Item):
    url         = scrapy.Field()
    name        = scrapy.Field()
    forum       = scrapy.Field()
    start_date  = scrapy.Field()
    replies     = scrapy.Field()
    views       = scrapy.Field()
    author_name = scrapy.Field()

class LinkItem(scrapy.Item):
    url        = scrapy.Field()
    host       = scrapy.Field()
    thread_url = scrapy.Field()
