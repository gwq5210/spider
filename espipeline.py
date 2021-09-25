# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import logging
import json
from urllib.parse import urlparse
from scrapy.pipelines.files import FilesPipeline
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch
from scrapy.exceptions import DropItem
from http import HTTPStatus
from datetime import datetime

class ElasticsearchPipeline:
    def __init__(self, es_uri, es_index):
        self.es_uri = es_uri
        self.es_index = es_index
        self.es_client = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            es_uri=crawler.settings.get('ES_URI', 'localhost:9200'),
            es_index=crawler.settings.get('ES_INDEX', '')
        )

    def open_spider(self, spider):
        if self.es_index:
            self.es_client = Elasticsearch([self.es_uri])

    def close_spider(self, spider):
        pass

    def set_crawl_time(self, res, item):
        if "first_crawl_time" in item:
            if res["found"]:
                item["first_crawl_time"] = res["_source"]["first_crawl_time"]
            else:
                item["first_crawl_time"] = 0
        if "crawl_time" in item:
            item["crawl_time"] = int(datetime.now().timestamp())
        if "first_crawl_time" in item and "crawl_time" in item and item["first_crawl_time"] == 0:
            item["first_crawl_time"] = item["crawl_time"]

    def process_item(self, item, spider):
        if not self.es_client or "id" not in item:
            return item
        res = self.es_client.get(index=self.es_index, id=item["id"], ignore=[HTTPStatus.NOT_FOUND])
        spider.logger.debug(f'es get {res}')
        self.set_crawl_time(res, item)
        res = self.es_client.index(index=self.es_index, id=item["id"], body=ItemAdapter(item).asdict())
        spider.logger.debug(f'es index {res}')
        return item
