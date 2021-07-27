# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HomeworkItem(scrapy.Item):
    _id = scrapy.Field()
    vacancy = scrapy.Field()
    salary = scrapy.Field()
    minimum_salary = scrapy.Field()
    maximum_salary = scrapy.Field()
    link = scrapy.Field()
    site = scrapy.Field()

