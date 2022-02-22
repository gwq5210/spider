import pprint
from scrapy.mail import MailSender
from scrapy import signals
from datetime import datetime
from autostatsmailer import AutoStatsMailer as BaseAutoStatsMailer


class AutoStatsMailer(BaseAutoStatsMailer):
    def __init__(self, settings):
        super().__init__(settings)
        self.auto_mail_keys = settings.getlist('AUTO_MAIL_KEYS')

    def need_send_mail(self, item, spider):
        for key in self.auto_mail_keys:
            if key in item['title']:
                self.spider.logger.info(f'need_send_mail: key({key}), body({item["title"]})')
                return True
        return False

    def get_mail_body(self, item, spider):
        return f'{item["title"]} {item["url"]} {datetime.fromtimestamp(item["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")}'

    def get_subject(self, item, spider):
        return 'spider[%s] %s' % (spider.name, item['title'])
