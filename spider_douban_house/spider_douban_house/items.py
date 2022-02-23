# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HouseItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    group_name = scrapy.Field()
    url = scrapy.Field()
    timestamp = scrapy.Field()
    first_crawl_time = scrapy.Field()
    crawl_time = scrapy.Field()
    msg_sended = scrapy.Field()
