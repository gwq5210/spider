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

class ImageSpider(scrapy.Spider):
    name = "image_spider"
    spider_name_list = ["美图秀秀"]
    spider_title_list = ["唯美清純"]
    filter_text_list = ["站点公告", "置顶", "赌场"]
    invalid_char_regex = re.compile(r"[\/\\\:\*\?\"\<\>\|]")  # '/ \ : * ? " < > |'

    def __init__(self, base_url=None, page_limit_count=None, image_limit_count=None, *args, **kwargs):
        super(ImageSpider, self).__init__(*args, **kwargs)
        self.start_urls = []
        if base_url:
            self.start_urls.append(f"{base_url}")
        self.page_limit_count = 0
        self.image_limit_count = 0
        if page_limit_count:
            self.page_limit_count = int(page_limit_count)
        if image_limit_count:
            self.image_limit_count = int(image_limit_count)
        self.logger.info("page_limit_count: {}, image_limit_count: {}".format(self.page_limit_count, self.image_limit_count))
        
    def parse(self, response):
        th_list = response.xpath("//*[@id='cate_1']/tr/th[1]")[1:]
        for th in th_list:
            th_name = th.css("a::text").get()
            if th_name not in self.spider_name_list:
                self.logger.warning("ignore th %s" % (th_name))
                continue
            a_list = th.css("a")[1:]
            for a in a_list:
                title = a.css("::text").get()
                if title in self.spider_title_list:
                    yield response.follow(a, self.parse_first_page, cb_kwargs={"title": title})

    def parse_first_page(self, response, title):
        page_str = response.xpath("//*[@class='pagesone']/span/text()").get()
        parse_result = parse.parse("Pages: {page_index}/{page_count:d}", page_str)
        page_limit_count = self.page_limit_count
        page_count = page_limit_count
        if parse_result and parse_result["page_count"]:
            page_count = parse_result["page_count"]
            if page_limit_count < 0:
                page_limit_count = page_count
            self.logger.info("%s total page count %d, page limit count %d" % (title, page_count, self.page_limit_count))
        else:
            page_limit_count = 0
            self.logger.warning("%s parse total page count failed, page_str(%s)" % (title, page_str))
        url_pattern = response.url.replace(".html", "-page-%d.html")
        i = 1
        while i <= self.page_limit_count and i <= page_count:
            url = url_pattern % (i)
            yield scrapy.Request(url, self.parse_thread_list, cb_kwargs={"title": title})
            i += 1

    def parse_thread_list(self, response, title):
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
            img_title = a_tag.css("::text").get()
            img_title = self.invalid_char_regex.sub("_", img_title)
            self.logger.debug("found img page %s %s" % (img_title, img_page_url))
            valid_count += 1
            yield response.follow(a, self.parse_image_thread, cb_kwargs={"title": title})
        self.logger.info("parse (%s) finished, valid thread count %d" % (response.url, valid_count))

    def parse_image_thread(self, response, title):
        img_list = response.xpath("//*[@class='tpc_content']//img")
        img_count = len(img_list)
        if img_count == 0:
            return None
        img_title = response.xpath("//*[@id='subject_tpc']/text()").get()
        img_title = self.invalid_char_regex.sub("_", img_title)

        items = Spider2048Item()
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
        items["title"] = title
        items["image_title"] = img_title
        items["thread_url"] = response.url
        items["thread_id"] = response.url
        items["file_urls"] = img_url_list
        if not img_title:
            self.logger.waring("parse %s (%s) title failed" % (title, response.url))
        if len(invalid_url_list) > 0:
            self.logger.error("parse %s/%s(%s) invalid url count %d, %s" % (title, img_title, response.url, len(invalid_url_list), invalid_url_list))
        self.logger.info("parse %s/%s(%s) finished, valid img count %d/%d" % (title, img_title, response.url, len(img_url_list), img_count))
        return items
