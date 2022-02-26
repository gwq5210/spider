import os, sys
import pprint
import requests
from scrapy.mail import MailSender
from scrapy import signals
from datetime import datetime
from urllib.parse import urlparse, urljoin

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))

from mirai_client import MiraiClient

class AutoStatsMailer:
    def __init__(self, settings):
        self.spider = None
        self.item_count = 0
        self.auto_stats_interval = settings.getint('AUTO_STATS_INTERVAL', 3600)
        self.mail_sender = MailSender.from_settings(settings)
        self.auto_mail_stats = settings.getbool('AUTO_MAIL_STATS', False)
        self.item_count_interval = settings.getint('ITEM_COUNT_INTERVAL', 1000)
        self.recipients = settings.getlist('STATSMAILER_RCPTS')
        self.last_stats_time = int(datetime.now().timestamp())
        self.mirai_recipients = settings.getlist('MIRAI_RECIPIENTS')
        self.mirai_client = MiraiClient.from_settings(settings)

    @classmethod
    def from_crawler(cls, crawler):
        # instantiate the extension object
        ext = cls(crawler.settings)

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

        return ext

    def spider_opened(self, spider):
        self.spider = spider
        self.mirai_client.send_text_msg(self.mirai_recipients, f'spider {self.spider.name} opened')

    def spider_closed(self, spider):
        self.mirai_client.send_text_msg(self.mirai_recipients, f'spider {self.spider.name} closed')

    def need_notify(self, item, spider):
        return False

    def get_mail_body(self, item, spider):
        mail_body = 'processed item count: %d, stats info: %s' % (
            self.item_count, pprint.pformat(spider.crawler.stats.get_stats()))
        return mail_body

    def get_subject(self, item, spider):
        return 'spider[%s] auto stats info' % (spider.name)

    def send_msg(self, item, spider, now_time=None):
        mail_body = self.get_mail_body(item, spider)
        subject = self.get_subject(item, spider)
        self.spider.logger.info(f'autostatsmailer: subject({subject}), body({mail_body})')
        if now_time:
            self.last_stats_time = now_time
        # self.mail_sender.send(to=self.recipients, subject=subject, body=mail_body)
        self.mirai_client.send_text_msg(self.mirai_recipients, mail_body)

    def item_scraped(self, item, spider):
        self.item_count += 1
        if self.need_notify(item, spider):
            self.send_msg(item, spider)

        now_time = int(datetime.now().timestamp())
        if self.auto_mail_stats and ((self.item_count % self.item_count_interval == 0) or (now_time - self.last_stats_time >= self.auto_stats_interval)):
            self.send_msg(item, spider, now_time)
        return item
