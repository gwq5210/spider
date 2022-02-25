# 
import scrapy
import sys
import os
import re
import random
import time
import json
import logging
import parse
from spider_douban_house.items import HouseItem
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta
from scrapy.exceptions import NotConfigured

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))
print(os.path.abspath(os.path.dirname(os.getcwd())))

from mirai_client import MiraiClient

class HouseSpider(scrapy.Spider):
    name = 'house'
    group_name_index = 0
    page_index = 0
    page_count = 25
    min_page_sleep_ms = 10 * 1000
    max_page_sleep_ms = 30 * 1000
    min_sleep_ms = 3 * 60 * 1000
    max_sleep_ms = 5 * 60 * 1000
    crawl_page_count = 20
    failed_check_page_count = 0
    max_failed_check_page_count = 5
    # 北京租房，北京租房（真的没有中介）小组，北京个人租房 （真房源|无中介），北京租房豆瓣，北京无中介租房，北京租房（非中介）
    # group_name_list = ['beijingzufang', '625354', 'opking', '26926', 'zhufang', '279962']
    group_name_list = ['beijingzufang']
    topic_url_prefix = 'https://www.douban.com/group/topic/'
    topic_url_suffix = '?_dtcc=1'
    page_path_format = '/group/{group_name}/discussion?start={start}&type=new'
    filter_text_list = []

    def __init__(self, base_url='https://www.douban.com/', page_limit_count=-1, day_limit_count=14, crawl_interval=-1, mirai_sender='', mirai_recipient='', mirai_api_key='', *args, **kwargs):
        super(HouseSpider, self).__init__(*args, **kwargs)
        self.base_url = base_url
        self.start_urls = []
        if base_url:
            self.start_urls.append(self.get_page_url())
        self.page_limit_count = int(page_limit_count)
        self.day_limit_count = int(day_limit_count)
        self.crawl_interval = int(crawl_interval)
        self.mirai_recipient = mirai_recipient
        self.mirai_client = MiraiClient(mirai_sender, api_key=mirai_api_key)

    def filter(self, text):
        filtered = False
        for filter_text in self.filter_text_list:
            if filter_text in text:
                filtered = True
                break
        return filtered

    def get_page_url(self):
        return urljoin(self.base_url, self.page_path_format.format(
            group_name=self.group_name_list[self.group_name_index], start=self.page_count * self.page_index))

    def random_page_sleep(self):
        sleep_ms = random.randint(self.min_page_sleep_ms, self.max_page_sleep_ms)
        self.logger.info(f'random_page_sleep {sleep_ms} ms')
        time.sleep(sleep_ms / 1000.0)

    def random_sleep(self):
        sleep_ms = random.randint(self.min_sleep_ms, self.max_sleep_ms)
        self.logger.info(f'random_sleep {sleep_ms} ms')
        time.sleep(sleep_ms / 1000.0)

    def parse(self, response):
        self.logger.info(
            f'response page_url: {self.get_page_url()}, page_limit_count: {self.page_index + 1}/{self.page_limit_count}, day_limit_count: {self.day_limit_count}')
        tr_list = response.xpath('//*[@class="olt"]/tr')[1:]
        latest_timestamp = 0
        latest_time_str = 0
        for tr_selector in tr_list:
            title = tr_selector.xpath('td')[0].xpath('a').attrib['title']
            url = tr_selector.xpath('td')[0].xpath('a').attrib['href']
            time_str = tr_selector.xpath('td')[3].css('::text').get()
            time_format = '%Y-%m-%d'
            if len(time_str) != len('2020-01-01'):
                time_str = str(datetime.now().year) + '-' + time_str
                time_format = '%Y-%m-%d %H:%M'
            timestamp = int(datetime.strptime(time_str, time_format).timestamp())
            if not url.endswith(self.topic_url_suffix):
                url += self.topic_url_suffix
            id = url
            if url.startswith(self.topic_url_prefix) and url.endswith(self.topic_url_suffix):
                id = url[len(self.topic_url_prefix):-len(self.topic_url_suffix)].strip('/')
            else:
                self.logger.warning(f'invalid url {url}')
                continue
            if self.filter(tr_selector.get()):
                self.logger.warning(f'ignore title {title}')
                continue
            self.logger.info(f'discussion info {title} {url} {id} {timestamp} {time_str}')

            item = HouseItem()
            item['id'] = id
            item['title'] = title
            item['url'] = url
            item['group_name'] = self.group_name_list[self.group_name_index]
            item['timestamp'] = timestamp
            if latest_timestamp < timestamp:
                latest_timestamp = timestamp
                latest_time_str = time_str
            yield item
        time_delta = datetime.now() - datetime.fromtimestamp(latest_timestamp)
        if time_delta.days > self.day_limit_count:
            self.failed_check_page_count += 1
        else:
            self.failed_check_page_count = 0
        self.logger.info(
            f'time_delta days: {time_delta.days} latest_time_str:{latest_time_str} latest_timestamp:{latest_timestamp} failed_check_page_count: {self.failed_check_page_count}')
        run = True
        if (self.page_limit_count <= 0 or self.page_index + 1 < self.page_limit_count) and self.failed_check_page_count <= self.max_failed_check_page_count:
            self.page_index += 1
            if self.crawl_page_count > 0 and self.page_index % self.crawl_page_count == 0:
                self.random_sleep()
            else:
                self.random_page_sleep()
        elif self.group_name_index + 1 < len(self.group_name_list):
            self.group_name_index += 1
            self.page_index = 0
        elif self.crawl_interval > 0:
            self.mirai_client.send_text_msg(
                self.mirai_recipient, f'all group done. run after {timedelta(seconds=self.crawl_interval)}')
            time.sleep(self.crawl_interval)
            self.page_index = 0
            self.group_name_index = 0
            self.failed_check_page_count = 0
        else:
            run = False
        if run:
            self.logger.info(
                f'request page_url: {self.get_page_url()}, page_limit_count: {self.page_index + 1}/{self.page_limit_count}, day_limit_count: {self.day_limit_count}')
            self.mirai_client.send_text_msg(
                self.mirai_recipient, f'request page_url: {self.get_page_url()}, page_limit_count: {self.page_index + 1}/{self.page_limit_count}, day_limit_count: {self.day_limit_count}')
            yield scrapy.Request(self.get_page_url(), self.parse, dont_filter=True)
