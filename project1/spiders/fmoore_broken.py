# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.spidermiddlewares.httperror import HttpError

index = 0
disallowedUrls = []
disallowedExtensions = ['.pdf', '.xlsx', '.jpg', '.gif']


class FmooreBrokenSpider(scrapy.Spider):
    name = 'fmoore-broken'
    allowed_domains = ['lyle.smu.edu', 's2.smu.edu']
    start_urls = [
        'http://lyle.smu.edu/~fmoore/robots.txt', 'http://lyle.smu.edu/~fmoore/']

    def err_callbck(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            yield {'broken-link': response.url}

    def parse(self, response):
        if "PAGE_LIMIT" in self.settings.attributes and index == int(self.settings.attributes['PAGE_LIMIT'].value):
            return

        global index
        global disallowedUrls

        # Verify if file is robots.txt
        if response.url.endswith("robots.txt"):
            global disallowedUrls
            robotsText = response.css('*::text').extract_first()
            lines = robotsText.splitlines()
            for line in lines:
                if str(line).startswith('Disallow: '):
                    route = re.match("^([^/.]+)(.*)$", str(line))
                    disallowedUrls.append(str(route.group(2)))
            return

        # Blacklist disallowed Urls
        for url in disallowedUrls:
            if url in response.url:
                return
        # Blacklist disallowed Extensions
        for disallowedExt in disallowedExtensions:
            if response.url.endswith(disallowedExt):
                return

        index = index + 1
        # Get all urls, print them and visit them
        for link in response.css('a::attr(href)').extract():
            yield response.follow(link, callback=self.parse, errback=self.err_callbck)
