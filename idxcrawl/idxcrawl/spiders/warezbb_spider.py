from urllib.parse import urljoin

from idxcrawl.spiders.index_spider import IndexSpider
from idxcrawl.spiders.index_spider import Author
from idxcrawl.spiders.index_spider import Forum
from idxcrawl.spiders.index_spider import Thread

class WarezBBSpider(IndexSpider):
    name = 'warezbb'

    login_required = True
    username_field_name = 'username'
    password_field_name = 'password'

    urls = {'start_page': 'https://www.warez-bb.org',
            'login_page': 'https://www.warez-bb.org/login.php'}

    forums = {'Apps'                  : 'software',
              'Games'                 : 'software',
              'Console Games'         : 'software',
              'Movies'                : 'movies'  ,
              'TV Shows'              : 'tv'      ,
              'Anime'                 : 'tv'      ,
              'Music'                 : 'music'   ,
              'Music Videos'          : 'music'   ,
              'Templates and Scripts' : 'other'   ,
              'eBooks'                : 'ebooks'  ,
              'Audiobooks'            : 'other'   ,
              'Tutorials'             : 'other'   ,
              'Mac'                   : 'software',
              'Mobile'                : 'software',
              'Other OSes'            : 'software'}

    def is_login_success(self, response):
        # If login is successful, the response contains the cookies |phpBB_WBB_sid| and |phpBB_WBB_data|.
        # If login fails, no new cookies are set.
        if not response.headers.getlist('Set-Cookie'):
            return False
        return True

    def get_forum_pages(self, response):
        forum_links = response.xpath(
            ('//body/div[@id="main-content"]'
             '/div[@class="wrap"]'
             '/div[@id="index-page"]'
             '/div[@id="forum-"]'
             '/div[@id="subforum-"]'
             '/div[@class="name"]'
             '/span/strong/a[@href]')
        )

        for forum in self.forums:
            forum_link = forum_links.xpath('self::node()[text()="{}"]'.format(forum))
            forum_url  = urljoin(self.urls['start_page'],
                                 forum_link.xpath('./@href').extract_first())
            if forum_link:
                yield Forum(
                    name=forum,
                    category=self.forums[forum],
                    page=1,
                    url=forum_url
                )

    def get_thread_pages(self, response):
        thread_rows = response.xpath(
            ('//body/div[@id="main-content"]'
             '/div[@class="wrap"]'
             '/div[@class="list-wrap"]'
             '/div[@class="list-rows"][preceding-sibling::div[@class="cat-row"][span/text()="Topics"]]'
             '/div[@class="topicrow"]'
            )
        )

        for thread_row in thread_rows:
            thread_link = thread_row.xpath(
                ('./div[@class="description"]'
                 '/span/span[@class="title"]'
                 '/a[@class="topictitle"]'
                )
            )
            thread_author_link = thread_row.xpath(
                ('./div[@class="posts"]'
                 '/span/a[@href]')
            )

            thread_name = thread_link.xpath('./text()').extract_first()
            thread_url  = urljoin(self.urls['start_page'], thread_link.xpath('./@href').extract_first())

            thread_start_date = None

            thread_author_name = thread_author_link.xpath('./text()').extract_first()
            thread_author_url  = urljoin(self.urls['start_page'], thread_author_link.xpath('./@href').extract_first())

            thread_replies = thread_row.xpath('./div[@class="topics"]/span/text()').extract_first()
            thread_views   = thread_row.xpath('./div[@class="views"]/span/text()').extract_first()

            yield Thread(
                name=thread_name,
                url=thread_url,
                author_name=thread_author_name,
                author_url=thread_author_url,
                start_date=thread_start_date,
                replies=thread_replies,
                views=thread_views
            )

    def get_thread_start_date(self, response):
        start_date = response.xpath(
            ('(//body/div[@id="main-content"]'
             '/div[@id="viewtopic"]/div[@class="wrap"]'
             '/div[@class="topic-rows"]/div[@id])[1]'
             '/div[@class="message-content"]'
             '/div[@class="tools"]/div[@class="date"]'
             '/a[@href]/text()')
        ).extract_first()

        return start_date
