# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class VideoItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    name = scrapy.Field()
    tags = scrapy.Field()
    path = scrapy.Field()
    url = scrapy.Field()
    season_id = scrapy.Field()
    status = scrapy.Field()
