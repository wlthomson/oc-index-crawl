import re
from urllib.parse import urljoin

from idxcrawl.spiders.index_spider import IndexSpider

from idxcrawl.items import ForumPage
from idxcrawl.items import ThreadPage

class TehParadoxSpider(IndexSpider):
    name = 'tehparadox'

    login_required = True
    username_field_name = 'vb_login_username'
    password_field_name = 'vb_login_password'

    urls = {'start_page': 'http://tehparadox.com/forum',
            'login_page': 'http://tehparadox.com/forum/login.php?do=login'}

    forums = {'Applications'         : 'software',
              'Games'                : 'software',
              'Movies'               : 'movies'  ,
              'TV Shows'             : 'tv'      ,
              'Anime'                : 'tv'      ,
              'Music'                : 'music'   ,
              'E-Books & Tutorials'  : 'ebooks'  ,
              'Web/Design Resources' : 'other'   ,
              'Trash Bin'            : 'trash'   }

    def is_login_success(self, response):
        # If login is successful, the response contains the cookie |vbseo_loggedin=yes|.
        # If login fails, the response contains the cookie |vbseo_loggedin=deleted|.
        for header in response.headers.getlist('Set-Cookie'):
            if 'vbseo_loggedin=yes' in header.decode('utf-8'):
                return True
        return False

    def get_forum_pages(self, response):
        forum_links = response.xpath(
            ('//body/div[@id="page"]'
             '/div[@id="main"]'
             '/div[@class="page"]'
             '/table[@class="tborder"]'
             '/tbody/tr/td/div/a[@href]')
        )

        for forum in self.forums:
            forum_link = forum_links.xpath('./strong[text()="{}"]/parent::a'.format(forum))
            forum_url  = urljoin(self.urls['start_page'],
                                 forum_link.xpath('.//@href').extract_first())
            if forum_link:
                yield ForumPage(
                    name=forum,
                    page=1,
                    url=forum_url
                )


    def get_thread_pages(self, response):
        thread_rows = response.xpath(
            ('//body/div[@id="page"]'
             '/div[@id="main"]'
             '/div[@class="page"]'
             '/form[@id="inlinemodform"]'
             '/table[@id="threadslist"]'
             '//tr[contains(@class,"alt")]')
        )

        for thread_row in thread_rows:
            thread_inner = thread_row.xpath('./td[contains(@id, "threadtitle")]')
            thread_link = thread_inner.xpath('./div/a[contains(@id, "thread_title")]')
            thread_author_link = thread_inner.xpath('./div[@class="smallfont"]/span')
            thread_replies_views = thread_row.xpath('td[preceding-sibling::td[not(@id)][@title]]')

            thread_name = thread_link.xpath('./text()').extract_first()
            thread_url  = urljoin(self.urls['start_page'], thread_link.xpath('./@href').extract_first())

            thread_start_date = None

            thread_author_name = thread_author_link.xpath('./text()').extract_first()
            thread_author_url  = re.search('{}/members/\w*/'.format(self.urls['start_page']),
                                           thread_author_link.xpath('./@onclick').extract_first()).group()

            thread_replies, thread_views = thread_replies_views.xpath('./text()').extract()

            yield ThreadPage(
                name=thread_name,
                url=thread_url,
                author_name=thread_author_name,
                author_url=thread_author_url,
                start_date=thread_start_date,
                replies=thread_replies,
                views=thread_views
            )

    def get_thread_start_date(self, response):
        start_date = ''.join(
            response.xpath(
                ('(//body/div[@id="page"]'
                 '/div[@id="main"]/div[@id="posts"]'
                 '/div[@class="page"]/div[@id]'
                 '/table[@id]/tr/td)[1]/text()')
            ).extract())

        return start_date
