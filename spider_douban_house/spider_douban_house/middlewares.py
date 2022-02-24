# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
# from scrapy.downloadermiddlewares.retry import get_retry_request
from http import HTTPStatus
from scrapy.utils.response import response_status_message
from logging import getLogger, Logger
from typing import Optional, Union
import time
from twisted.internet import defer
from twisted.internet.error import (
    ConnectError,
    ConnectionDone,
    ConnectionLost,
    ConnectionRefusedError,
    DNSLookupError,
    TCPTimedOutError,
    TimeoutError,
)
from twisted.web.client import ResponseFailed

from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.exceptions import NotConfigured
from scrapy.http.request import Request
from scrapy.spiders import Spider
from scrapy.utils.python import global_object_name
from scrapy.utils.response import response_status_message
import logging
import random


# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

logger = logging.getLogger(__name__)


def load_proxy_file(proxy_file):
    proxy_list = []
    if proxy_file:
        with open(proxy_file) as f:
            proxy_list = f.read().split('\n')
    logger.info(f'proxy_list_len {len(proxy_list)} {proxy_list}')
    return proxy_list


def get_retry_request(
    request: Request,
    *,
    spider: Spider,
    reason: Union[str, Exception] = 'unspecified',
    priority_adjust: Optional[int] = None,
    stats_base_key: str = 'retry',
    proxy_list: list = [],
):
    """
    Returns a new :class:`~scrapy.Request` object to retry the specified
    request, or ``None`` if retries of the specified request have been
    exhausted.

    For example, in a :class:`~scrapy.Spider` callback, you could use it as
    follows::

        def parse(self, response):
            if not response.text:
                new_request_or_none = get_retry_request(
                    response.request,
                    spider=self,
                    reason='empty',
                )
                return new_request_or_none

    *spider* is the :class:`~scrapy.Spider` instance which is asking for the
    retry request. It is used to access the :ref:`settings <topics-settings>`
    and :ref:`stats <topics-stats>`, and to provide extra logging context (see
    :func:`logging.debug`).

    *reason* is a string or an :class:`Exception` object that indicates the
    reason why the request needs to be retried. It is used to name retry stats.

    *max_retry_times* is a number that determines the maximum number of times
    that *request* can be retried. If not specified or ``None``, the number is
    read from the :reqmeta:`max_retry_times` meta key of the request. If the
    :reqmeta:`max_retry_times` meta key is not defined or ``None``, the number
    is read from the :setting:`RETRY_TIMES` setting.

    *priority_adjust* is a number that determines how the priority of the new
    request changes in relation to *request*. If not specified, the number is
    read from the :setting:`RETRY_PRIORITY_ADJUST` setting.

    *logger* is the logging.Logger object to be used when logging messages

    *stats_base_key* is a string to be used as the base key for the
    retry-related job stats
    """
    settings = spider.crawler.settings
    stats = spider.crawler.stats
    retry_times = request.meta.get('retry_times', 0) + 1
    if True:
        new_proxy = ''
        if len(proxy_list) > 0:
            new_proxy = random.choice(proxy_list)
        spider.logger.info(
            "Retrying %(request)s (failed %(retry_times)d times): %(reason)s, proxy: %(proxy)s",
            {'request': request, 'retry_times': retry_times, 'reason': reason,
                'proxy': new_proxy},
            extra={'spider': spider}
        )
        sleep_s = 10
        time.sleep(sleep_s)
        new_request: Request = request.copy()
        new_request.meta['retry_times'] = retry_times
        if 'proxy' in new_request.meta:
            del new_request.meta['proxy']
        # if new_proxy:
            # new_request.meta['proxy'] = new_proxy
        new_request.dont_filter = True
        if priority_adjust is None:
            priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
        new_request.priority = request.priority + priority_adjust

        if callable(reason):
            reason = reason()
        if isinstance(reason, Exception):
            reason = global_object_name(reason.__class__)

        stats.inc_value(f'{stats_base_key}/count')
        stats.inc_value(f'{stats_base_key}/reason_count/{reason}')
        return new_request


class SpiderDoubanHouseSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class DoubanHouseRetryMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self, settings):
        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        self.proxy_list = load_proxy_file('proxy.txt')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        spider.logger.debug(f'process_response {response}')
        if response.status != HTTPStatus.OK:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        spider.logger.error(f'process_exception {request} {exception}')
        return self._retry(request, exception, spider)

    def _retry(self, request, reason, spider):
        return get_retry_request(
            request,
            reason=reason,
            spider=spider,
            proxy_list=self.proxy_list,
        )

    def spider_opened(self, spider):
        spider.logger.info('DoubanHouseRetryMiddleware Spider opened: %s' % spider.name)
