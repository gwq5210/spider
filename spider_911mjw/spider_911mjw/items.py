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
    videe_url_info_list = scrapy.Field()
    description = scrapy.Field()
    video_count = scrapy.Field()
    director = scrapy.Field()
    starring = scrapy.Field()
    country_region = scrapy.Field()
    language = scrapy.Field()
    premiere = scrapy.Field()
    alias = scrapy.Field()
    imdb_code = scrapy.Field()
    score = scrapy.Field()
    duration = scrapy.Field()
    screenwriter = scrapy.Field()
    release_date = scrapy.Field()
    official_website = scrapy.Field()
    img_url = scrapy.Field()
    first_crawl_time = scrapy.Field()
    crawl_time = scrapy.Field()
