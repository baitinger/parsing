"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
записывающую собранные вакансии в созданную БД.
"""

from pymongo import MongoClient
import pandas as pd

df = pd.read_csv('/Users/tomas/Desktop/Python/jobs.csv')

client = MongoClient('localhost', 27017)
db = client['jobs_database']
collection = db['vacancy']

df.reset_index(inplace=True)
data = df.to_dict('records')

collection.insert_many(data)
