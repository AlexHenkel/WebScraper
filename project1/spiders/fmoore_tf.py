# -*- coding: utf-8 -*-
import scrapy
import re
import string
from nltk import PorterStemmer
from nltk.corpus import stopwords

index = 0
disallowedUrls = []
disallowedExtensions = ['.pdf', '.xlsx', '.jpg', '.gif']
stop_words = set(stopwords.words('english'))


class FmooreTfSpider(scrapy.Spider):
    name = 'fmoore-tf'
    allowed_domains = ['lyle.smu.edu', 's2.smu.edu']
    start_urls = [
        'http://lyle.smu.edu/~fmoore/robots.txt', 'http://lyle.smu.edu/~fmoore/']

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

        # Filter empty words and stop words. Start indexing
        urlContent = map(lambda x: str(
            x.strip()), response.css('*:not(style):not(script)::text').extract())
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

        # Get all urls, and visit them
        for link in response.css('a::attr(href)').extract():
            yield response.follow(link, callback=self.parse)
