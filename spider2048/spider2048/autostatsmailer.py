import pprint
from scrapy.mail import MailSender
from scrapy import signals
from datetime import datetime
from autostatsmailer import AutoStatsMailer as BaseAutoStatsMailer


class AutoStatsMailer(BaseAutoStatsMailer):
    def __init__(self, settings):
        super().__init__(settings)
        self.image_count = 0
        self.image_count_interval = settings.getint('IMAGE_COUNT_INTERVAL', 3000)

    def need_send_mail(self, item, spider):
        self.image_count += len(item["file_urls"])
        if self.image_count >= self.image_count_interval:
            self.image_cousnt = 0
            return True
        return False
