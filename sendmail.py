import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.mail import MailSender

logger = logging.getLogger(__name__)


class SendMail(object):

    def __init__(self, mail_sender, mail_enabled, mail_to, crawler):
        self.mail_sender = mail_sender
        self.mail_enabled = mail_enabled
        self.mail_to = mail_to
        crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(MailSender.from_settings(crawler.settings), crawler.settings.getbool('MAIL_ENABLED'), crawler.settings.get('MAIL_TO'), crawler)

    def spider_idle(self, spider):
        logger.info('idle spider %s' % spider.name)

    def spider_closed(self, spider):
        subject = 'spider[%s] closed' % spider.name
        body = subject
        logger.info(body)
        # https://github.com/scrapy/scrapy/issues/3478
        if self.mail_enabled:
            return self.mail_sender.send(to=self.mail_to, subject=subject, body=body)
