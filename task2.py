# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
# Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.

import requests
import json
import base64
from fake_headers import Headers

# логин и пароль для авторизации в Basic Auth на сайте http://httpbin.org/basic-auth/tomas/baitinger
password = 'tomas:baitinger'
# Кодируем в Base64
encoded_password = base64.b64encode(bytes(password, 'utf-8'))
# Генерируем header
header = Headers(headers=True).generate()
# Добавляем в header авторизацию для Basic Authorisation. Так как encoded_password является типом bytes, докодируем,
# для того, чтобы получить string.
header['Authorization'] = f'Basic {encoded_password.decode("utf-8")}'

url = 'http://httpbin.org/basic-auth/tomas/baitinger'

req = requests.get(url, headers=header)
print('HTTP - код: \n', req)
print('Заголовки: \n',  req.headers)
print('Ответ: \n',  req.text)

with open('server_answer.json', 'w') as write_file:
    json.dump(req.json(), write_file, indent=2)
