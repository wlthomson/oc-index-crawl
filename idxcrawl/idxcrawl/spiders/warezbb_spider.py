from idxcrawl.spiders.index_spider import IndexSpider

class WarezBBSpider(IndexSpider):
    name = 'warezbb'

    login_required = True
    username_field_name = 'username'
    password_field_name = 'password'

    urls = {'start_page': 'https://www.warez-bb.org',
            'login_page': 'https://www.warez-bb.org/login.php'}
