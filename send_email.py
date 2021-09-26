import logging
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.mail import MailSender

logger = logging.getLogger(__name__)


class SendEmail(object):

    def __init__(self, sender, mail_enabled, crawler):
        self.sender = sender
        self.mail_enabled = mail_enabled
        crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)
        crawler.signals.connect(
            self.spider_closed, signal=signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings['MAIL_ENABLED']:
            raise NotConfigured

        return cls(MailSender.from_settings(crawler.settings), crawler.settings.getbool('MAIL_ENABLED'), crawler)

    def spider_idle(self, spider):
        logger.info('idle spider %s' % spider.name)

    def spider_closed(self, spider):
        subject = 'spider[%s] closed' % spider.name
        body = subject
        logger.info(body)
        # https://github.com/scrapy/scrapy/issues/3478
        if self.mail_enabled:
            return self.sender.send(to=self.sender.mailfrom, subject=subject, body=body)
