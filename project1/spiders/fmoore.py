# -*- coding: utf-8 -*-
import scrapy
import re
import hashlib
import string
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy import signals
from utils import stop_words, filter_word
from search_engine import start_search_engine
from defaults import words, titles, titles_tokenized, urls

index = 0
disallowedUrls = []
disallowedExtensions = ['.pdf', '.xlsx', '.jpg', '.gif']
hashedFiles = []
docs_list = []
title_tokenized_list = []
title_list = []
url_list = []


class FmooreSpider(scrapy.Spider):
    name = 'fmoore'
    allowed_domains = ['lyle.smu.edu', 's2.smu.edu']
    start_urls = [
        'http://lyle.smu.edu/~fmoore/robots.txt', 'http://lyle.smu.edu/~fmoore/']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FmooreSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(spider.on_quit, signals.spider_closed)
        crawler.signals.connect(spider.on_start, signals.spider_opened)
        return spider

    def on_start(self):
        print "Loading... We are retrieving your data\n"

    def on_quit(self):
        start_search_engine(docs_list, title_list,
                            title_tokenized_list, url_list)

    def parse(self, response):
        if "DEFAULT_SEARCH_ENGINE" in self.settings.attributes:
            global docs_list
            global title_tokenized_list
            global title_list
            global url_list
            print "You are using default information. Remove DEFAULT_SEARCH_ENGINE=1 flag to use info directly from crawler\n"
            docs_list = words
            title_list = titles
            title_tokenized_list = titles_tokenized
            url_list = urls
            return

        if "STOP_WORDS" in self.settings.attributes:
            global stop_words
            stop_words = self.settings.attributes['STOP_WORDS'].value.split(
                ',')
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

        # Verify exact duplicates
        urlContent = map(lambda x: str(
            x.strip()), response.css('*:not(style):not(script)::text').extract())
        hashKey = hashlib.md5("".join(urlContent)).hexdigest()
        if hashKey in hashedFiles:
            return
        hashedFiles.append(hashKey)

        local_list = []
        # Filter empty words and stop words. Start indexing
        for text in filter(lambda x: x, urlContent):
            for word in text.split():
                new_token = filter_word(word)
                if new_token:
                    local_list.append(new_token)

        # Filter empty words and stop words from <title> tags
        title_tag = response.css('title::text').extract_first()
        local_title = []
        if title_tag:
            title_tag = str(title_tag)
            for word in str(title_tag).split():
                new_token = filter_word(word)
                if new_token:
                    local_title.append(new_token)

        docs_list.append(local_list)
        title_tokenized_list.append(local_title)
        title_list.append(title_tag)
        url_list.append(response.url)

        # Get all urls, print them and visit them
        for link in response.css('a::attr(href)').extract():
            yield response.follow(link, callback=self.parse)
