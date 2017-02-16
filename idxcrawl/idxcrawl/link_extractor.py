import re

from bs4 import BeautifulSoup

class FileLink:
    def __init__(self, host=None, url=None):
        self.host = host
        self.url  = url

class LinkExtractor:
    def __init__(self, hosts_file):
        self.host_names = [host.rstrip() for host in hosts_file]
        self.host_regexes = [(host_name, 'https?://(?:www\.|\w\d{2}\.|download\.)?' + host_name +
                              '\.[a-z]{2,}/[\w~!@#$%&()\-_+=\[\]:;\',.?/]+?(?:(?:\.html)|(?=http|[\s\],<]|$))')
                             for host_name in self.host_names]

    def extract_file_links(self, html):
        response_soup = BeautifulSoup(html, 'lxml')

        for br in response_soup.findAll('br'):
            br.replaceWith('\n')

        try:
            for hostname, host_regex in self.host_regexes:
                for file_link in re.findall(host_regex, response_soup.text):
                    yield FileLink(hostname, file_link)
        except TypeError:
            return []
