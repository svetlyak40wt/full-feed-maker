#!/usr/bin/env python
"""
    Simple full feed maker for http://8020photo.com
"""
import sys
import logging
from lxml import etree as ET
from lxml import html

def process_feed(input, output, limit = 5):
    log = logging.getLogger('feed-maker')

    log.debug('processing "%s"' % input)
    xml = ET.parse(input)
    items = xml.findall('channel/item')

    for item in items[:limit]:
        url = item.find('link').text

        log.debug('downloading content from "%s"' % url)
        page = html.parse(url)

        content = page.find("//div[@class='post']//div[@class='content']")
        sociallist = content.find("div[@class='sociallist']")
        content.remove(sociallist)

        item.find('description').text = ET.CDATA(ET.tostring(content))

    # remove ignored items
    channel = xml.find('channel')
    for item in items[limit:]:
        channel.remove(item)

    log.debug('writing to "%s"' % output)
    xml.write(output)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    process_feed(sys.argv[1], sys.argv[2])
