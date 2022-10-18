# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy_spider_utils.eswriter import ESWriterPipeline
from http import HTTPStatus


class HouseESWriterPipeline(ESWriterPipeline):
    def set_msg_sended(self, res, item, spider):
        if 'status' in res and res['status'] == HTTPStatus.NOT_FOUND:
            return
        if "msg_sended" in item.fields and res["found"] and "msg_sended" in res["_source"]:
            item["msg_sended"] = res["_source"]["msg_sended"]

    def before_write(self, res, item, spider):
        self.set_msg_sended(res, item, spider)