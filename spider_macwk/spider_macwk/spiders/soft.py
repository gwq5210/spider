import scrapy
import js2py
import json
from spider_macwk.items import SpiderMacwkItem
from urllib.parse import urljoin

class SoftSpider(scrapy.Spider):
    name = 'soft'
    soft_name = "软件"
    path_format = '/soft/all/p{page_index}'
    soft_version_url_format = 'https://api.macwk.com/api/items/soft_version?filter[softid][eq]={softid}'
    key_name_list = ["id", "language", "title", "title_des", "description", "modified_on", "slug", "website"]

    def __init__(self, settings=None, *args, **kwargs):
        super(SoftSpider, self).__init__(*args, **kwargs)
        self.base_url = settings.get('BASE_URL', 'https://macwk.com/')
        self.start_urls = []
        if self.base_url:
            self.start_urls = [self.base_url]
        self.page_limit_count = settings.getint('PAGE_LIMIT_COUNT', -1)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(settings=crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider

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

    def parse_soft_list(self, response):
        js_str = response.xpath('/html/body/script[1]/text()').get()
        js_data=js2py.eval_js(js_str)
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