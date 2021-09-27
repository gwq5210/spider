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
from scrapy.mail import MailSender

class ESWriterPipeline:
    def __init__(self, es_uri, es_index, es_index_mapping_file):
        self.es_uri = es_uri
        self.es_index = es_index
        self.es_index_mapping_file = es_index_mapping_file
        self.es_client = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            es_uri=crawler.settings.get('ES_URI', 'localhost:9200'),
            es_index=crawler.settings.get('ES_INDEX', ''),
            es_index_mapping_file=crawler.settings.get('ES_INDEX_MAPPING_FILE', 'mapping.json')
        )

    def open_spider(self, spider):
        if not self.es_index:
            return
        self.es_client = Elasticsearch([self.es_uri])
        self.create_index(spider)

    def close_spider(self, spider):
        pass

    def create_index(self, spider):
        if self.es_client.indices.exists(index=self.es_index):
            spider.logger.info('es index(%s) already exists' % (self.es_index))
            return
        if not self.es_index_mapping_file or not os.path.exists(self.es_index_mapping_file):
            spider.logger.error('es index mapping file does not exist' % (self.es_index_mapping_file))
            return
        json_str = ''
        with open(self.es_index_mapping_file) as f:
            json_str = f.read()
        if json_str:
            self.es_client.indices.create(index=self.es_index, body=json_str)
        else:
            spider.logger.error('read es index mapping file(%s) failed' % (self.es_index_mapping_file))

    def set_crawl_time(self, res, item):
        if "first_crawl_time" in item.fields:
            if res["found"] and "first_crawl_time" in res["_source"]:
                item["first_crawl_time"] = res["_source"]["first_crawl_time"]
            else:
                item["first_crawl_time"] = 0
        now_time = int(datetime.now().timestamp())
        if "crawl_time" in item.fields:
            item["crawl_time"] = now_time
        if "first_crawl_time" in item.fields and item["first_crawl_time"] == 0:
            item["first_crawl_time"] = now_time

    def process_item(self, item, spider):
        if not self.es_client or "id" not in item.keys():
            return item
        res = self.es_client.get(index=self.es_index, id=item["id"], ignore=[HTTPStatus.NOT_FOUND])
        spider.logger.debug(f'es get {res}')
        self.set_crawl_time(res, item)
        res = self.es_client.index(index=self.es_index, id=item["id"], body=ItemAdapter(item).asdict())
        spider.logger.debug(f'es index {res}')
        return item
