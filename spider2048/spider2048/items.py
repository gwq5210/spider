# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Spider2048Item(scrapy.Item):
    id = scrapy.Field()
    top_title = scrapy.Field()
    thread_title = scrapy.Field()
    thread_id = scrapy.Field()
    thread_time = scrapy.Field()
    file_urls = scrapy.Field()
    results = scrapy.Field()
    files = scrapy.Field()
    succeeded_count = scrapy.Field()
    failed_count = scrapy.Field()
    total_count = scrapy.Field()
    first_crawl_time = scrapy.Field()
    crawl_time = scrapy.Field()
