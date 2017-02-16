from abc import ABCMeta, abstractmethod

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.shell import inspect_response

from idxcrawl.link_extractor import LinkExtractor

class IndexSpider(scrapy.Spider):
    __metaclass__ = ABCMeta

    def get_link_extractor(self):
        try:
            hosts_file = open('hosts.txt', 'r')
        except FileNotFoundError:
            raise CloseSpider('ERROR_NO_HOSTS_FILE')
        self.link_extractor = LinkExtractor(hosts_file)
        hosts_file.close()

    def parse_args(self, kwargs):
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')

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
                url=forum_page['url'],
                meta={'forum_page': forum_page},
                callback=self.parse_forum_page
            )

    @abstractmethod
    def get_thread_pages(self, response):
        pass

    def parse_forum_page(self, response):
        forum_page = response.meta['forum_page']

        for thread_page in self.get_thread_pages(response):
            yield scrapy.Request(
                url=thread_page['url'],
                meta={'forum_page' : forum_page,
                      'thread_page': thread_page},
                callback=self.parse_thread_page
            )

    def parse_thread_page(self, response):
        forum_page    = response.meta['forum_page']
        thread_page   = response.meta['thread_page']
        thread_author = self.get_thread_author(response)

        if not thread_page['start_date']:
            thread_page['start_date'] = self.get_thread_start_date(response)

        file_links = self.link_extractor.extract_file_links(response.body)

        # DEBUG
        response.meta['thread_author'] = thread_author
        response.meta['file_links'] = file_links
        inspect_response(response, self)
