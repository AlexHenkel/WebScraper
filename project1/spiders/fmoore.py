# -*- coding: utf-8 -*-
import scrapy
import re
from nltk import PorterStemmer

index = 0
disallowedUrls = []


class FmooreSpider(scrapy.Spider):
    name = 'fmoore'
    allowed_domains = ['lyle.smu.edu', 's2.smu.edu']
    start_urls = [
        'http://lyle.smu.edu/~fmoore/robots.txt', 'http://lyle.smu.edu/~fmoore/']
    custom_settings = {
        'DUPEFILTER_DEBUG': True
    }

    def parse(self, response):
        global index
        global disallowedUrls

        # Verify if file is robots.txt
        if response.url.endswith("robots.txt"):
            global disallowedUrls
            robotsText = response.css('*::text').extract_first()
            disallowed = re.findall('Disallow: .*', robotsText)
            for rule in disallowed:
                route = re.match("^([^/.]+)(.*)$", rule)
                disallowedUrls.append(str(route.group(2)))
            return

        # Blacklist disallowedUrls
        for url in disallowedUrls:
            if url in response.url:
                return
        index = index + 1
        doc = "Doc{}".format(index)
        print('url @{} {}'.format(doc, response.url))
        for text in filter(lambda x: x, map(lambda x: str(
                x.strip()), response.css('*:not(style):not(script)::text').extract())):
            for word in text.split():
                yield {
                    'word': PorterStemmer().stem(word),
                    'doc': doc
                }
        for link in response.css('a::attr(href)').extract():
            print('link: {}'.format(str(link)))
            yield response.follow(link, callback=self.parse)
