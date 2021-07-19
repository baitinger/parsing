from bs4 import BeautifulSoup as bs
from fake_headers import Headers
import lxml
import requests
import pandas as pd
import re

header = Headers(headers=True).generate()
# keyword - ключевое слово (вакансия), которую мы будем искать на сайтах.
keyword = input('Введите интересующую Вас вакансию:\n')

# Часть 1 - superjob.ru
url = f'https://russia.superjob.ru/vacancy/search/?keywords={keyword}'
response = requests.get(url=url, headers=header)
soup = bs(response.text, 'lxml')

# создаем датафрейм, в который будем добавлять данные после парсинга.
# С помощью метода set_option, pandas будет выводить нам все признаки (колонки) датафрейма.
pd.set_option('display.max_columns', None)
df = pd.DataFrame(columns=['vacancies', 'salaries', 'minimal salary', 'maximal salary', 'links', 'site'])


def parse_superjob(soup):
    '''
    Функция для парсинга сайта superjob. Сама функция ничего возвращать не будет, будет лишь добавлять данные в df.
    :param soup: BeatifulSoup parsed html page
    :return: doesn't return, makes changes in original dataframe
    '''
    global df
    # вакансии, зарплаты, сайт, ссылки находим по классам тегов на html страничке.
    vacancies = [i.text for i in soup.select('.f-test-vacancy-item ._2JivQ')]
    salaries = [i.text for i in soup.select('.f-test-text-company-item-salary ._2Wp8I')]
    site = str(soup.find(attrs={'property': 'og:site_name'})['content'])
    links = [site + str(el['href']) for el in soup.find_all(attrs={"href": True, "class": '_6AfZ9'})]
    # есть несколько вариантов з/п: 'до XXXX', 'от XXXX', 'XXXX - YYYY' или 'По договоренности'
    # Обработаем варианты, с помощью регулярных выражений (import re), добудем из string строк цифры.
    # создаем пустые списки для поиска min и max зарплаты.
    minimal_salary = []
    maximum_salary = []
    for salary in salaries:
        # на сайте superjob используются nbsp - беспрерывные пробелы(u'\xa0' или &NBSP), заменяем их на обычные пробелы.
        salary_without_nbsp = salary.replace(u'\xa0', '')
        salary_min_max = re.findall(r"(\d+)", salary_without_nbsp)  # Регулярное выражение, которое ищет все числа.
        if len(salary_min_max) == 2:
            minimal_salary.append(int(salary_min_max[0]))
            maximum_salary.append(int(salary_min_max[1]))
        elif salary[:2] == 'от':
            minimal_salary.append(int(salary_min_max[0]))
            maximum_salary.append(None)
        elif salary[:2] == 'до':
            minimal_salary.append(None)
            maximum_salary.append(int(salary_min_max[0]))
        else:
            minimal_salary.append(None)
            maximum_salary.append(None)
    # добавляем всю полученную информацию в dataframe
    df = df.append(pd.DataFrame(data={'vacancies': vacancies,
                                      'salaries': salaries,
                                      'minimal salary': minimal_salary,
                                      'maximal salary': maximum_salary,
                                      'links': links,
                                      'site': site}))
    # реиндексируем dataframe
    df.reset_index(inplace=True, drop=True)


# Вызываем функцию парсинга, передаем аргумент soup
print('Парсим страницу 1 на superjob.ru')
parse_superjob(soup=soup)

# Так как страниц поиска может быть много, будем парсить до тех пор, пока кнопка "Дальше" не исчезнет из html документа
while soup.find(attrs={'class': 'f-test-button-dalshe'}) is not None:
    # Если есть кнопка "Дальше" -> передаем soup адрес url следующей страницы, и снова парсим функцией parse_superjob()
    response = requests.get(url='https://russia.superjob.ru' +
                                str(soup.find(attrs={'class': 'f-test-button-dalshe'})['href']), headers=header)
    print(f'Парсим страницу {re.findall("[0-9]+", str(soup.find(attrs={"class": "f-test-button-dalshe"})["href"]))[0]}'
          f' на superjob.ru')
    soup = bs(response.text, 'lxml')
    parse_superjob(soup=soup)


# Часть 2 - hh.ru
url = f'https://hh.ru/search/vacancy?area=&fromSearchLine=true&st=searchVacancy&text={keyword}'
response = requests.get(url=url, headers=header)
soup = bs(response.text, 'lxml')

# Далее функция для парсинга hh.ru, смысл такой-же, с небольшими изменениями.
def parse_hh(soup):
    '''
    Функция для парсинга сайта hh.ru. Сама функция ничего возвращать не будет, будет лишь добавлять данные в df.
    :param soup: BeatifulSoup parsed html page
    :return: doesn't return, makes changes in original dataframe
    '''
    global df
    vacancies = [i.text for i in soup.find_all(attrs={'data-qa': 'vacancy-serp__vacancy-title'})]
    links = [el['href'] for el in soup.find_all(attrs={'data-qa': 'vacancy-serp__vacancy-title'})]
    site = 'https://hh.ru/'
    salaries = [i.text for i in soup.select('.vacancy-serp-item__sidebar .bloko-header-section-3_lite')]
    '''
    Возникшая сложность при парсинге hh.ru - если работодатель не указывает предлагаемую з/п - то класса, определяющего
    заработную плату в html попросту нет. При парсинге superjob.ru в таких случаях, указывалась з/п "По договоренности"
    Поэтому, при парсинге 50 вакансий, beatifulsoup может вернуть, например, всего лишь 13 заработных плат.
    Я сделал список link_of_jobs_with_salaries - в котором указываются ссылки на вакансию, у которой есть з/п
    В списке salaries - сами значения этих заработных плат.
    Далее я создаю dictionary в котором ключу "ссылка на вакансию" соответствует значение з/п
    И далее создав список final_salaries, который заполняю по принципу: перебираем все ссылки которые мы напарсили в 
    links, и если какая-то ссылка будет являться ключом dictionary - добавляем в значение з/п value этого ключа. 
    В противном случае, заполняем None, так как это значит, что з/п не была указана.
    '''
    link_of_jobs_with_salaries = [i.parent.parent.find(attrs={'data-qa': 'vacancy-serp__vacancy-title'}).attrs['href']
                                  for i in soup.select('.vacancy-serp-item__sidebar .bloko-header-section-3_lite')]
    dictionary = {link_of_jobs_with_salaries[i]: salaries[i] for i in range(len(link_of_jobs_with_salaries))}
    final_salaries = []
    for link in links:
        if link in dictionary.keys():
            final_salaries.append(dictionary.pop(link))
        else:
            final_salaries.append(None)
    minimal_salary = []
    maximum_salary = []
    for salary in final_salaries:
        if salary is not None:
            # на сайте hh.ru используются nnbsp - узкие беспрерывные пробелы(u'\u202F' или &NNBSP),
            # заменяем их на обычные пробелы.
            salary_without_nbsp = salary.replace(u'\u202F', '').replace(' ', '')
            salary_min_max = re.findall(r"(\d+)", salary_without_nbsp)
            if len(salary_min_max) == 2:
                minimal_salary.append(int(salary_min_max[0]))
                maximum_salary.append(int(salary_min_max[1]))
            elif salary[:2] == 'от':
                minimal_salary.append(int(salary_min_max[0]))
                maximum_salary.append(None)
            elif salary[:2] == 'до':
                minimal_salary.append(None)
                maximum_salary.append(int(salary_min_max[0]))
            else:
                minimal_salary.append(None)
                maximum_salary.append(None)
        else:
            minimal_salary.append(None)
            maximum_salary.append(None)
    df = df.append(pd.DataFrame(data={'vacancies': vacancies,
                                      'salaries': final_salaries,
                                      'minimal salary': minimal_salary,
                                      'maximal salary': maximum_salary,
                                      'links': links,
                                      'site': site}))
    df.reset_index(inplace=True, drop=True)

print('Парсим страницу 1 на hh.ru')
parse_hh(soup=soup)


while soup.find(attrs={'data-qa': 'pager-next'}) is not None:
    response = requests.get(url='https://hh.ru' +
                                str(soup.find(attrs={'data-qa': 'pager-next'})['href']), headers=header)
    print(f'Парсим страницу {int(re.findall("[0-9]+", str(soup.find(attrs={"data-qa": "pager-next"})["href"]))[0]) + 1}'
          f' на hh.ru')
    soup = bs(response.text, 'lxml')
    parse_hh(soup=soup)

# Проверяем получившийся dataframe
print(df.info())
# Выводим dataframe. Я для своего удобства вывожу в excel файл.
df.to_excel('../jobs.xlsx', encoding='utf-8')
