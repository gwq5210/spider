import pprint
from scrapy.mail import MailSender
from scrapy import signals
from datetime import datetime


class AutoStatsMailer:
    def __init__(self, settings):
        self.spider = None
        self.item_count = 0
        self.auto_stats_interval = settings.getint('AUTO_STATS_INTERVAL', 3600)
        self.mail_sender = MailSender.from_settings(settings)
        self.mail_stats = settings.getbool('AUTO_MAIL_STATS', False)
        self.item_count_interval = settings.getint('ITEM_COUNT_INTERVAL', 1000)
        self.recipients = settings.getlist('STATSMAILER_RCPTS')
        self.last_stats_time = int(datetime.now().timestamp())

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

    def spider_closed(self, spider):
        pass

    def need_send_mail(self, item, spider):
        return False

    def item_scraped(self, item, spider):
        self.item_count += 1
        now_time = int(datetime.now().timestamp())
        if self.need_send_mail(item, spider) or (self.item_count % self.item_count_interval == 0) or (now_time - self.last_stats_time >= self.auto_stats_interval):
            stats_str = 'processed item count: %d, stats info: %s' % (self.item_count, pprint.pformat(spider.crawler.stats.get_stats()))
            subject = 'spider[%s] auto stats info' % (spider.name)
            self.spider.logger.info(stats_str)
            self.last_stats_time = now_time
            if self.mail_stats:
                self.mail_sender.send(to=self.recipients, subject=subject, body=stats_str)
        return item
