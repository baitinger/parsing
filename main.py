"""
Написать программу, которая собирает входящие письма из своего или тестового почтового ящика,
и сложить информацию о письмах в базу данных (от кого, дата отправки, тема письма, текст письма).
"""

from pymongo import MongoClient
from selenium import webdriver
# Импортируем ошибку, для ее последующей обработки в try except
from selenium.common.exceptions import ElementNotInteractableException

# Подключаем MongoDB
client = MongoClient('localhost', 27017)
database = client['hackermail']
collection = database['mail']

# Подключаем драйвер для selenium Chrome
driver = webdriver.Chrome(executable_path='/Users/tomas/Downloads/chromedriver')
# Заходим на страничку с логином в тестовый email
driver.get('https://mail.tutanota.com/login')

# Отправляем ключи в логин и пароль
driver.find_element_by_xpath('//*[@id="login-view"]/div[2]/div/div[1]/form/div[1]/div/div/div/div/div/input').send_keys('tomashacker@tutanota.com')
driver.find_element_by_xpath('//*[@id="login-view"]/div[2]/div/div[1]/form/div[2]/div/div/div/div/div/input').send_keys('Tomashacker1337')
driver.find_element_by_class_name('button-height').click()
# Неявное ожидание
driver.implicitly_wait(3)
# находим все емэйлы на страничке
mails = driver.find_elements_by_class_name('list-row')
for mail in mails:
    try:
        mail.click()
        sender = driver.find_element_by_xpath('//*[@id="mail-viewer"]/div[1]/div[1]/div/div')
        date = driver.find_element_by_xpath('//*[@id="mail-viewer"]/div[1]/div[3]/div/div[2]/small')
        topic = driver.find_element_by_xpath('//*[@id="mail-viewer"]/div[1]/div[3]/div/div[1]')
        text = driver.find_element_by_xpath('//*[@id="mail-body"]')
        email = {
            'sender': sender.text,
            'date': date.text,
            'topic': topic.text,
            'text': text.text
        }
        collection.insert_one(email)
    # Обрабатываем исключение, некоторые html объекты будут пустые, и при попытки клика на него, selenium выдаст error.
    # Как только мы кликаем пустой html объект, это значит что письма закончились. Выходим из цикла
    except ElementNotInteractableException:
        break

driver.quit()
