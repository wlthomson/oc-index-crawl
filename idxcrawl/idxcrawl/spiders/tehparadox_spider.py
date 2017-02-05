from idxcrawl.spiders.index_spider import IndexSpider

class TehParadoxSpider(IndexSpider):
    name = 'tehparadox'

    login_required = True
    username_field_name = 'vb_login_username'
    password_field_name = 'vb_login_password'

    urls = {'start_page': 'http://tehparadox.com',
            'login_page': 'http://tehparadox.com/forum/login.php?do=login'}

    def is_login_success(self, response):
        # If login is successful, the response contains the cookie |vbseo_loggedin=yes|.
        # If login fails, the response contains the cookie |vbseo_loggedin=deleted|.
        for header in response.headers.getlist('Set-Cookie'):
            if 'vbseo_loggedin=yes' in header.decode('utf-8'):
                return True
        return False
