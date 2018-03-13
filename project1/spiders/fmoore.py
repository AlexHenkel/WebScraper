# -*- coding: utf-8 -*-
import scrapy
import re
import hashlib
from nltk import PorterStemmer

index = 0
disallowedUrls = []
disallowedExtensions = ['.pdf', '.xlsx', '.jpg', '.gif']
hashedFiles = []


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

        # Blacklist disallowed Urls
        for url in disallowedUrls:
            if url in response.url:
                return
        # Blacklist disallowed Extensions
        for disallowedExt in disallowedExtensions:
            if response.url.endswith(disallowedExt):
                return

        index = index + 1
        doc = "Doc{}".format(index)
        print('url @{} {}'.format(doc, response.url))

        # Verify exact duplicates
        urlContent = map(lambda x: str(
            x.strip()), response.css('*:not(style):not(script)::text').extract())
        hashKey = hashlib.md5("".join(urlContent)).hexdigest()
        if hashKey in hashedFiles:
            print('{} is an exact duplicate from Doc{}'.format(
                doc, hashedFiles.index(hashKey) + 1))
        hashedFiles.append(hashKey)

        # Filter empty words and start indexing
        for text in filter(lambda x: x, urlContent):
            for word in text.split():
                yield {
                    'word': PorterStemmer().stem(word),
                    'doc': doc
                }

        # Get all urls, print them and visit them
        for link in response.css('a::attr(href)').extract():
            print('link: {}'.format(str(link)))
            yield response.follow(link, callback=self.parse)
