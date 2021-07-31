# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LeroyItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    source_images = scrapy.Field()
    price = scrapy.Field()
    pass
