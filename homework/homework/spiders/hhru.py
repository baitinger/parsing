'''
Паучок для hh.ru

Запуск только из консоли:

scrapy crawl hhru
или
scrapy runspider hhru.py
'''
import scrapy

from homework.items import HomeworkItem
# Импорт объекта Item из Scrapy. Почему-то PyCharm ругается, но код отлично запускается из консоли.
import requests
from lxml import html
from fake_headers import Headers
import re


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/vacancies/data-scientist?page=0']
    header = Headers(headers=True).generate()
    res = requests.get(url=start_urls[0], headers=header)
    root = html.fromstring(res.text)
    # с помощью requests.get я узнаю по xpath точное количество страниц, выданных по поиску.
    total_pages = root.xpath('//*[@id="HH-React-Root"]/div/div/div[3]/div[2]/div/div[8]/div/span[2]/span[3]/a/span/text()')[0]

    def start_requests(self):
        for page in range(int(self.total_pages)):  # на hh.ru подсчет идет с 0
            url = 'https://hh.ru/vacancies/data-scientist?page={}'.format(page)
            yield scrapy.Request(url, callback=self.parse_pages)

    def parse_pages(self, response, **kwargs):
        # с помощью xpath получаем все ссылки на вакансии.
        for href in response.xpath('//a[contains(@href, "https://hh.ru/vacancy/")]/@href').extract():
            yield scrapy.Request(href, callback=self.parse)

    def parse(self, response, **kwargs):
        # создаем новый объект класса Item:
        item = HomeworkItem()
        # Складываем в атрибуты объекта Item искомые значения xpath
        item['vacancy'] = response.xpath('//*[@id="HH-React-Root"]/div/div/div/div/div[1]/div[1]/div/div/h1/text()').extract_first()
        item['salary'] = response.xpath(
            '//*[@id="HH-React-Root"]/div/div[1]/div/div/div/div[1]/div/div/p/span/text()').extract_first()

        # Далее фокус с преобразованием string с заработной платой с помощью регулярных выражений
        # Например заработная плата может быть запарсена как "от 100 000 до 200 000 руб."
        # Нам необходимо вытащить оттуда только 100000 и 200000, и сложить их в minimal и maximum salary.
        salary_without_nbsp = item['salary'].replace(u'\xa0', '')
        # строка выше заменяет беспрерывные пробелы из salary на обычные пробелы.
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
        item['site'] = 'hh.ru'

        return item

