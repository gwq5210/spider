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

ES_URL = 'http://localhost:9200'
ES_INDEX_NAME = 'douban_house'

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
    'Cookie': '',
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
    'spider_douban_house.auto_notify.AutoNotify': 3,
}

MAIL_ENABLED = False
MAIL_HOST = 'smtp.qq.com'
MAIL_FROM = 'gwq5210@qq.com'
STATSMAILER_RCPTS = 'gwq5210@qq.com'
MAIL_USER = 'gwq5210@qq.com'
MAIL_PASS = ''
MAIL_PORT = 465
MAIL_SSL = True

AUTO_NOTIFY_STATS = False

NOTIFY_CONFIGS = [{
    'keys':
    ['??????', '????????????', '????????????', '??????', '????????????', '?????????', '??????', '?????????', '????????????', '?????????'],
    'filter_keys': ['??????'],
    'recipients': [457781132, 1329646082],
}]

MIRAI_API_URL = 'http://localhost:8080'
MIRAI_API_KEY = ''
MIRAI_SENDER = 2423087292

PAGE_LIMIT_COUNT = -1
DAY_LIMIT_COUNT = 7
CRAWL_INTERVAL = 600

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
