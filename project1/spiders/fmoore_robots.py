# -*- coding: utf-8 -*-
import scrapy
import re

disallowedUrls = {}


class FmooreRobotsSpider(scrapy.Spider):
    name = 'fmoore-robots'
    allowed_domains = ['lyle.smu.edu']
    start_urls = ['http://lyle.smu.edu/~fmoore/robots.txt']

    def parse(self, response):
        global disallowedUrls
        robotsText = response.css('*::text').extract_first()
        disallowed = re.findall('Disallow: .*', robotsText)
        for rule in disallowed:
            route = re.match("^([^/.]+)(.*)$", rule)
            disallowedUrls[route.group(2)] = True
        print(disallowedUrls)
