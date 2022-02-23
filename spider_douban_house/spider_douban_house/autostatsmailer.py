import pprint
import os
from scrapy.mail import MailSender
from scrapy import signals
from datetime import datetime
from autostatsmailer import AutoStatsMailer as BaseAutoStatsMailer
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch
from http import HTTPStatus
from datetime import datetime

class AutoStatsMailer(BaseAutoStatsMailer):
    def __init__(self, settings):
        super().__init__(settings)
        self.auto_mail_keys = settings.getlist('AUTO_MAIL_KEYS')
        self.auto_mail_filter_keys = settings.getlist('AUTO_MAIL_FILTER_KEYS')
        self.es_uri = settings.get('ES_URI', 'localhost:9200')
        self.es_index = settings.get('ES_INDEX', '')
        self.es_index_mapping_file = settings.get('ES_INDEX_MAPPING_FILE', 'mapping.json')
        self.es_client = None

    def spider_opened(self, spider):
        super().spider_opened(spider)
        if not self.es_index:
            return
        try:
            self.es_client = Elasticsearch([self.es_uri])
            self.create_index(spider)
        except Exception as e:
            self.logger.error(f'create es client failed, except: {e}')

    def spider_closed(self, spider):
        super().spider_closed(spider)

    def create_index(self, spider):
        if not self.es_client:
            return
        if self.es_client.indices.exists(index=self.es_index):
            spider.logger.info('es index(%s) already exists' % (self.es_index))
            return
        if not self.es_index_mapping_file or not os.path.exists(self.es_index_mapping_file):
            spider.logger.error('es index mapping file %s does not exist' % (self.es_index_mapping_file))
            return
        json_str = ''
        with open(self.es_index_mapping_file) as f:
            json_str = f.read()
        if json_str:
            self.es_client.indices.create(index=self.es_index, body=json_str)
        else:
            spider.logger.error('read es index mapping file(%s) failed' % (self.es_index_mapping_file))

    def set_msg_sended(self, res, item):
        if 'msg_sended' in res["_source"] and res["_source"]['msg_sended'] == True:
            return False
        item['msg_sended'] = True
        return True

    def need_send_mail(self, item, spider):
        if not self.es_client or "id" not in item.keys():
            return item
        res = self.es_client.get(index=self.es_index, id=item["id"], ignore=[HTTPStatus.NOT_FOUND])
        if not self.set_msg_sended(res, item):
            self.spider.logger.info(f'already_send_msg: body({item["title"]}), url({item["url"]})')
            return False
        res = self.es_client.index(index=self.es_index, id=item["id"], body=ItemAdapter(item).asdict())
        for key in self.auto_mail_filter_keys:
            if key in item['title']:
                self.spider.logger.info(f'need_filter: key({key}), body({item["title"]}), url({item["url"]})')
                return False
        for key in self.auto_mail_keys:
            if key in item['title']:
                self.spider.logger.info(f'need_send_mail: key({key}), body({item["title"]}), url({item["url"]})')
                return True
        return False

    def get_mail_body(self, item, spider):
        return f'{item["title"]} {item["url"]} {datetime.fromtimestamp(item["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")}'

    def get_subject(self, item, spider):
        return 'spider[%s] %s' % (spider.name, item['title'])
