#!/usr/bin/env python
"""
    Simple full feed maker for those sited, which has 'stripped' RSS/Atom feeds.
    Author: Alexander Artemenko <svetlyak.40wt@gmail.com>
    Site: http://github.com/svetlyak40wt/
"""
import sys
import logging
import urllib2
import pdb

from lxml import etree as ET
from lxml import html

__version__ = '0.0.1'
__all__ = ['__version__', 'FullFeedMaker', 'Full2080']

class FullFeedMaker(object):
    feed_url = None
    output_file = None
    limit = 20
    headers = {
        'User-agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en; rv:1.9.1)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru,en;q=0.5',
    }

    def __init__(self, debug = False):
        if debug:
            h = urllib2.HTTPHandler(debuglevel=1)
            self.opener = urllib2.build_opener(h)
        else:
            self.opener = urllib2.build_opener()

    def process(self):
        log = logging.getLogger('feed-maker')

        if not self.feed_url:
            raise RuntimeError('Please, define "feed_url"')
        if not self.output_file:
            raise RuntimeError('Please, define "output_file"')

        log.debug('processing "%s"' % self.feed_url)
        try:
            xml = ET.parse(self._urlopen(self.feed_url))
        except Exception, e:
            pdb.set_trace()
        channel = xml.find('channel')
        items = channel.findall('item')

        for item in items[:self.limit]:
            url = item.find('link').text
            log.debug('downloading content from "%s"' % url)
            item.find('description').text = ET.CDATA(
                self.get_description(html.parse(self._urlopen(url))))

        # remove ignored items
        for item in items[self.limit:]:
            channel.remove(item)

        log.debug('writing to "%s"' % self.output_file)
        xml.write(self.output_file)


    def _urlopen(self, url):
        request = urllib2.Request(url)
        for name, value in self.headers.iteritems():
            request.add_header(name, value)
        return self.opener.open(request)


    def get_description(self, html):
        """
            Returns unicode string with item description.
            @param html parsed HTML page from linked page.
            @return unicode string with item description.
        """
        raise NotImplementedError('Implement "get_description" method')


class Full8020(FullFeedMaker):
    """Example feed maker for site http://8020photo.com"""

    feed_url = 'http://8020photo.com/feed/'
    limit = 10

    def __init__(self, output_file):
        super(Full8020, self).__init__()
        self.output_file = output_file

    def get_description(self, html):
        content = html.find("//div[@class='post']//div[@class='content']")
        sociallist = content.find("div[@class='sociallist']")
        content.remove(sociallist)
        return ET.tostring(content)

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    Full8020(output_file = sys.argv[1]).process()

