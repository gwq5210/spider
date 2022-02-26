import requests
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class MiraiClient:
    def __init__(self, sender, api_key, api_url='http://localhost:8080'):
        self.api_url = api_url
        self.sender = int(sender)
        self.api_key = api_key
        self.session = ''
        self.verify_url = urljoin(self.api_url, '/verify')
        self.bind_url = urljoin(self.api_url, '/bind')
        self.release_url = urljoin(self.api_url, '/release')
        self.send_msg_url = urljoin(self.api_url, '/sendFriendMessage')
        self.bind()

    @classmethod
    def from_settings(cls, settings):
        client = cls(
            sender=settings.getint('MIRAI_SENDER', 0),
            api_key=settings.get('MIRAI_API_KEY'),
            api_url=settings.get('MIRAI_API_URL', 'http://localhost:8080')
        )
        return client

    def __del__(self):
        self.release()

    def bind(self):
        res_json = requests.post(self.verify_url, json={
            'verifyKey': self.api_key
        }).json()
        logger.info(f'client verify {res_json}')
        self.session = res_json['session']
        res_json = requests.post(self.bind_url, json={
            'sessionKey': self.session,
            'qq': self.sender,
        }).json()
        logger.info(f'client bind_qq {res_json}')

    def release(self):
        res_json = requests.post(self.bind_url, json={
            'sessionKey': self.session,
            'qq': self.sender,
        }).json()
        logger.info(f'client release_qq {res_json}')

    def send_text_msg(self, recipients, msg):
        if type(recipients) is int or type(recipients) is str:
            self._send_text_msg(recipients, msg)
            return
        for recipient in recipients:
            self._send_text_msg(recipient, msg)

    def _send_text_msg(self, recipient, msg):
        res_json = requests.post(self.send_msg_url, json={
            "sessionKey": self.session,
            "target": int(recipient),
            "messageChain": [
                {"type": "Plain", "text": msg},
            ]
        }).json()
        logger.info(f'client_send_text_msg({msg}) to ({recipient}) {res_json}')
