from idxcrawl.spiders.index_spider import IndexSpider

class WarezBBSpider(IndexSpider):
    name = 'warezbb'

    login_required = True
    username_field_name = 'username'
    password_field_name = 'password'

    urls = {'start_page': 'https://www.warez-bb.org',
            'login_page': 'https://www.warez-bb.org/login.php'}

    def is_login_success(self, response):
        # If login is successful, the response contains the cookies |phpBB_WBB_sid| and |phpBB_WBB_data|.
        # If login fails, no new cookies are set.
        if not response.headers.getlist('Set-Cookie'):
            return False
        return True
