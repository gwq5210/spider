import pprint
import os, sys
from scrapy.mail import MailSender
from scrapy import signals
from datetime import datetime
from autostatsmailer import AutoStatsMailer as BaseAutoStatsMailer
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch
from http import HTTPStatus
from datetime import datetime

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))

from eswriter import ESClient

class AutoStatsMailer(BaseAutoStatsMailer):
    def __init__(self, settings):
        super().__init__(settings)
        self.auto_notify_keys = settings.getlist('AUTO_NOTIFY_KEYS')
        self.auto_notify_filter_keys = settings.getlist('AUTO_NOTIFY_FILTER_KEYS')
        self.es_client = ESClient.from_settings(settings)

    def spider_opened(self, spider):
        super().spider_opened(spider)

    def spider_closed(self, spider):
        super().spider_closed(spider)

    def set_msg_sended(self, res, item):
        if 'found' in res and res['found'] == True and 'msg_sended' in res["_source"] and res["_source"]['msg_sended'] == True:
            return False
        item['msg_sended'] = True
        return True

    def need_notify(self, item, spider):
        self.spider.logger.debug(f'need_notify ({self.auto_notify_keys}), ({self.auto_notify_filter_keys}) ({type(self.auto_notify_keys)}), ({type(self.auto_notify_filter_keys)})')
        if not self.es_client or "id" not in item.keys():
            return True
        res = self.es_client.get(id=item["id"], ignore=[HTTPStatus.NOT_FOUND])
        need_send_msg = True
        if not self.set_msg_sended(res, item):
            need_send_msg = False
        res = self.es_client.index(id=item["id"], body=ItemAdapter(item).asdict())
        for key in self.auto_notify_filter_keys:
            if key in item['title']:
                self.spider.logger.debug(f'need_filter: key({key}), body({item["title"]}), url({item["url"]})')
                return False
        for key in self.auto_notify_keys:
            if key in item['title']:
                msg = f'key({key}), body({item["title"]}), url({item["url"]})'
                if need_send_msg:
                    self.spider.logger.info(f'need_notify: {msg}')
                    return True
                else:
                    self.spider.logger.info(f'already_send_msg: {msg}')
                    return False
        return False

    def get_mail_body(self, item, spider):
        return f'{item["title"]} {item["url"]} {datetime.fromtimestamp(item["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")}'

    def get_subject(self, item, spider):
        return 'spider[%s] %s' % (spider.name, item['title'])
