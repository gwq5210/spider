# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class M3u8Item(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    page_url = scrapy.Field()
    img_url = scrapy.Field()
    m3u8_page_url = scrapy.Field()
    category = scrapy.Field()
    duration = scrapy.Field()
    tags = scrapy.Field()
    like_count = scrapy.Field()
    watch_count = scrapy.Field()
    first_crawl_time = scrapy.Field()
    crawl_time = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
