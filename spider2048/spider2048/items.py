# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Spider2048Item(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    image_title = scrapy.Field()
    thread_url = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
