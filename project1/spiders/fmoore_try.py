# -*- coding: utf-8 -*-
import scrapy
from nltk import PorterStemmer

index = 0


class FmooreTrySpider(scrapy.Spider):
    name = 'fmoore-try'
    allowed_domains = ['lyle.smu.edu']
    start_urls = ['http://lyle.smu.edu/~fmoore']

    def parse(self, response):
        global index
        index = index + 1
        for text in filter(lambda x: x, map(lambda x: str(
                x.strip()), response.css('*::text').extract())):
            doc = "Doc{}".format(index)
            for word in text.split():
                yield {
                    'word': PorterStemmer().stem(word),
                    'doc': doc
                }
        for link in response.css('a::attr(href)').extract():
            print('link: {}'.format(str(link)))
            yield response.follow(link, callback=self.parse)
        print('url {}'.format(response.url))
