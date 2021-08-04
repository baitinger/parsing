import pandas as pd


class OpenDataCsv:

    """Датасет с чешской open data,
     Список животных для "усыновления" в зоопарке Праги.
     Под усыновлением понимается взятие опеки и ежемесячный перевод денег на кормления и уход за животным.
     При этом животное все равно находится в зоопарке, а не у Вас дома.
     """

    def __init__(self):
        """
        Чтение csv файла с сайта opendata.praha.eu
        """
        self.url = 'https://opendata.praha.eu/dataset/9e9ec749-db30-4f0d-bb02-5b48cf090888/resource/f4432746' \
                   '-002d-45dd-bb09-d1719acf35fb/download/959c0e6f-5afb-489f-95ef-c9c2982963de-adopcezvirata.csv'
        self.dataframe = pd.read_csv(self.url, sep=';')

    def cleandata(self):
        """
        Чистка датасета на месте, там есть ненужная колонка с NaN данными.
        :return:
        """
        self.dataframe.drop(['Unnamed: 6'], axis=1, inplace=True)

    def get_data(self):
        """
        Разная статистика из датасета
        """
        print(f'Всего животных для усыновления: ', self.dataframe.count()['id'])
        print(f'Из них доступны для осмотра: ', int(self.dataframe.sum()['k_prohlidce']))
        print(f"Средняя стоимость усыновления животного в "
              f"зоопарке Праги: {round(self.dataframe.mean(axis=0)['cena'], 2)} Kč")

    def to_csv(self):
        """
        Сохранение очищеного csv файла
        """
        self.dataframe.to_csv('new.csv')


data = OpenDataCsv()
data.cleandata()
data.get_data()
data.to_csv()

