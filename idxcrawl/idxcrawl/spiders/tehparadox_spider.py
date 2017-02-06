from urllib.parse import urljoin

from idxcrawl.spiders.index_spider import IndexSpider

from idxcrawl.items import ForumPage

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
