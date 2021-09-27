import scrapy
import sys
import os
import re
import random
import time
import json
import logging
import parse
from spider2048.items import Spider2048Item
from urllib.parse import urlparse
from datetime import datetime
from scrapy.exceptions import NotConfigured

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))


class ImageSpider(scrapy.Spider):
    name = "image_spider"
    thread_url_format = "{base_url}read.php?tid-{thread_id}.html"
    filter_text_list = ["站点公告", "置顶", "澳门"]
    invalid_char_regex = re.compile(
        r"[\/\\\:\*\?\"\<\>\|]")  # '/ \ : * ? " < > |'

    def __init__(self, base_url=None, page_limit_count=1, image_limit_count=-1, spider_category_name="", spider_top_title="", *args, **kwargs):
        super(ImageSpider, self).__init__(*args, **kwargs)
        self.start_urls = []
        if base_url:
            self.start_urls.append(base_url)
        self.page_limit_count = int(page_limit_count)
        self.image_limit_count = int(image_limit_count)
        self.spider_category_name = spider_category_name
        self.spider_top_title = spider_top_title

    def parse(self, response):
        self.logger.info("page_limit_count: {}, image_limit_count: {}, spider_category_name: {}, spider_top_title: {}".format(
            self.page_limit_count, self.image_limit_count, self.spider_category_name, self.spider_top_title))
        th_list = response.xpath("//*[@id='cate_1']/tr/th[1]")[1:]
        for th in th_list:
            category_name = th.css("a::text").get()
            if category_name not in self.spider_category_name:
                self.logger.warning("ignore category %s" % (category_name))
                continue
            a_list = th.css("a")[1:]
            for a in a_list:
                top_title = a.css("::text").get()
                if top_title in self.spider_top_title:
                    yield response.follow(a, self.parse_first_page, cb_kwargs={"top_title": top_title}, dont_filter=True)

    def parse_first_page(self, response, top_title):
        page_str = response.xpath("//*[@class='pagesone']/span/text()").get()
        parse_result = parse.parse(
            "Pages: {page_index}/{page_count:d}", page_str)
        page_limit_count = self.page_limit_count
        page_count = page_limit_count
        if parse_result and parse_result["page_count"]:
            page_count = parse_result["page_count"]
            if page_limit_count < 0:
                page_limit_count = page_count
            self.logger.info("%s total page count %d, page limit count %d" % (
                top_title, page_count, self.page_limit_count))
        else:
            page_limit_count = 0
            self.logger.warning(
                "%s parse total page count failed, page_str(%s)" % (top_title, page_str))
        url_pattern = response.url.replace(".html", "-page-%d.html")
        i = 1
        while i <= self.page_limit_count and i <= page_count:
            url = url_pattern % (i)
            yield scrapy.Request(url, self.parse_thread_list, cb_kwargs={"top_title": top_title}, dont_filter=True)
            i += 1

    def parse_thread_list(self, response, top_title):
        td_list = response.xpath("//*[@id='ajaxtable']/tbody[1]/tr/td[2]")
        valid_count = 0
        self.logger.debug("td list size %d" % (len(td_list)))
        for td in td_list:
            filtered = False
            for filter_text in self.filter_text_list:
                if filter_text in td.get():
                    filtered = True
                    continue
            if filtered:
                continue
            a_list = td.xpath("a")
            if len(a_list) == 0:
                continue
            a_tag = None
            for a in a_list:
                if "subject" in a.attrib["class"]:
                    a_tag = a
            if not a_tag:
                continue
            img_page_url = a_tag.attrib["href"]
            thread_title = a_tag.css("::text").get()
            thread_title = self.normalize_path(thread_title)
            thread_id = self.parse_thread_id(img_page_url)
            self.logger.info("found img page %s %s %s %s" % (top_title, thread_title, img_page_url, thread_id))
            if thread_id == "-1":
                self.logger.error("parse thread id failed, %s %s %s %s" % (top_title, thread_title, img_page_url, thread_id))
                continue
            valid_count += 1
            yield response.follow(img_page_url, self.parse_image_thread, cb_kwargs={"top_title": top_title, "thread_title": thread_title, "id": thread_id, "img_page_url": img_page_url})
        self.logger.info("parse (%s) finished, valid thread count %d" %
                         (response.url, valid_count))

    def parse_thread_id(self, thread_url):
        # tid-4200989-fpage-3.html
        # tid-4200989.html
        # jt/pc/21/2109/4241813.html
        urlparsed = urlparse(thread_url)
        parse_result = parse.parse("tid-{thread_id:d}-fpage-{}.html", urlparsed.query)
        if not parse_result:
            parse_result = parse.parse(
                "tid-{thread_id:d}.html", urlparsed.query)
        thread_id = "-1"
        if parse_result and parse_result["thread_id"]:
            thread_id = parse_result["thread_id"]
        else:
            thread_id = os.path.basename(thread_url).removesuffix(".html")
        return str(thread_id)

    def normalize_path(self, path):
        return self.invalid_char_regex.sub("", path).rstrip(' .')

    def parse_image_thread(self, response, top_title, thread_title, id, img_page_url):
        img_list = response.xpath("//*[@class='tpc_content']//img")
        img_count = len(img_list)
        if img_count == 0:
            self.logger.warning("parse %s (%s) img empty" %
                               (top_title, img_page_url))
        thread_id = id
        thread_time_result = response.xpath('//*[@id="td_tpc"]/div[2]/span[2]')
        thread_time = 0
        if len(thread_time_result) > 0:
            thread_time = int(datetime.strptime(
                thread_time_result[0].attrib["title"], '%Y-%m-%d %H:%M').timestamp())

        item = Spider2048Item()
        img_url_list = []
        invalid_url_list = []
        for img in img_list:
            if self.image_limit_count >= 0 and len(img_url_list) >= self.image_limit_count:
                break
            parse_result = urlparse(img.attrib["src"])
            if not parse_result.netloc:
                invalid_url_list.append(img.attrib["src"])
            else:
                img_url_list.append(img.attrib["src"])
        item["top_title"] = top_title
        item["thread_title"] = thread_title
        item["thread_id"] = thread_id
        item["id"] = thread_id
        item["file_urls"] = img_url_list
        item["thread_time"] = thread_time
        if thread_time == 0:
            self.logger.warning("parse %s (%s) thread time failed" %
                               (top_title, img_page_url))
        if not thread_title:
            self.logger.warning("parse %s (%s) title failed" %
                               (top_title, img_page_url))
        if len(invalid_url_list) > 0:
            self.logger.error("parse %s/%s(%s) invalid url count %d, %s" % (
                top_title, thread_title, img_page_url, len(invalid_url_list), invalid_url_list))
        self.logger.info("parse %s/%s(%s) finished, valid img count %d/%d" %
                         (top_title, thread_title, img_page_url, len(img_url_list), img_count))
        return item
