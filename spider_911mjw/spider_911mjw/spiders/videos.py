import scrapy
import sys
import os
import re
import random
import time
import json
import logging
import parse
from spider_911mjw.items import VideoItem
from urllib.parse import urlparse, urljoin
from datetime import datetime
from scrapy.exceptions import NotConfigured

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))

class VideosSpider(scrapy.Spider):
    name = 'videos'
    page_path_format = 'index{page_index}.html'
    spider_title_list = ['美剧', '电影', '纪录片', '真人秀']

    def __init__(self, base_url='https://www.911mjw.com/', page_limit_count=1, video_limit_count=-1, *args, **kwargs):
        super(VideosSpider, self).__init__(*args, **kwargs)
        self.base_url = base_url
        self.start_urls = []
        if base_url:
            self.start_urls.append(base_url)
        self.page_limit_count = int(page_limit_count)
        self.video_limit_count = int(video_limit_count)

    def parse(self, response):
        self.logger.info(f'base_url: {self.base_url}, page_limit_count: {self.page_limit_count}, video_limit_count: {self.video_limit_count}')
        a_list = response.xpath('//*[@class="nav"]/li/a')
        for a_selector in a_list:
            top_title = a_selector.css('::text').get().strip()
            if top_title in self.spider_title_list:
                base_page_path = a_selector.attrib["href"]
                yield response.follow(a_selector, self.parse_first_videos_page, cb_kwargs={"top_title": top_title, 'base_page_path': base_page_path}, dont_filter=True)
            else:
                self.logger.warning(f'ignore title {top_title}')

    def parse_page_count(self, response):
        page_count_str = response.css('.pagination').xpath('ul/li[last()]').css('::text').get()
        res = parse.findall('{:d}', page_count_str)
        page_count = -1
        if res:
            for c in res:
                page_count = c[0]
        if page_count < 0:
            self.logger.warning(f'parse page count failed, set page count is 1')
            page_count = 1
        return page_count

    def get_page_url(self, base_page_path, page_index):
        return urljoin(urljoin(self.base_url, base_page_path), self.page_path_format.format(page_index=page_index))

    def parse_first_videos_page(self, response, top_title, base_page_path):
        page_index = 1
        page_count = self.parse_page_count(response)
        self.logger.info(f'found title {top_title}, page_path: {base_page_path}, page_count: {self.page_limit_count}/{page_count}')
        while page_index <= page_count and page_index <= self.page_limit_count:
            page_url = self.get_page_url(base_page_path, page_index)
            yield scrapy.Request(page_url, self.parse_videos_page, cb_kwargs={"top_title": top_title}, dont_filter=True)
            page_index += 1

    def parse_videos_page(self, response, top_title):
        movie_list = response.css('.u-movie')
        movie_count = 0
        self.logger.info(f'parse video url: {response.url}, found movie count: {self.video_limit_count}/{len(movie_list)}')
        for movie_selector in movie_list:
            movie_count += 1
            a_info = movie_selector.xpath('a')
            movie_name = a_info.attrib['title']
            movie_path = a_info.attrib['href']
            movie_url = urljoin(self.base_url, movie_path)
            item = VideoItem()
            item['name'] = movie_name
            self.logger.info(f'movie_path: {movie_path}, movie_name: {movie_name}')
            yield response.follow(movie_path, self.parse_video_info, cb_kwargs={"top_title": top_title, "item": item}, dont_filter=True)
            if self.video_limit_count > 0 and movie_count >= self.video_limit_count:
                break

    def parse_video_info(self, response, top_title, item):
        return item
