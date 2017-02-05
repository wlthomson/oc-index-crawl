from abc import ABCMeta, abstractmethod

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.shell import inspect_response

class IndexSpider(scrapy.Spider):
    __metaclass__ = ABCMeta

    def parse_args(self, kwargs):
        self.username = kwargs.get('username', '')
        self.password = kwargs.get('password', '')

    def __init__(self, **kwargs):
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
            return scrapy.Request(url=self.urls['start_page'], callback=self.parse_start_page)
        except (AttributeError, KeyError):
            raise CloseSpider('ERROR_NO_START_PAGE')

    def parse_start_page(self, response):
        # DEBUG
        inspect_response(response, self)
