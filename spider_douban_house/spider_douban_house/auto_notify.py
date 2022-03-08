from eswriter import ESClient
import pprint
import os
import sys
from scrapy.mail import MailSender
from scrapy import signals
from datetime import datetime
from auto_notify import AutoNotify as BaseAutoNotify
from auto_notify import NotifyInfo, NotifyConfig
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch
from http import HTTPStatus
from datetime import datetime

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))


class AutoNotify(BaseAutoNotify):
    def __init__(self, settings):
        super().__init__(settings)
        self.notify_configs = NotifyConfig.from_configs(settings.get('NOTIFY_CONFIGS'))
        self.es_client = ESClient.from_settings(settings)

    def spider_opened(self, spider):
        super().spider_opened(spider)

    def spider_closed(self, spider):
        super().spider_closed(spider)

    def set_msg_sended(self, res, item):
        if 'found' in res and res['found'] == True and 'msg_sended' in res["_source"] and res["_source"]['msg_sended'] == True:
            return True
        item['msg_sended'] = True
        return False

    def is_msg_sended(self, item):
        if not self.es_client or "id" not in item.keys():
            return False
        res = self.es_client.get(id=item["id"], ignore=[HTTPStatus.NOT_FOUND])
        msg_sended = self.set_msg_sended(res, item)
        res = self.es_client.index(id=item["id"], body=ItemAdapter(item).asdict())
        return msg_sended

    def is_filtered(self, item, notify_config: NotifyConfig):
        for key in notify_config.filter_keys:
            if key in item['title']:
                self.spider.logger.debug(f'is_filtered: key({key}), body({item["title"]}), url({item["url"]})')
                return True
        return False

    def is_hit_keys(self, item, notify_config: NotifyConfig):
        for key in notify_config.keys:
            if key in item['title']:
                return True
        return False

    def get_notify_infos(self, item):
        notify_infos = []
        msg_sended = self.is_msg_sended(item)
        for notify_config in self.notify_configs:
            if self.is_filtered(item, notify_config):
                continue
            if self.is_hit_keys(item, notify_config):
                notify_info = NotifyInfo(self.get_subject(item), self.get_body(item), notify_config.recipients)
                tip = 'already_send_msg'
                if not msg_sended:
                    notify_infos.append(notify_info)
                    tip = 'need_notify'
                self.spider.logger.info(f'{tip}: {notify_info.body}')
        return notify_infos

    def get_body(self, item):
        return f'{item["title"]} {item["url"]} {datetime.fromtimestamp(item["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")}'

    def get_subject(self, item):
        return 'spider[%s] %s' % (self.spider.name, item['title'])
