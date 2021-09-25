# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderMacwkItem(scrapy.Item):
    id = scrapy.Field()
    softid = scrapy.Field()
    soft_path = scrapy.Field()
    soft_url = scrapy.Field()
    language = scrapy.Field()
    title = scrapy.Field()
    title_des = scrapy.Field()
    description = scrapy.Field()
    modified_on = scrapy.Field()
    slug = scrapy.Field()
    website = scrapy.Field()
    soft_version_list = scrapy.Field()
    first_crawl_time = scrapy.Field()
    crawl_time = scrapy.Field()