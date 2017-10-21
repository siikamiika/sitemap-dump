#!/usr/bin/env python3
"""Sitemap url dumper with patterns"""

import argparse
import re
import sys
import requests
from bs4 import BeautifulSoup as BS


class Website(object):
    """A website with a sitemap"""

    def __init__(self, domain, protocol, sitemap_path, url_pattern):
        self.domain = domain
        self.protocol = protocol
        self.sitemap_path = sitemap_path
        self.url_pattern = re.compile(url_pattern) if url_pattern else None
        self.urls = set()

    def _download_sitemap(self, url):
        print('Downloading part {}'.format(url), file=sys.stderr)

        response = requests.get(url)
        sitemap = BS(response.text, 'lxml')

        def _match(text):
            if self.url_pattern is None:
                return True
            return self.url_pattern.match(text)

        self.urls |= set([url.loc.text for url in sitemap.urlset.find_all('url')
                          if _match(url.loc.text)])

    def download_sitemap(self):
        """Download urls matching url_pattern from the sitemaps in
        {protocol}://{domain}{sitemap_path}"""

        url = '{}://{}{}'.format(self.protocol, self.domain, self.sitemap_path)
        print('Downloading sitemap for {}'.format(url), file=sys.stderr)
        response = requests.get(url)
        sitemaps = BS(response.text, 'lxml')

        for sitemap in sitemaps.sitemapindex.find_all('sitemap'):
            while True:
                try:
                    self._download_sitemap(sitemap.loc.text)
                    break
                except Exception as e:
                    print(e, file=sys.stderr)
                    sys.stderr.write('Download failed. Retry? (Y/n): ')
                    if input() == 'n':
                        break

    def get_urls(self):
        """Get urls downloaded with Website.download_sitemap"""
        return self.urls

def main():
    """Print matching sitemap urls to stdout"""

    parser = argparse.ArgumentParser()
    parser.add_argument('domain')
    parser.add_argument('--protocol', '-p', nargs='?')
    parser.add_argument('--sitemap-path', '-m', nargs='?')
    parser.add_argument('--url-pattern', '-up', nargs='?')
    args = parser.parse_args()

    domain = args.domain
    protocol = args.protocol or 'http'
    sitemap_path = args.sitemap_path or '/sitemap.xml'
    url_pattern = args.url_pattern

    website = Website(domain, protocol, sitemap_path, url_pattern)
    website.download_sitemap()
    for url in website.get_urls():
        print(url)

    print('Done!', file=sys.stderr)

if __name__ == '__main__':
    main()
