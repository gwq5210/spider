import logging
import os
import sys
from typing import Optional, Set, Type, TypeVar

from twisted.internet.defer import Deferred

from scrapy.http.request import Request
from scrapy.settings import BaseSettings
from scrapy.spiders import Spider
from scrapy.utils.job import job_dir
from scrapy.dupefilters import BaseDupeFilter
from scrapy.utils.request import referer_str, request_fingerprint
from elasticsearch import Elasticsearch
from esdupefilter import ESDupeFilter as BaseESDupeFilter
from http import HTTPStatus

class ESDupeFilter(BaseESDupeFilter):
    """Request ES duplicates filter"""

    def is_request_dup(self, request: Request, res) -> bool:
        return res and res["found"] and "failed_count" in res["_source"] and res["_source"]["failed_count"] == 0 and "first_crawl_time" in res["_source"]
