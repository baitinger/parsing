import requests
from lxml import html
from fake_headers import Headers


start_urls = ['https://leroymerlin.ru/catalogue/stolyarnye-izdeliya/?page=1']
header = Headers(headers=True).generate()
response = requests.get(url='https://leroymerlin.ru/product/evrovagonka-hvoya-12-5h96h2000-mm-sort-optima-10-sht-1-92-m-81947961/', headers=header)
root = html.fromstring(response.text)
total_pages = root.xpath('//*[@itemprop="image"]//@src')
print(type(total_pages))
print(len(total_pages))
print(total_pages)


total_pages = root.xpath('//*[@slot="price"]//text()')
print(total_pages)
print(len(total_pages))