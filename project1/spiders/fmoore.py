# -*- coding: utf-8 -*-
import scrapy
import re
import hashlib
import string
from scrapy.spidermiddlewares.httperror import HttpError
from nltk import PorterStemmer
from nltk.corpus import stopwords

index = 0
disallowedUrls = []
disallowedExtensions = ['.pdf', '.xlsx', '.jpg', '.gif']
hashedFiles = []
stop_words = set(stopwords.words('english'))


class FmooreSpider(scrapy.Spider):
    name = 'fmoore'
    allowed_domains = ['lyle.smu.edu', 's2.smu.edu']
    start_urls = [
        'http://lyle.smu.edu/~fmoore/robots.txt', 'http://lyle.smu.edu/~fmoore/']

    def err_callbck(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            print('Error on {}'.format(response.url))

    def parse(self, response):
        if "PAGE_LIMIT" in self.settings.attributes and index == int(self.settings.attributes['PAGE_LIMIT'].value):
            return

        if "STOP_WORDS" in self.settings.attributes:
            global stop_words
            stop_words = self.settings.attributes['STOP_WORDS'].value.split(
                ',')

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

        # Filter empty words and stop words. Start indexing
        for text in filter(lambda x: x, urlContent):
            for word in text.split():
                word = word.lower()
                # Filter tokens that don't start with letters
                if not word or not word[0].isalpha():
                    continue

                # If word ends with sign, remove it
                while word and word[-1] in string.punctuation:
                    word = word[:-1]
                if not word:
                    continue

                # Filter stop words
                if word in stop_words:
                    continue

                # Apply Porter Stemmer to word and construct and return item
                yield {
                    'word': PorterStemmer().stem(word),
                    'doc': doc
                }

        # Get all urls, print them and visit them
        for link in response.css('a::attr(href)').extract():
            print('link: {}'.format(str(link)))
            yield response.follow(link, callback=self.parse, errback=self.err_callbck)
