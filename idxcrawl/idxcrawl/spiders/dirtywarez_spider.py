from urllib.parse import urljoin

from idxcrawl.spiders.index_spider import IndexSpider
from idxcrawl.spiders.index_spider import Author
from idxcrawl.spiders.index_spider import Forum
from idxcrawl.spiders.index_spider import Thread

class DirtywarezSpider(IndexSpider):
    name = 'dirtywarez'

    login_required = True
    username_field_name = 'username'
    password_field_name = 'password'

    urls = {'start_page': 'http://forum.dirtywarez.com/index.php',
            'login_page': 'http://forum.dirtywarez.com/ucp.php?mode=login'}

    forums = {'Applications'      : 'software',
              'Games'             : 'software',
              'Movies'            : 'movies'  ,
              'TV Shows'          : 'tv'      ,
              'Anime'             : 'tv'      ,
              'Music'             : 'music'   ,
              'E-Books'           : 'ebooks'  ,
              'Web Developments'  : 'other'   ,
              'Non-Windows Warez' : 'software',
              'Recycle Bin'       : 'trash'   }

    def is_login_success(self, response):
        # If login is successful, the response contains the cookies |phpbb3_g836c_sid| and |phpbb3_g836c_u=X|, where X > 1.
        # If login fails, no new cookies are set.
        if not response.headers.getlist('Set-Cookie'):
            return False
        return True

    def get_forum_pages(self, response):
        forum_links = response.xpath(
            ('//body/div[@id="wrapc"]'
             '/div[@id="page-body"]'
             '/div[@class="forabg"]'
             '/div[@class="inner"]'
             '/ul[@class="topiclist forums"]'
             '/li[@class="row"]/dl/dt/'
             '/div[@class="list-inner"]'
             '/a[@class="forumtitle"][@href]')
        )

        for forum in self.forums:
            forum_link = forum_links.xpath('self::node()[text()="{}"]'.format(forum))
            forum_url  = urljoin(self.urls['start_page'],
                                 forum_link.xpath('./@href').extract_first())
            if forum_link:
                yield Forum(
                    name=forum,
                    page=1,
                    url=forum_url
                )

    def get_thread_pages(self, response):
        thread_rows = response.xpath(
            ('//body/div[@id="wrapc"]'
             '/div[@id="page-body"]'
             '/div[@class="forumbg"]'
             '/div[@class="inner"]'
             '/ul[@class="topiclist topics"]'
             '/li[contains(@class, "row")]'
             '/dl[contains(@class, "topic")]')
        )

        for thread_row in thread_rows:
            thread_inner       = thread_row.xpath('./dt/div[@class="list-inner"]')
            thread_link        = thread_inner.xpath('./a[@class="topictitle"][@href]')
            thread_author_link = thread_inner.xpath('./div[2]/a[contains(@class, "username")][@href]')

            thread_name = thread_link.xpath('./text()').extract_first()
            thread_url  = urljoin(self.urls['start_page'], thread_link.xpath('./@href').extract_first())

            thread_start_date  = thread_author_link.xpath('../text()[2]').extract_first()

            thread_replies = thread_row.xpath('./dd[@class="posts"]/text()').extract_first()
            thread_views   = thread_row.xpath('./dd[@class="views"]/text()').extract_first()

            yield Thread(
                name=thread_name,
                url=thread_url,
                start_date=thread_start_date,
                replies=thread_replies,
                views=thread_views
            )

    def get_thread_author(self, response):
        author_box = response.xpath(
            '(//body/div[@id="wrapc"]'
            '/div[@id="page-body"]'
            '/div[@id])[1]'
            '/div[@class="inner"]'
            '/dl[contains(@id, "profile")]'
        )

        author_name = author_box.xpath('./dt/a/text()').extract_first()
        author_url  = author_box.xpath('./dt/a/@href').extract_first()

        author_join_date   = urljoin(self.urls['start_page'],
                                     author_box.xpath('./dd[@class="profile-joined"]/text()').extract_first())
        author_total_posts = author_box.xpath('./dd[@class="profile-posts"]/a/text()').extract_first()
        author_rank        = author_box.xpath('./dd[@class="profile-rank"]/text()').extract_first()

        return Author(
            name=author_name,
            url=author_url,
            join_date=author_join_date,
            total_posts=author_total_posts,
            rank=author_rank
        )
