from idxcrawl.spiders.index_spider import IndexSpider

class TehParadoxSpider(IndexSpider):
    name = 'tehparadox'

    login_required = True
    username_field_name = 'vb_login_username'
    password_field_name = 'vb_login_password'

    urls = {'start_page': 'http://tehparadox.com',
            'login_page': 'http://tehparadox.com/forum/login.php?do=login'}
