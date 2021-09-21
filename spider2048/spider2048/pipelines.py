# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
from itemadapter import ItemAdapter
from urllib.parse import urlparse
from scrapy.pipelines.files import FilesPipeline
from spider2048.settings import FILES_STORE

class Spider2048FilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        if item and item["image_title"]:
            return item["title"] + os.path.sep + item["image_title"] + os.path.sep + os.path.basename(urlparse(request.url).path)
        else:
            os.path.basename(urlparse(request.url).path)

    def item_completed(self, results, item, info):
        url_filename = FILES_STORE + os.path.sep + item["title"] + os.path.sep + item["image_title"] + os.path.sep + "url.txt"
        with open(url_filename, "w") as f:
            f.write(item["thread_url"])
        return item