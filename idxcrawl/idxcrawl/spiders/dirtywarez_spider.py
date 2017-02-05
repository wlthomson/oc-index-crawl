from idxcrawl.spiders.index_spider import IndexSpider

class DirtywarezSpider(IndexSpider):
    name = 'dirtywarez'

    login_required = True
    username_field_name = 'username'
    password_field_name = 'password'

    urls = {'start_page': 'http://forum.dirtywarez.com/index.php',
            'login_page': 'http://forum.dirtywarez.com/ucp.php?mode=login'}
