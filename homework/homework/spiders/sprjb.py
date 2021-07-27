'''
Паучок для superjob.ru

Запуск только из консоли:

scrapy crawl sprjb
или
scrapy runspider sprjb.py

Этот паучок сделан по точно такому же принципу, как и hhru, комментарии к коду указаны там.
'''
import scrapy

from homework.items import HomeworkItem
import requests
from lxml import html
from fake_headers import Headers
import re


class SprjbSpider(scrapy.Spider):
    name = 'sprjb'
    allowed_domains = ['superjob.ru', 'russia.superjob.ru']
    start_urls = ['https://www.superjob.ru/vakansii/data-scientist.html?noGeo=1%3F&page=1']
    header = Headers(headers=True).generate()
    res = requests.get(url=start_urls[0], headers=header)
    root = html.fromstring(res.text)
    total_pages = root.xpath('//*[@class="_3zucV L1p51 _3ZDWc _2LZO7 iBQ9h GpoAF _3fOgw"]//text()')[-2]

    def start_requests(self):
        for page in range(1, int(self.total_pages) + 1):  # на superjob подсчет идет с 1
            url = 'https://www.superjob.ru/vakansii/data-scientist.html?noGeo=1%3F&page={}'.format(page)
            yield scrapy.Request(url, callback=self.parse_pages)

    def parse_pages(self, response, **kwargs):
        for href in response.xpath('//*[@class="_1h3Zg _2rfUm _2hCDz _21a7u"]//@href').extract():
            yield scrapy.Request('https://www.superjob.ru'+href, callback=self.parse)

    def parse(self, response, **kwargs):
        item = HomeworkItem()
        item['vacancy'] = response.xpath(
            '//*[@class="_1h3Zg rFbjy _2dazi _2hCDz"]//text()').extract_first()
        item['salary'] = ''.join(response.xpath(
            '//*[@class="_1h3Zg _2Wp8I _2rfUm _2hCDz"]//text()').extract())

        salary_without_nbsp = item['salary'].replace(u'\xa0', '')
        salary_min_max = re.findall(r"(\d+)", salary_without_nbsp)  # Регулярное выражение, которое ищет все числа.
        if len(salary_min_max) == 2:
            item['minimum_salary'] = int(salary_min_max[0])
            item['maximum_salary'] = int(salary_min_max[1])
        elif str(item['salary'])[:2] == 'от':
            item['minimum_salary'] = (int(salary_min_max[0]))
            item['maximum_salary'] = None
        elif str(item['salary'])[:2] == 'до':
            item['minimum_salary'] = None
            item['maximum_salary'] = (int(salary_min_max[0]))
        elif len(salary_min_max) == 1:
            item['minimum_salary'] = (int(salary_min_max[0]))
            item['maximum_salary'] = None
        else:
            item['minimum_salary'] = None
            item['maximum_salary'] = None

        item['link'] = response.url
        item['site'] = 'superjob.ru'

        return item
