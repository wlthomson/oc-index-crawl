import hashlib
import pymongo

from idxcrawl.items import AuthorItem
from idxcrawl.items import ThreadItem
from idxcrawl.items import LinkItem

class MongoPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db  = crawler.settings.get('MONGO_DB')
        )

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db  = mongo_db

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db     = self.client[self.mongo_db]

        self.authors_collection = '{}_authors'.format(spider.name)
        self.threads_collection = '{}_threads'.format(spider.name)
        
    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, AuthorItem):
            author_id = hashlib.sha1((item['name']).encode()).hexdigest()
            author = {
                '_id'         : author_id,
                'name'        : item['name'],
                'join_date'   : item['join_date'],
                'total_posts' : item['total_posts']
            }

            self.db[self.authors_collection].update(
                {'_id' : author_id}, author, True
            )

        if isinstance(item, ThreadItem):
            thread_id = hashlib.sha1((item['url']).encode()).hexdigest()
            thread = {
                '_id'        : thread_id,
                'url'        : item['url'],
                'name'       : item['name'],
                'forum'      : item['forum'],
                'start_date' : item['start_date'],
                'replies'    : item['replies'],
                'views'      : item['views'],
                'author'     : item['author_name'],
                'links'      : [],
            }

            self.db[self.threads_collection].update(
                {'_id' : thread_id}, thread, True
            )

        if isinstance(item, LinkItem):
            thread_id = hashlib.sha1((item['thread_url']).encode()).hexdigest()
            link_id   = hashlib.sha1((item['url'] + item['thread_url']).encode()).hexdigest()
            link = {
                'url'        : item['url'],
                'host'       : item['host'],
            }

            self.db[self.threads_collection].update(
                {'_id' : thread_id},
                {'$addToSet' : {'links' : link}}
            )

        return item
