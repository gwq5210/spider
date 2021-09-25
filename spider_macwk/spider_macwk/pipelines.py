# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import logging
import json
from scrapy.pipelines.files import FilesPipeline
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch
from scrapy.exceptions import DropItem
from http import HTTPStatus
from datetime import datetime
