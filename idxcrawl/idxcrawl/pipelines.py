# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3

from idxcrawl.items import AuthorItem
from idxcrawl.items import ThreadItem
from idxcrawl.items import LinkItem

class SQLitePipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sql_db = crawler.settings.get('SQLITE_DB')
        )

    def __init__(self, sql_db):
        self.sql_db = sql_db

    def open_spider(self, spider):
        self.authors_table   = '{}_authors'.format(spider.name)
        self.threads_table = '{}_threads'.format(spider.name)
        self.links_table   = '{}_links'.format(spider.name)

        self.CREATE_AUTHORS_TABLE = '''
            CREATE TABLE IF NOT EXISTS {} (
                name        TEXT,
                join_date   TEXT,
                total_posts INTEGER,
                PRIMARY KEY (name)
            );
        '''.format(self.authors_table)

        self.CREATE_THREADS_TABLE = '''
            CREATE TABLE IF NOT EXISTS {} (
                url         TEXT,
                name        TEXT,
                forum       TEXT,
                start_date  TEXT,
                replies     INTEGER,
                views       INTEGER,
                author      TEXT,
                PRIMARY KEY (url),
                FOREIGN KEY (author) REFERENCES {}(name)
            );
        '''.format(self.threads_table, self.authors_table)

        self.CREATE_LINKS_TABLE = '''
           CREATE TABLE IF NOT EXISTS {} (
               url         TEXT,
               host        TEXT,
               thread_url  TEXT NOT NULL,
               PRIMARY KEY (url, thread_url),
               FOREIGN KEY (thread_url) REFERENCES {}(url)
           );
        '''.format(self.links_table, self.threads_table)

        self.QUERY_AUTHORS_TABLE = '''
            SELECT * FROM {}
            WHERE name=:name;
        '''.format(self.authors_table)

        self.QUERY_THREADS_TABLE = '''
            SELECT * FROM {}
            WHERE url=:url;
        '''.format(self.threads_table)

        self.QUERY_LINKS_TABLE = '''
            SELECT * FROM {}
            WHERE thread_url=:thread_url AND url=:url;
        '''.format(self.links_table)

        self.INSERT_AUTHORS_TABLE = '''
            INSERT INTO {} (
                name,
                join_date,
                total_posts
            ) VALUES (
                :name,
                :join_date,
                :total_posts
            );
        '''.format(self.authors_table)

        self.INSERT_THREADS_TABLE = '''
            INSERT INTO {} (
                url,
                name,
                forum,
                start_date,
                replies,
                views,
                author
            ) VALUES (
                :url,
                :name,
                :forum,
                :start_date,
                :replies,
                :views,
                :author
            );
        '''.format(self.threads_table)

        self.INSERT_LINKS_TABLE = '''
            INSERT INTO {} (
                url,
                host,
                thread_url
            ) VALUES (
                :url,
                :host,
                :thread_url
            );
        '''.format(self.links_table)

        self.UPDATE_AUTHORS_TABLE = '''
            UPDATE {}
            SET join_date=:join_date,
                total_posts=:total_posts
                WHERE name=:name;
        '''.format(self.authors_table)

        self.UPDATE_THREADS_TABLE = '''
            UPDATE {}
            SET name=:name,
                forum=:forum,
                start_date=:start_date,
                replies=:replies,
                views=:views,
                author=:author
                WHERE url=:url;
        '''.format(self.threads_table)

        self.UPDATE_LINKS_TABLE = '''
            UPDATE {}
            SET host=:host
            WHERE thread_url=:thread_url AND url=:url;
        '''.format(self.links_table)

        self.conn   = sqlite3.connect(self.sql_db)
        self.cursor = self.conn.cursor()

        self.cursor.execute(self.CREATE_AUTHORS_TABLE)
        self.cursor.execute(self.CREATE_THREADS_TABLE)
        self.cursor.execute(self.CREATE_LINKS_TABLE)

        self.conn.commit()

    def process_item(self, item, spider):
        if isinstance(item, AuthorItem):
            self.cursor.execute(
                self.QUERY_AUTHORS_TABLE, {
                    'name' : item['name']
                }
            )
            if not self.cursor.fetchone():
                self.cursor.execute(
                    self.INSERT_AUTHORS_TABLE, {
                        'name'        : item['name'],
                        'join_date'   : item['join_date'],
                        'total_posts' : item['total_posts']
                    }
                )
            else:
                self.cursor.execute(
                    self.UPDATE_AUTHORS_TABLE, {
                        'name'        : item['name'],
                        'join_date'   : item['join_date'],
                        'total_posts' : item['total_posts']
                    }
                )

        if isinstance(item, ThreadItem):
            self.cursor.execute(
                self.QUERY_THREADS_TABLE, {
                    'url' : item['url']
                }
            )
            if not self.cursor.fetchone():
                self.cursor.execute(
                    self.INSERT_THREADS_TABLE, {
                        'url'        : item['url'],
                        'name'       : item['name'],
                        'forum'      : item['forum'],
                        'start_date' : item['start_date'],
                        'replies'    : item['replies'],
                        'views'      : item['views'],
                        'author'     : item['author_name']
                    }
                )
            else:
                self.cursor.execute(
                    self.UPDATE_THREADS_TABLE, {
                        'url'        : item['url'],
                        'name'       : item['name'],
                        'forum'      : item['forum'],
                        'start_date' : item['start_date'],
                        'replies'    : item['replies'],
                        'views'      : item['views'],
                        'author'     : item['author_name']
                    }
                )

        if isinstance(item, LinkItem):
            self.cursor.execute(
                self.QUERY_LINKS_TABLE, {
                    'url'        : item['url'],
                    'thread_url' : item['thread_url']
                }
            )
            if not self.cursor.fetchone():
                self.cursor.execute(
                    self.INSERT_LINKS_TABLE, {
                        'url'        : item['url'],
                        'host'       : item['host'],
                        'thread_url' : item['thread_url']
                    }
                )
            else:
                self.cursor.execute(
                    self.UPDATE_LINKS_TABLE, {
                        'url'        : item['url'],
                        'host'       : item['host'],
                        'thread_url' : item['thread_url']
                    }
                )

        self.conn.commit()

        return item

    def close_spider(self, spider):
        self.conn.close()
