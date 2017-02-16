# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ForumPage(scrapy.Item):
    name = scrapy.Field()
    page = scrapy.Field()
    url  = scrapy.Field()

class ThreadPage(scrapy.Item):
    name        = scrapy.Field()
    url         = scrapy.Field()
    start_date  = scrapy.Field()
    replies     = scrapy.Field()
    views       = scrapy.Field()

class Author(scrapy.Item):
    name         = scrapy.Field()
    url          = scrapy.Field()
    join_date    = scrapy.Field()
    total_posts  = scrapy.Field()
    rank         = scrapy.Field()
