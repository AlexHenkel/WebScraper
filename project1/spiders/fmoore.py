# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class FmooreSpider(CrawlSpider):
    name = 'fmoore'
    allowed_domains = ['lyle.smu.edu']
    start_urls = ['http://lyle.smu.edu/~fmoore/']

    rules = (
        Rule(LinkExtractor(allow=()),
             callback="parse_item",
             follow=True),)

    def parse_item(self, response):
        print('Processing..' + response.url)
