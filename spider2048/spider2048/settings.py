# Scrapy settings for spider2048 project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'spider2048'

SPIDER_MODULES = ['spider2048.spiders']
NEWSPIDER_MODULE = 'spider2048.spiders'
LOG_LEVEL = 'INFO'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'spider2048 (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

DUPEFILTER_DEBUG = True

MEDIA_ALLOW_REDIRECTS = True

#DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'
DUPEFILTER_CLASS = 'spider2048.esdupefilter.ESDupeFilter'

ES_URL = 'https://gwq5210.com/es'
ES_INDEX_NAME = 'spider2048_image'

AUTO_NOTIFY_STATS = True
AUTO_NOTIFY_RECIPIENTS = [457781132]
AUTO_NOTIFY_INTERVAL = 3600
AUTO_NOTIFY_ITEM_COUNT_INTERVAL = 20

MIRAI_API_URL = 'https://gwq5210.com/mirai'
MIRAI_API_KEY = ''
MIRAI_SENDER = 2423087292

BASE_URL = 'https://2048files.net/2048/'
PAGE_LIMIT_COUNT = 5
SCRAPY_CATEGORY_NAME = ["唯美清純"]
SCRAPY_TOP_TITLE = ["唯美清純"]

FILES_STORE = 'images'

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
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'spider2048.middlewares.Spider2048SpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'spider2048.middlewares.Spider2048DownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    'scrapy_spider_utils.auto_notify.AutoNotify': 3,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'spider2048.pipelines.Spider2048FilesPipeline': 1,
    'scrapy_spider_utils.eswriter.ESWriterPipeline': 2,
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
