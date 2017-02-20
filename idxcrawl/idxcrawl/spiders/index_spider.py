from abc import ABCMeta, abstractmethod

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.shell import inspect_response

from idxcrawl.link_extractor import LinkExtractor

from idxcrawl.items import AuthorItem
from idxcrawl.items import ThreadItem
from idxcrawl.items import LinkItem
from idxcrawl.items import AuthorLoader
from idxcrawl.items import ThreadLoader
from idxcrawl.items import LinkLoader

class Author:
    def __init__(self, name=None, url=None, join_date=None,
                 total_posts=None, rank=None):
        self.name        = name
        self.url         = url
        self.join_date   = join_date
        self.total_posts = total_posts
        self.rank        = rank

class Forum:
    def __init__(self, name=None, category=None, page=None,
                 url=None):
        self.name     = name
        self.category = category
        self.page     = page
        self.url      = url

class Thread:
    def __init__(self, name=None, url=None, start_date=None,
                 replies=None, views=None):
        self.name = name
        self.url  = url
        self.start_date = start_date
        self.replies = replies
        self.views = views

class IndexSpider(scrapy.Spider):
    __metaclass__ = ABCMeta

    def get_link_extractor(self):
        try:
            self.link_extractor = LinkExtractor()
        except FileNotFoundError:
            raise CloseSpider('ERROR_NO_HOSTS_FILE')

    def parse_args(self, kwargs):
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')

        try:
            self.min_page_num = int(kwargs['min_page_num'])
        except (KeyError, TypeError, ValueError):
            self.min_page_num = 1

        try:
            self.max_page_num = int(kwargs['max_page_num'])
        except (KeyError, TypeError, ValueError):
            self.max_page_num = float('inf')

    def __init__(self, **kwargs):
        self.get_link_extractor()
        self.parse_args(kwargs)
        self.start_requests()

    def start_requests(self):
        if self.login_required:
            try:
                login_field_username = self.username_field_name
                login_field_password = self.password_field_name
            except AttributeError:
                raise CloseSpider('ERROR_MISSING_LOGIN_FIELD')

            self.login_form_data = {login_field_username: self.username,
                                    login_field_password: self.password}

            try:
                return [scrapy.Request(url=self.urls['login_page'], callback=self.log_in_spider)]
            except (AttributeError, KeyError):
                raise CloseSpider('ERROR_NO_LOGIN_PAGE')
        else:
            try:
                return [scrapy.Request(url=self.urls['start_page'], callback=self.parse_start_page)]
            except (AttributeError, KeyError):
                raise CloseSpider('ERROR_NO_START_PAGE')

    def log_in_spider(self, response):
        return scrapy.FormRequest.from_response(response,
                                                formdata=self.login_form_data,
                                                meta={'dont_redirect': True,
                                                      'handle_httpstatus_list': [302]},
                                                callback=self.after_login)

    @abstractmethod
    def is_login_success(self, response):
        pass

    def after_login(self, response):
        if not self.is_login_success(response):
            raise CloseSpider('ERROR_LOGIN_FAILED')
        try:
            return scrapy.Request(url=self.urls['start_page'],
                                  callback=self.parse_start_page,
                                  dont_filter=True)
        except (AttributeError, KeyError):
            raise CloseSpider('ERROR_NO_START_PAGE')

    @abstractmethod
    def get_forum_pages(self, response):
        pass

    def parse_start_page(self, response):
        for forum_page in self.get_forum_pages(response):
            yield scrapy.Request(
                url=forum_page.url,
                meta={'forum_page': forum_page},
                callback=self.parse_forum_page
            )

    @abstractmethod
    def get_thread_pages(self, response):
        pass

    @abstractmethod
    def get_next_forum_page(self, response):
        pass

    def parse_forum_page(self, response):
        forum_page = response.meta['forum_page']
        page_num   = forum_page.page

        is_valid_page = page_num >= self.min_page_num

        if is_valid_page:
            for thread_page in self.get_thread_pages(response):
                yield scrapy.Request(
                    url=thread_page.url,
                    meta={'forum_page' : forum_page,
                          'thread_page': thread_page},
                    callback=self.parse_thread_page
                )
            next_page_num = page_num + 1
        else:
            next_page_num = self.min_page_num
        get_next_page = next_page_num <= self.max_page_num

        if get_next_page:
            next_forum_page = self.get_next_forum_page(response, forum_page, next_page_num)

            if next_forum_page.url:
                yield scrapy.Request(
                    url=next_forum_page.url,
                    meta={'forum_page' : next_forum_page},
                    callback=self.parse_forum_page
                )

    def parse_thread_page(self, response):
        forum_page    = response.meta['forum_page']
        thread_page   = response.meta['thread_page']
        thread_author = self.get_thread_author(response)

        if not thread_page.start_date:
            thread_page.start_date = self.get_thread_start_date(response)

        file_links = self.link_extractor.extract_file_links(response.body)

        author_loader = AuthorLoader(item=AuthorItem())
        author_loader.add_value('name', thread_author.name)
        author_loader.add_value('join_date', thread_author.join_date)
        author_loader.add_value('total_posts', thread_author.total_posts)

        yield author_loader.load_item()

        thread_loader = ThreadLoader(item=ThreadItem())
        thread_loader.add_value('url', thread_page.url)
        thread_loader.add_value('name', thread_page.name)
        thread_loader.add_value('forum', forum_page.name)
        thread_loader.add_value('category', forum_page.category)
        thread_loader.add_value('start_date', thread_page.start_date)
        thread_loader.add_value('replies', thread_page.replies)
        thread_loader.add_value('views', thread_page.views)
        thread_loader.add_value('author_name', thread_author.name)

        yield thread_loader.load_item()

        for file_link in file_links:
            link_loader = LinkLoader(item=LinkItem())
            link_loader.add_value('url', file_link.url)
            link_loader.add_value('host', file_link.host)
            link_loader.add_value('thread_url', thread_page.url)

            yield link_loader.load_item()

        # DEBUG
        inspect_response(response, self)
