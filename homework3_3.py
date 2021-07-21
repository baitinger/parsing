"""
3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
"""

from pymongo import MongoClient
import pandas as pd

client = MongoClient('localhost', 27017)
db = client['jobs_database']
collection = db['vacancy']

# Для начала считываем данные из MongoDB и сохраняем в формат датафрейма.
df = pd.DataFrame(list(collection.find({})))
# Читаем все вакансии после парсинга
parsed_data = pd.read_csv('/Users/tomas/Desktop/Python/jobs.csv')

# Уникальными в обоих датафреймах будут ссылки на вакансию. Поэтому будем сравнивать ссылки на вакансии.
# Если такая ссылка уже есть в нашей MongoDB, тогда мы ее добавлять не будем.
database_links = df['links'].to_list()
parsed_links = parsed_data['links'].to_list()
# Создаем новый список из тех ссылок, которых нет в списке ссылок MongoDB
new_links = [link for link in parsed_links if link not in database_links]

# Создаем датафрейм в которых сохраняем только те вакансии, ссылки которых не были найдены в MongoDB
new_data_to_add = parsed_data.loc[parsed_data['links'].isin(new_links)]

# Если все ссылки уже будут в MongoDB, то длина полученного датафрейма будет равна 0 и мы получим сообщение о том,
# что у нас "Нет новых данных".
if len(new_data_to_add) != 0:
    try:
        # Добавляем новые вакансии в базу данных MongoDB.
        collection.insert_many(new_data_to_add.to_dict('records'))
        print('Новые данные успешно занесены')
    except:
        print('Данные не занесены! Ошибка.')
else:
    print('Нет новых данных')
