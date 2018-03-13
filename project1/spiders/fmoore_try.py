# -*- coding: utf-8 -*-
import scrapy
from nltk import PorterStemmer


class FmooreTrySpider(scrapy.Spider):
    name = 'fmoore-try'
    allowed_domains = ['lyle.smu.edu']
    start_urls = ['http://lyle.smu.edu/~fmoore']

    def parse(self, response):
        for text in filter(lambda x: x, map(lambda x: str(
                x.strip()), response.css('*::text').extract())):
            page = response.url
            for word in text.split():
                yield {
                    page: PorterStemmer().stem(word)
                }
