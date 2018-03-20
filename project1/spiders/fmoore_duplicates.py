# -*- coding: utf-8 -*-
import scrapy
import re
import hashlib

index = 0
disallowedUrls = []
disallowedExtensions = ['.pdf', '.xlsx', '.jpg', '.gif']
hashedFiles = {}


class FmooreDuplicatesSpider(scrapy.Spider):
    name = 'fmoore-duplicates'
    allowed_domains = ['lyle.smu.edu', 's2.smu.edu']
    start_urls = [
        'http://lyle.smu.edu/~fmoore/robots.txt', 'http://lyle.smu.edu/~fmoore/']

    def parse(self, response):
        if "PAGE_LIMIT" in self.settings.attributes and index == int(self.settings.attributes['PAGE_LIMIT'].value):
            return

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

        # Blacklist disallowed Urls
        for url in disallowedUrls:
            if url in response.url:
                return
        # Blacklist disallowed Extensions
        for disallowedExt in disallowedExtensions:
            if response.url.endswith(disallowedExt):
                return

        # Verify exact duplicates
        urlContent = map(lambda x: str(
            x.strip()), response.css('*:not(style):not(script)::text').extract())
        hashKey = hashlib.md5("".join(urlContent)).hexdigest()
        if hashKey in hashedFiles:
            yield {
                'duplicate': response.url,
                'original': hashedFiles[hashKey]
            }
        else:
            hashedFiles[hashKey] = response.url

        index = index + 1
        # Get all urls, print them and visit them
        for link in response.css('a::attr(href)').extract():
            yield response.follow(link, callback=self.parse)
