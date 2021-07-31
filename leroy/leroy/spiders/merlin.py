"""
Взять любую категорию товаров на сайте Леруа Мерлен. Собрать следующие данные:
название;
все фото;
параметры товара в объявлении.
"""

import scrapy
from ..items import LeroyItem
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse

class MerlinSpider(scrapy.Spider):
    name = 'merlin'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/catalogue/stolyarnye-izdeliya/?page=1']

    def parse(self, response: HtmlResponse, **kwargs):
        links = response.xpath('//*[@class="phytpj4_plp largeCard"]/a/@href').extract()
        for link in links:
            yield response.follow(link, callback=self.parse_links)

    def parse_links(self, response: HtmlResponse, **kwargs):
        name = response.xpath('//*[@class="header-2"]/text()').extract_first()
        source_images = response.xpath('//*[@slot="pictures"]//@src').extract()
        price = response.xpath('//*[@slot="price"]//text()').extract_first()
        yield LeroyItem(name=name, source_images=source_images, price=price)
