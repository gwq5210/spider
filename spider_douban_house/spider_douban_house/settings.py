# Scrapy settings for spider_douban_house project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'spider_douban_house'

SPIDER_MODULES = ['spider_douban_house.spiders']
NEWSPIDER_MODULE = 'spider_douban_house.spiders'
LOG_LEVEL = 'INFO'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

RETRY_ENABLED = True

DUPEFILTER_DEBUG = True

REDIRECT_ENABLED = False

MEDIA_ALLOW_REDIRECTS = False

#DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'
# DUPEFILTER_CLASS = 'spider_douban_house.esdupefilter.ESDupeFilter'

ES_URI = 'localhost:9200'
ES_INDEX = 'douban_house'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# DOWNLOAD_TIMEOUT = 10

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh,zh-CN;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'Cookie': 'll="108288"; bid=aUa6ZE9XX7w; push_doumail_num=0; __utmv=30149280.18531; _vwo_uuid_v2=D6BCDF104C3C62FEDBAB9BBD70F613998|3a5066384e70913d5c688334bcda1937; ct=y; push_noty_num=0; dbcl2="185310482:hw0RQFjfGhM"; _ga=GA1.2.1622722708.1640692505; __utmz=30149280.1645599036.22.6.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not provided); ck=3hQt; __utmc=30149280; ap_v=0,6.0; _pk_ref.100001.8cb4=["","",1645755677,"https://www.google.com.hk/"]; _pk_ses.100001.8cb4=*; __utma=30149280.1622722708.1640692505.1645705028.1645755677.28; __utmt=1; _pk_id.100001.8cb4=cf5b39d5ade74fb9.1640692501.28.1645755754.1645705028.; __utmb=30149280.22.4.1645755754937',
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'spider_douban_house.middlewares.SpiderDoubanHouseSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    # 'random_ua.RandomUserAgentMiddleware': 543,
    'proxy_pool.ProxyPoolMiddleware': 543,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 600,
    'spider_douban_house.middlewares.DoubanHouseRetryMiddleware': 543,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    # 'sendmail.SendMail': 1,
    # 'scrapy.extensions.statsmailer.StatsMailer': 2,
    'spider_douban_house.autostatsmailer.AutoStatsMailer': 3,
}

MAIL_ENABLED = False
MAIL_HOST = 'smtp.qq.com'
MAIL_FROM = 'gwq5210@qq.com'
STATSMAILER_RCPTS = 'gwq5210@qq.com'
MAIL_USER = 'gwq5210@qq.com'
MAIL_PASS = ''
MAIL_PORT = 465
MAIL_SSL = True

AUTO_MAIL_STATS = True
AUTO_MAIL_KEYS = ['沙河', '巩华家园', '于新家园']
AUTO_MAIL_FILTER_KEYS = ['求租', '合租']

MIRAI_HTTP_URL = 'http://localhost:8080'
MIRAI_HTTP_KEY = ''
MIRAI_SEND_QQ = 457781132
MIRAI_RECV_QQ = 202011284

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'eswriter.ESWriterPipeline': 4,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

PROXY_FILE = 'proxy.txt'
