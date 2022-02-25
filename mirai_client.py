import requests
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class MiraiClient:
  def __init__(self, sender, api_key='', api_url='http://localhost:8080'):
    self.api_url = api_url
    self.sender = sender
    self.api_key = api_key
    self.session = ''
    self.verify_url = urljoin(self.api_url, '/verify')
    self.bind_url = urljoin(self.api_url, '/bind')
    self.release_url = urljoin(self.api_url, '/release')
    self.send_msg_url = urljoin(self.api_url, '/sendFriendMessage')
    self.bind()

  def __del__(self):
    self.release()

  def bind(self):
      res_json = requests.post(self.verify_url, json={
          'verifyKey': self.api_key
      }).json()
      logger.info(f'verify {res_json}')
      self.session = res_json['session']
      res_json = requests.post(self.bind_url, json={
          'sessionKey': self.session,
          'qq': self.sender,
      }).json()
      logger.info(f'bind_qq {res_json}')

  def release(self):
      res_json = requests.post(self.bind_url, json={
          'sessionKey': self.session,
          'qq': self.sender,
      }).json()
      logger.info(f'release_qq {res_json}')

  def send_text_msg(self, recipient, msg):
      res_json = requests.post(self.send_msg_url, json={
          "sessionKey": self.session,
          "target": recipient,
          "messageChain": [
              {"type": "Plain", "text": msg},
          ]
      }).json()
      logger.info(f'send_text_msg {res_json}')
