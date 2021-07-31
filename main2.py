"""
Написать программу, которая собирает «Хиты продаж» с сайтов техники М.видео, ОНЛАЙН ТРЕЙД и складывает данные в БД.
Магазины можно выбрать свои. Главный критерий выбора: динамически загружаемые товары.

P.S. Мвидео не получилось, там сразу же просит капчу, не удалось обойти.
"""

from pymongo import MongoClient
from selenium import webdriver

client = MongoClient('localhost', 27017)
database = client['onlinetrade']
collection = database['hits']

driver = webdriver.Chrome(executable_path='/Users/tomas/Downloads/chromedriver')
driver.get('https://www.onlinetrade.ru')
driver.implicitly_wait(5)

# Пять раз кликаем на стрелочку в разделе "Хиты продаж", для того чтобы подгрузились все продукты. Там их всегда 12,
# поэтому с помощью 5 кликов получается увидеть все продукты.
for i in range(5):
    driver.find_element_by_xpath('//*[@id="tabs_hits"]/div[1]/span[2]').click()

# с помощью list comprehension получаем ссылки из всех найденных "Хитов продаж"
hits = [link.get_attribute('href') for link in driver.find_elements_by_xpath('//*[@id="tabs_hits"]/div['
                                                                             '2]/div/div/div/div[2]/a')]

for hit in hits:
    driver.get(hit)
    name = driver.find_element_by_tag_name('h1')
    price = driver.find_element_by_class_name('js__actualPrice')
    item = {
        'name': name.text,
        'price': price.text,
        'link': driver.current_url
    }
    print(item)
    collection.insert_one(item)
driver.quit()

