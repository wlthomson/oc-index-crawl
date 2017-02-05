from idxcrawl.spiders.index_spider import IndexSpider

class DirtywarezSpider(IndexSpider):
    name = 'dirtywarez'

    login_required = True
    username_field_name = 'username'
    password_field_name = 'password'

    urls = {'start_page': 'http://forum.dirtywarez.com/index.php',
            'login_page': 'http://forum.dirtywarez.com/ucp.php?mode=login'}

    def is_login_success(self, response):
        # If login is successful, the response contains the cookies |phpbb3_g836c_sid| and |phpbb3_g836c_u=X|, where X > 1.
        # If login fails, no new cookies are set.
        if not response.headers.getlist('Set-Cookie'):
            return False
        return True
