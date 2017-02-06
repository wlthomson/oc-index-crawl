from urllib.parse import urljoin

from idxcrawl.spiders.index_spider import IndexSpider

from idxcrawl.items import ForumPage

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
                yield ForumPage(
                    name=forum,
                    page=1,
                    url=forum_url
                )
