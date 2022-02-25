import pprint
import requests
from scrapy.mail import MailSender
from scrapy import signals
from datetime import datetime
from urllib.parse import urlparse, urljoin


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
        self.mirai_http_url = settings.get('MIRAI_HTTP_URL', 'http://localhost:8080')
        self.mirai_verify_url = urljoin(self.mirai_http_url, '/verify')
        self.mirai_bind_url = urljoin(self.mirai_http_url, '/bind')
        self.mirai_release_url = urljoin(self.mirai_http_url, '/release')
        self.mirai_send_msg_url = urljoin(self.mirai_http_url, '/sendFriendMessage')
        self.mirai_http_key = settings.get('MIRAI_HTTP_KEY')
        self.mirai_send_qq = settings.getint('MIRAI_SEND_QQ')
        self.mirai_recv_qq = settings.getint('MIRAI_RECV_QQ')
        self.session = ''

    @classmethod
    def from_crawler(cls, crawler):
        # instantiate the extension object
        ext = cls(crawler.settings)

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)

        return ext

    def mirai_bind(self):
        res_json = requests.post(self.mirai_verify_url, json={
            'verifyKey': self.mirai_http_key
        }).json()
        self.spider.logger.info(f'verify {res_json}')
        self.session = res_json['session']
        res_json = requests.post(self.mirai_bind_url, json={
            'sessionKey': self.session,
            'qq': self.mirai_send_qq,
        }).json()
        self.spider.logger.info(f'bind_qq {res_json}')

    def mirai_release(self):
        res_json = requests.post(self.mirai_bind_url, json={
            'sessionKey': self.session,
            'qq': self.mirai_send_qq,
        }).json()
        self.spider.logger.info(f'release_qq {res_json}')

    def send_qq_msg(self, msg):
        res_json = requests.post(self.mirai_send_msg_url, json={
            "sessionKey": self.session,
            "target": self.mirai_recv_qq,
            "messageChain": [
                {"type": "Plain", "text": msg},
            ]
        }).json()
        self.spider.logger.info(f'send_qq_msg {res_json}')

    def spider_opened(self, spider):
        self.spider = spider
        self.mirai_bind()

    def spider_closed(self, spider):
        self.spider.logger.info(f'send_qq_msg spider closed')
        self.send_qq_msg('spider closed')
        self.mirai_release()

    def need_send_mail(self, item, spider):
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
        self.send_qq_msg(mail_body)

    def item_scraped(self, item, spider):
        self.item_count += 1
        if self.need_send_mail(item, spider):
            self.send_msg(item, spider)

        now_time = int(datetime.now().timestamp())
        if self.auto_mail_stats and ((self.item_count % self.item_count_interval == 0) or (now_time - self.last_stats_time >= self.auto_stats_interval)):
            self.send_msg(item, spider, now_time)
        return item
