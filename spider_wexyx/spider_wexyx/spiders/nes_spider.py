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
            self.start_urls = [urljoin(self.base_url, nes_list_path_format.format(page_index=self.page_index))]
        self.page_limit_count = int(page_limit_count)

    def parse(self, response):
        link_list = response.xpath('//div[contains(@class, "app-header-nav")]//a[contains(@class, "nav-link")]')
        for link in link_list:
            if self.soft_name in link.get():
                yield response.follow(link, self.parse_soft_page, dont_filter = True)

    def parse_page_count(self, response):
        page_list = response.xpath('//li[contains(@class, "number")]/text()')
        page_count = 0
        if len(page_list) > 0:
            page_count = int(page_list[len(page_list) - 1].get())
        return page_count - 1

    def parse_soft_page(self, response):
        page_count = self.parse_page_count(response)
        self.logger.info(f"page_count: {page_count}, page_limit_count: {self.page_limit_count}")
        if self.page_limit_count >= 0:
            page_count = min(page_count, self.page_limit_count)
        page_index = 0
        while page_index < page_count:
            yield response.follow(self.path_format.format(page_index=page_index+1), self.parse_soft_list, dont_filter = True)
            page_index += 1

    def parse_nes_list(self, response):
        result = json.loads(response.text)
        soft_list = js_data["state"]["storage"]["soft"]["list"]
        link_list = response.xpath('//*[@id="listAppContainer"]/div/div/a')
        if len(soft_list) != len(link_list):
            self.logger.error("response %s, size mismatch, soft_list_size: %d, link_list_size: %d" % (response.url, len(soft_list), len(link_list)))
        index = 0
        while index < len(soft_list):
            soft_info = soft_list[index].to_dict()
            soft_path = link_list[index].attrib["href"]
            self.logger.info('found softid: {}, title: {}, title_des: {}, soft_path: {}'.format(soft_info["id"], soft_info["title"], soft_info["title_des"], soft_path))
            yield response.follow(self.soft_version_url_format.format(softid=soft_info["id"]), self.parse_soft_version, cb_kwargs={"soft_info": soft_info, "id": soft_info["id"], "soft_path": soft_path})
            index += 1

    def parse_soft_version(self, response, soft_info, id, soft_path):
        result = json.loads(response.text)
        item = SpiderMacwkItem()
        item["soft_version_list"] = result["data"]
        for key in self.key_name_list:
            item[key] = soft_info[key]
        item["id"] = str(id)
        item["softid"] = str(id)
        item["soft_path"] = soft_path
        item["soft_url"] = urljoin(self.base_url, soft_path)
        return item