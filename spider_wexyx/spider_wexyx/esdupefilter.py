from scrapy.http.request import Request
from scrapy_spider_utils.esdupefilter import ESDupeFilter as BaseESDupeFilter

class ESDupeFilter(BaseESDupeFilter):
    """Request ES duplicates filter"""

    def is_request_dup(self, request: Request, res) -> bool:
        return res and res["found"] and "failed_count" in res["_source"] and res["_source"]["failed_count"] == 0 and "first_crawl_time" in res["_source"]
