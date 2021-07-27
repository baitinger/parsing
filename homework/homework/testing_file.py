
"""
THIS FILE IS ONLY INTENDED FOR TEST PURPOSES, IT DOES NOT AFFECT SCRAPY
Я тестировал xpath'ы здесь, чтобы понять что я парсю то что нужно
"""

import requests
from lxml import html
from fake_headers import Headers


start_urls = ['https://www.superjob.ru/vakansii/data-scientist.html?noGeo=1?page=1']
header = Headers(headers=True).generate()
response = requests.get(url='https://www.superjob.ru/vakansii/data-scientist.html?noGeo=1', headers=header)
root = html.fromstring(response.text)
total_pages = root.xpath('//*[@class="_3zucV L1p51 _3ZDWc _2LZO7 iBQ9h GpoAF _3fOgw"]//text()')[-2]
print(type(total_pages))
print(len(total_pages))

# a = root.xpath('//a[contains(@href, "https://hh.ru/vacancy/")]/@href')
# print(len(a))
#
# import json
# with open('vacancytest.json') as file:
#     data = file.read()
#
# data = json.loads(data)
# print(data)