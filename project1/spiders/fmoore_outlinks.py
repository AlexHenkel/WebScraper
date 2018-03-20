# -*- coding: utf-8 -*-
import scrapy
import re

index = 0
disallowedUrls = []
disallowedExtensions = ['.pdf', '.xlsx', '.jpg', '.gif']
allowed_domains = ['lyle.smu.edu', 's2.smu.edu']


class FmooreOutlinksSpider(scrapy.Spider):
    name = 'fmoore-outlinks'
    start_urls = [
        'http://lyle.smu.edu/~fmoore/robots.txt', 'http://lyle.smu.edu/~fmoore/']

    def parse(self, response):
        if "PAGE_LIMIT" in self.settings.attributes and index == int(self.settings.attributes['PAGE_LIMIT'].value):
            return

        global index
        global disallowedUrls

        # Verify if site is allowed to crawl
        allowedSite = False
        if "http" in response.url:
            for domain in allowed_domains:
                if domain in response.url:
                    allowedSite = True
                    break
        else:
            allowedSite = True

        # Filter disallowed domains and yield content
        if not allowedSite:
            yield {
                'outgoing-link': response.url,
                'title': str(response.css('title::text').extract_first())
            }
            return

        # Verify if file is robots.txt
        if response.url.endswith("robots.txt"):
            global disallowedUrls
            robotsText = response.css('*::text').extract_first()
            disallowed = re.findall('Disallow: .*', robotsText)
            for rule in disallowed:
                route = re.match("^([^/.]+)(.*)$", rule)
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
            yield response.follow(link, callback=self.parse)
