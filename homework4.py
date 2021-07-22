from lxml import html
import requests
import pandas as pd

# из-за fake_headers некоторые сайты не давали нормально парсить, поэтому я нашел header, который работал в 100% случаев
header = {'Accept': '*/*', 'Connection': 'keep-alive',
          'User-Agent': 'Mozilla/5.0 (X11; Linux i686 on x86_64; rv:61.0.2) Gecko/20100101 Firefox/61.0.2',
          'Accept-Language': 'en-US;q=0.5,en;q=0.3', 'Cache-Control': 'max-age=0', 'DNT': '1',
          'Referer': 'https://google.com', 'Pragma': 'no-cache'}

# создаем датафрейм, где будет хранить список новостей с сайтов.
df = pd.DataFrame(columns=['site', 'news', 'link', 'date'])

""" Часть 1. lenta.ru """
url = 'https://lenta.ru'
response = requests.get(url=url, headers=header)
root = html.fromstring(response.text)
# У ленты гораздо удобнее создан блок с главными новостями, у них одинаковая html структура.
# находим нужный узел, и в цикле проходим по всем детям этого узла.
result = root.xpath('//*[@id="root"]/section[2]/div/div/div[2]/div[1]/section/div/node()')[1:]

for i in result:
    news = i.xpath('*/text()')
    link = i.xpath('*/@href')
    # для того, чтобы выцепить время создания новости, придется пройти внутрь каждой новости, получив новый request
    # и взять оттуда дату.
    temporary_response = requests.get(url=(url + str(link[0])), headers=header)
    temporary_root = html.fromstring(temporary_response.text)
    # Забираем дату:
    date = temporary_root.xpath('//*[@id="root"]/div[4]/div/div/div[2]/div[2]/div/div[1]/div[1]/div[1]/time/text()')
    # Закидываем данные в датафрейм.
    df = df.append({'site': str(url),
                    'news': str(news[0]),
                    'link': url + str(link[0]),
                    'date': str(date[0])}, ignore_index=True)


""" Часть 2. Яндекс """
url = 'https://yandex.ru/news'
response = requests.get(url=url, headers=header)
root = html.fromstring(response.text)


def xpath_yandex(root):
    '''
    На сайте яндекс новостей, главные новости, имеют разную структуру, поэтому я воспользовался условиями, такие как:
    a[contains(@class, "mg-card__link")] или h2[contains(@class, "mg-card__title")]
    Для того, чтобы не забирать абсолютно все новости, а лишь главные - я дополнительно указал путь в XPath только для
    div с главными новостями.
    По сути это то же самое, что и BeatifulSoup.find_all(), просто немного в другом виде.
    :param root: html.fromstring(response.text)
    :return: returns nothing, updates dataframe
    '''
    global df
    url = 'https://yandex.ru/news'

    links_path = root.xpath('//*[@id="neo-page"]/div/div[2]/div/div[1]/div[1]//a[contains(@class, "mg-card__link")]')
    link = [i.xpath('./@href')[0] for i in links_path]

    news_path = root.xpath('//*[@id="neo-page"]/div/div[2]/div/div[1]/div[1]//h2[contains(@class, "mg-card__title")]')
    news = [i.xpath('./text()')[0] for i in news_path]

    date_path = root.xpath(
        '//*[@id="neo-page"]/div/div[2]/div/div[1]/div[1]//span[contains(@class, "mg-card-source__time")]')
    date = [i.xpath('./text()')[0] for i in date_path]

    df = df.append(pd.DataFrame(data={'site': url,
                                      'news': news,
                                      'link': link,
                                      'date': date}))


xpath_yandex(root=root)

# Сохраняю в excel, для своего удобства.
df.to_excel('../news.xlsx', encoding='utf-8', index=False)
