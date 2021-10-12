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

class SpiderWexyxFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        if response:
            return item["name"] + os.path.sep + os.path.basename(urlparse(response.url).path)
        else:
            return item["name"] + os.path.sep + os.path.basename(urlparse(request.url).path)

    def item_completed(self, results, item, info):
        results_info = []
        total_count = len(results)
        succeeded_count = 0
        failed_count = 0
        for result in results:
            succeeded, result_info = result
            if succeeded:
                succeeded_count += 1
                result_info["succeeded"] = succeeded
                result_info["message"] = "succeeded"
                results_info.append(result_info)
            else:
                failed_count += 1
                results_info.append({
                    "succeeded": succeeded,
                    "message": str(result_info)
                })
        item["results"] = results_info
        item["failed_count"] = failed_count
        item["succeeded_count"] = succeeded_count
        item["total_count"] = total_count
        if succeeded_count > 0:
            filename = info.spider.settings["FILES_STORE"] + os.path.sep + item["name"] + os.path.sep + "info.txt"
            with open(filename, "w") as f:
                f.write("id: %s\n" % (item["id"]))
                f.write("location: %s\n" % (item["location"]))
                f.write("img_url: %s\n" % (item["img_url"]))

        return item