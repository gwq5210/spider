import scrapy
import json
import sys
import os
import re
from spider_wexyx.items import SpiderNesItem
from urllib.parse import urljoin

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))

class NesSpider(scrapy.Spider):
    name = 'nes'
    page_index = 1
    nes_list_path_format = '/api/file/list?page={page_index}&pageSize=20'
    invalid_char_regex = re.compile(r"[\/\\\:\*\?\"\<\>\|]")  # '/ \ : * ? " < > |'

    def __init__(self, settings=None, *args, **kwargs):
        super(NesSpider, self).__init__(*args, **kwargs)
        self.base_url = settings.get('BASE_URL', 'https://wexyx.com/')
        self.start_urls = []
        if self.base_url:
            self.start_urls = [self.get_nes_list_url()]
        self.page_limit_count = settings.getint('PAGE_LIMIT_COUNT', -1)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(settings=crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def normalize_path(self, path):
        return self.invalid_char_regex.sub(" ", path).rstrip(' .')

    def get_nes_list_url(self):
        return urljoin(self.base_url, self.nes_list_path_format.format(page_index=self.page_index))

    def parse(self, response):
        self.logger.info("parse url(%s), page %d/%d" % (response.url, self.page_index, self.page_limit_count))
        result = json.loads(response.text)
        if result["code"]:
            pass
        has_more = result["content"]["hasMore"]
        items_info = result["content"]["items"]
        for item_info in items_info:
            yield self.parse_nes_info(item_info)
        if has_more and (self.page_limit_count <= 0 or self.page_index < self.page_limit_count):
            self.page_index += 1
            yield response.follow(self.get_nes_list_url(), self.parse)

    def parse_nes_info(self, item_info):
        item = SpiderNesItem()
        item["id"] = str(item_info["id"])
        item["name"] = self.normalize_path(item_info["name"])
        item["type"] = item_info["type"]
        item["location"] = item_info["location"]
        item["img_url"] = item_info["imgUrl"]
        item["category_id"] = item_info["categoryId"]
        item["is_deleted"] = item_info["isDeleted"]
        item["description"] = item_info["description"]
        item["create_time"] = item_info["gmtCreate"]
        item["modified_time"] = item_info["gmtModified"]
        item["file_urls"] = [item_info["location"], item_info["imgUrl"]]
        return item