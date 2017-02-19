# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from dateparser import parse

def parse_date(join_date):
    return parse(join_date).strftime('%Y-%m-%d')

def string_to_int(int_num):
    return int(int_num.replace(',',''))

def resolve_host_alias(host):
    host_aliases = {
        'rg' : 'rapidgator',
        'ul' : 'uploaded'
    }

    if host in host_aliases:
        return host_aliases[host]
    return host

class AuthorLoader(ItemLoader):
    default_output_processor = TakeFirst()

    join_date_in   = MapCompose(parse_date)
    total_posts_in = MapCompose(string_to_int)

class ThreadLoader(ItemLoader):
    default_output_processor = TakeFirst()

    start_date_in = MapCompose(parse_date)
    replies_in    = MapCompose(string_to_int)
    views_in      = MapCompose(string_to_int)

class LinkLoader(ItemLoader):
    default_output_processor = TakeFirst()

    host_in = MapCompose(resolve_host_alias)

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
