import scrapy
import json
import sys
import os
from spider_wexyx.items import SpiderNesItem
from urllib.parse import urljoin

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))

class NesSpider(scrapy.Spider):
    name = 'nes_spider'
    page_index = 1
    nes_list_path_format = '/api/file/list?page={page_index}&pageSize=20'

    def __init__(self, base_url='https://wexyx.com/', page_limit_count=0, *args, **kwargs):
        super(NesSpider, self).__init__(*args, **kwargs)
        self.base_url = base_url
        if base_url:
            self.start_urls = [self.get_nes_list_url()]
        self.page_limit_count = int(page_limit_count)

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
        if has_more and (self.page_limit_count == 0 or self.page_index < self.page_limit_count):
            self.page_index += 1
            yield response.follow(self.get_nes_list_url(), self.parse)

    def parse_nes_info(self, item_info):
        item = SpiderNesItem()
        item["id"] = str(item_info["id"])
        return item