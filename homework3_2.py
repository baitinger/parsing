"""
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
"""

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['jobs_database']
collection = db['vacancy']

requested_salary = float(input('Введите искомую заработную плату\n'))

query = collection.find({
    "$or": [
        {
            "minimal salary": {"$gt": requested_salary}
        },
        {
            "maximal salary": {"$gt": requested_salary}
         }]
})
for row in query:
    print(row)
