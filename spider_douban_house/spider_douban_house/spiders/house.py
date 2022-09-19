import scrapy
import sys
import os
import random
import time
from spider_douban_house.items import HouseItem
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta
from scrapy.exceptions import NotConfigured
from http import HTTPStatus
from spider_utils.mirai_client import MiraiClient
from spider_utils.eswriter import ESClient
from spider_utils.login.douban_client import DoubanClient


class HouseSpider(scrapy.Spider):
    name = 'house'
    group_name_index = 0
    page_index = 0
    page_count = 25
    total_page_count = 0
    notify_page_count = 1000
    min_page_sleep_ms = 10 * 1000
    max_page_sleep_ms = 30 * 1000
    min_sleep_ms = 3 * 60 * 1000
    max_sleep_ms = 5 * 60 * 1000
    crawl_page_count = 20
    failed_check_page_count = 0
    msg_sended_page_count = 0
    max_failed_check_page_count = 5
    # 北京租房，北京租房（真的没有中介）小组，北京个人租房 （真房源|无中介），北京租房豆瓣，北京无中介租房，北京租房（非中介）
    group_name_list = [
        'beijingzufang', '625354', 'opking', '26926', 'zhufang', '279962'
    ]
    # group_name_list = ['beijingzufang']
    topic_url_prefix = 'https://www.douban.com/group/topic/'
    topic_url_suffix = '?_dtcc=1'
    page_path_format = '/group/{group_name}/discussion?start={start}&type=new'
    filter_text_list = []

    def __init__(self, settings=None, *args, **kwargs):
        super(HouseSpider, self).__init__(*args, **kwargs)
        self.base_url = settings.get('BASE_URL', 'https://www.douban.com/')
        self.start_urls = []
        if self.base_url:
            self.start_urls.append(self.get_page_url())
        self.page_limit_count = settings.getint('PAGE_LIMIT_COUNT', -1)
        self.day_limit_count = settings.getint('DAY_LIMIT_COUNT', 7)
        self.crawl_interval = settings.getint('CRAWL_INTERVAL', 600)
        self.douban_username = settings.get('DOUBAN_USERNAME', '18682085392')
        self.mirai_recipients = settings.get('AUTO_NOTIFY_RECIPIENTS')
        self.mirai_client = MiraiClient.from_settings(settings)
        self.es_client = ESClient.from_settings(settings)
        self.douban_client = DoubanClient()
        self.douban_session = None
        self.logger.info(f'config mirai_recipients: {self.mirai_recipients}')

    def douban_login(self):
        infos_return, session = self.douban_client.login(self.douban_username, '', 'scanqr')
        cookie_string = "; ".join([str(k)+"="+str(v) for k,v in session.cookies.items()])
        self.logger.info(f'username: {infos_return["username"]}, cookie_string: {cookie_string}')
        self.douban_session = session

    def start_requests(self):
        self.douban_login()
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse, dont_filter=True, cookies=self.douban_session.cookies.get_dict())

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(settings=crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def filter(self, text):
        filtered = False
        for filter_text in self.filter_text_list:
            if filter_text in text:
                filtered = True
                break
        return filtered

    def reset_spider_params(self):
        self.group_name_index = 0

    def reset_group_params(self):
        self.page_index = 0
        self.failed_check_page_count = 0
        self.msg_sended_page_count = 0

    def get_page_url(self):
        return urljoin(
            self.base_url,
            self.page_path_format.format(
                group_name=self.group_name_list[self.group_name_index],
                start=self.page_count * self.page_index))

    def random_page_sleep_s(self):
        sleep_ms = random.randint(self.min_page_sleep_ms,
                                  self.max_page_sleep_ms)
        return sleep_ms / 1000.0

    def random_sleep_s(self):
        sleep_ms = random.randint(self.min_sleep_ms, self.max_sleep_ms)
        return sleep_ms / 1000.0

    def sleep(self, sleep_s, msg=''):
        self.logger.info(f'sleep {timedelta(seconds=sleep_s)}')
        if msg:
            self.mirai_client.send_text_msg(
                self.mirai_recipients,
                f'{msg}. run after {timedelta(seconds=sleep_s)}.')
        time.sleep(sleep_s)
        self.logger.info(f'sleep done')
        if msg:
            self.mirai_client.send_text_msg(
                self.mirai_recipients,
                f'sleep done. spider {self.name} running')

    def parse_item(self, tr_selector):
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
        if url.startswith(self.topic_url_prefix) and url.endswith(
                self.topic_url_suffix):
            id = url[len(self.topic_url_prefix
                         ):-len(self.topic_url_suffix)].strip('/')
        else:
            self.logger.error(f'invalid url {url}')
            return None
        if self.filter(tr_selector.get()):
            self.logger.error(f'ignore title {title}')
            return None
        self.logger.info(
            f'discussion info {title} {url} {id} {timestamp} {time_str}')

        item = HouseItem()
        item['id'] = id
        item['title'] = title
        item['url'] = url
        item['group_name'] = self.group_name_list[self.group_name_index]
        item['timestamp'] = timestamp
        return item

    def check_page_timestamp(self, latest_timestamp):
        time_delta = datetime.now() - datetime.fromtimestamp(latest_timestamp)
        if time_delta.days > self.day_limit_count:
            self.failed_check_page_count += 1
        else:
            self.failed_check_page_count = 0
        self.logger.info(
            f'time_delta days: {time_delta.days} latest_timestamp:{latest_timestamp} failed_check_page_count: {self.failed_check_page_count}'
        )

    def check_page_msg_sended(self, id_list):
        for id in id_list:
            if not self.check_msg_sended(id):
                self.msg_sended_page_count = 0
                return False
        self.msg_sended_page_count += 1
        self.logger.info(
            f'check_page_msg_sended msg_sended_page_count: {self.msg_sended_page_count}'
        )
        return True

    def check_msg_sended(self, id):
        res = self.es_client.get(id=id, ignore=[HTTPStatus.NOT_FOUND])
        return 'found' in res and res['found'] is True and 'msg_sended' in res[
            "_source"] and res["_source"]['msg_sended'] is True

    def do_next_request(self):
        run = True
        sleep_s = 0
        notify_msg = ''
        if self.crawl_page_count > 0 and self.total_page_count % self.crawl_page_count == 0:
            sleep_s = self.random_sleep_s()
        else:
            sleep_s = self.random_page_sleep_s()
        if (
                self.page_limit_count <= 0
                or self.page_index + 1 < self.page_limit_count
        ) and self.failed_check_page_count <= self.max_failed_check_page_count and self.msg_sended_page_count <= self.max_failed_check_page_count:
            self.page_index += 1
        elif self.group_name_index + 1 < len(self.group_name_list):
            self.group_name_index += 1
            self.reset_group_params()
        elif self.crawl_interval > 0:
            # notify_msg = 'all group done'
            sleep_s = self.crawl_interval
            self.reset_group_params()
            self.reset_spider_params()
        else:
            run = False
        self.logger.info(
            f'do_next_request run: {run}, group_name_index: {self.group_name_index}({self.group_name_list[self.group_name_index]}), page_index: {self.page_index}'
        )
        if run:
            self.sleep(sleep_s, notify_msg)
            self.logger.info(
                f'request page_url: {self.get_page_url()}, page_limit_count: {self.page_index + 1}/{self.page_limit_count}, day_limit_count: {self.day_limit_count}'
            )
            return scrapy.Request(self.get_page_url(),
                                  self.parse,
                                  dont_filter=True,
                                  cookies=self.douban_session.cookies.get_dict())

    def parse(self, response):
        self.total_page_count += 1
        if self.total_page_count % self.notify_page_count == 0:
            self.mirai_client.send_text_msg(
                self.mirai_recipients,
                f'spider {self.name} running. total page count: {self.total_page_count}'
            )
        self.logger.info(
            f'response page_url: {self.get_page_url()}, page_limit_count: {self.page_index + 1}/{self.page_limit_count}, day_limit_count: {self.day_limit_count}'
        )
        latest_timestamp = 0
        page_item_count = 0
        tr_list = response.xpath('//*[@class="olt"]/tr')[1:]
        id_list = []
        item_list = []
        for tr_selector in tr_list:
            item = self.parse_item(tr_selector)
            if not item:
                continue
            if latest_timestamp < item['timestamp']:
                latest_timestamp = item['timestamp']
            page_item_count += 1
            id_list.append(item['id'])
            item_list.append(item)
        self.check_page_timestamp(latest_timestamp)
        self.check_page_msg_sended(id_list)
        for item in item_list:
            yield item
        yield self.do_next_request()
