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

ES_URL = 'https://gwq5210.com/es'
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
COOKIES_ENABLED = True
COOKIES_DEBUG = False

# DOWNLOAD_TIMEOUT = 10

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'zh,zh-CN;q=0.9,en;q=0.8,zh-TW;q=0.7',
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
    # 'proxy_pool.ProxyPoolMiddleware': 543,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 600,
    'spider_douban_house.middlewares.DoubanHouseRetryMiddleware': 543,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'spider_douban_house.auto_notify.AutoNotify': 3,
}

DOUBAN_USERNAME = '18682085392'

AUTO_NOTIFY_STATS = False
AUTO_NOTIFY_RECIPIENTS = [457781132]

NOTIFY_CONFIGS = [{
    'keys':
    ['沙河', '巩华家园', '于新家园', '翠湖', '绿城雅居', '于辛庄', '翠明', '辛力屯', '兆丰家园', '顺沙路', '五福家园', '路庄', '朱辛庄', '豆各庄'],
    'filter_keys': ['求租'],
    'recipients': [457781132, 1329646082],
}]

MIRAI_API_URL = 'https://gwq5210.com/mirai'
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
