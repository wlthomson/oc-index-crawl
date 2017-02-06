from urllib.parse import urljoin

from idxcrawl.spiders.index_spider import IndexSpider

from idxcrawl.items import ForumPage

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
                yield ForumPage(
                    name=forum,
                    page=1,
                    url=forum_url
                )
