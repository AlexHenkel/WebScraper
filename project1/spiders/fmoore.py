# -*- coding: utf-8 -*-
import scrapy
import re
import hashlib
import string
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from utils import stop_words, filter_word

index = 0
disallowedUrls = []
disallowedExtensions = ['.pdf', '.xlsx', '.jpg', '.gif']
hashedFiles = []
main_dict = []
title_dict = []
info_dict = []


class FmooreSpider(scrapy.Spider):
    name = 'fmoore'
    allowed_domains = ['lyle.smu.edu', 's2.smu.edu']
    start_urls = [
        'http://lyle.smu.edu/~fmoore/robots.txt', 'http://lyle.smu.edu/~fmoore/']

    def __init__(self):
        dispatcher.connect(self.on_quit, signals.spider_closed)

    def on_quit(self, spider):
        print title_dict
        print main_dict
        print info_dict

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
            for word in str(title_tag).split():
                new_token = filter_word(word)
                if new_token:
                    local_title.append(new_token)

        global main_dict
        global title_dict
        global info_dict
        main_dict.append(local_list)
        title_dict.append(local_title)
        info_dict.append({'doc': index})

        # Get all urls, print them and visit them
        for link in response.css('a::attr(href)').extract():
            yield response.follow(link, callback=self.parse)
