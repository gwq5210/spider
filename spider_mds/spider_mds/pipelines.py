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
from io import BytesIO, StringIO
from scrapy.utils.misc import md5sum
from contextlib import suppress
import re
import m3u8


class M3u8FilesPipeline(FilesPipeline):
    invalid_char_regex = re.compile(r"[\/\\\:\*\?\"\<\>\|]")  # '/ \ : * ? " < > |'
    uri_regex = re.compile(r"URI=\"(.*)ts.key\"")

    def normalize_path(self, path):
        return self.invalid_char_regex.sub(" ", path).strip().rstrip(' .')

    def file_path(self, request, response=None, info=None, *, item=None):
        path = ''
        if item:
            path = self.normalize_path(item["category"]) + os.path.sep
            path += self.normalize_path(item["name"]) + ".m3u8"
        else:
            path = os.path.basename(os.path.dirname(urlparse(request.url).path)) + ".m3u8"
        return path

    def parse_duration(self, info, item, content):
        playlist = m3u8.loads(content)
        duration = 0
        for segment in playlist.segments:
            duration += segment.duration
        item['duration'] = int(duration)

    def file_downloaded(self, response, request, info, *, item=None):
        path = self.file_path(request, response=response, info=info, item=item)
        content = response.text
        uri_result = self.uri_regex.search(content)
        if uri_result:
            base_uri = uri_result.group(1)
            content = content.replace('index', f'{base_uri}index')
        else:
            info.spider.logger.warning(f'url {response.url} parse uri failed')
        self.parse_duration(info, item, content)
        buf = BytesIO(content.encode())
        checksum = md5sum(buf)
        buf.seek(0)
        self.store.persist_file(path, buf, info)
        return checksum

    def item_completed(self, results, item, info):
        file_urls = []
        for url in item['file_urls']:
            file_urls.append(url.split('?')[0])
        item['file_urls'] = file_urls
        with suppress(KeyError):
            ItemAdapter(item)[self.files_result_field] = [x for ok, x in results if ok]
        for result in item['files']:
            result['url'] = result['url'].split('?')[0]
        return item