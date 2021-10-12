# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderNesItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    name = scrapy.Field()
    type = scrapy.Field()
    location = scrapy.Field()
    img_url = scrapy.Field()
    description = scrapy.Field()
    click = scrapy.Field()
    category_id = scrapy.Field()
    create_time = scrapy.Field()
    modified_time = scrapy.Field()
    is_deleted = scrapy.Field()
    first_crawl_time = scrapy.Field()
    crawl_time = scrapy.Field()
    file_urls = scrapy.Field()
    results = scrapy.Field()
    files = scrapy.Field()
    succeeded_count = scrapy.Field()
    failed_count = scrapy.Field()
    total_count = scrapy.Field()