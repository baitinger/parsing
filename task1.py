# 1. Посмотреть документацию к API GitHub,
# разобраться как вывести список репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.

import requests
import json


def get_repos(user):
    url = f'https://api.github.com/users/{user}/repos'
    req = requests.get(url)
    repos = req.json()
    print(f'Репозитории пользователя {user}:\n')
    # Вывод названий репозиториев:
    for repo in repos:
        print(repo['name'])
    # Сохранение в .json формат:
    with open('repos.json', 'w') as write_file:
        json.dump(repos, write_file, indent=4)


get_repos(user=input('Введите имя пользователя GitHub:\n'))  # Я использую мое имя - baitinger
