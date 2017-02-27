# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from idxcrawl.sqlite_pipeline import SQLitePipeline
from idxcrawl.mongo_pipeline import MongoPipeline

