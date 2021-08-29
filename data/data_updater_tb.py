import pandas as pd
from fredapi import Fred
import sys, os
from pandasdmx import Request
import requests
import json

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep

# Path modification
current_folder = dirname(abspath(__file__))
for i in range(1): current_folder = dirname(abspath(current_folder))
sys.path.append(current_folder)

def main():
    class FredExtractor:
        def __init__(self, api_key):
            self.api_key = api_key

        #####
        def fred_data_updater(self, series_dict: dict):
            print('USA')
            not_updated_dfs = []
            updated_dfs = []
            created_dfs = []
            for key, value in series_dict.items():
                fred = Fred(api_key=self.api_key)
                series = fred.get_series(key)
                new_dataframe = pd.DataFrame(series, columns=['Value'])
                new_dataframe.rename(columns={'Value': key}, inplace=True)
                if value == 'billions':
                    new_dataframe[new_dataframe.select_dtypes(include=['number']).columns] *= 1000000000
                elif value == '':
                    pass
                elif value == 'millions':
                    new_dataframe[new_dataframe.select_dtypes(include=['number']).columns] *= 1000000
                if os.path.isfile('.' + sep + 'usa' + sep + key + sep + key + '.parquet'):
                    old_dataframe = pd.read_parquet('.' + sep + 'usa' + sep + key + sep + key + '.parquet')
                    if old_dataframe.equals(new_dataframe):
                        print(key + ' ya existe y es igual, NO se ha actualizado')
                        not_updated_dfs.append(key)
                    else:
                        new_dataframe.to_parquet('.' + sep + 'usa' + sep + key + sep + key + '.parquet')
                        print(key + ' actualizado')
                        updated_dfs.append(key)
                else:
                    print(key + ' es nuevo')
                    if not os.path.isdir('.' + sep + 'usa' + sep + key):
                        os.makedirs('.' + sep + 'usa' + sep + key)
                        print('Creado directorio para ' + key)
                    new_dataframe.to_parquet('.' + sep + 'usa' + sep + key + sep + key + '.parquet')
                    print('Creado nuevo parquet para ' + key)
                    created_dfs.append(key)

            print(len(not_updated_dfs), 'Dataframes existentes y NO actualizados ', not_updated_dfs)
            print(len(updated_dfs), 'Dataframes existentes y actualizados ', updated_dfs)
            print(len(created_dfs), 'Dataframes NO existentes y creados ', created_dfs)


    fred_codes = {'M2NS': 'billions',
                  'CPIAUCNS': '',
                  'PCEPI': '',
                  'M1NS': 'billions'}
    #extractor = FredExtractor('a7eca89fdf2905baea21d67b942c9ef7')
    #extractor.fred_data_updater(fred_codes)


    class EcbExtractor():
        def __init__(self):
            pass

        def ecb_data_updater(self, series_dict: dict):
            print('EUROPE')
            not_updated_dfs = []
            updated_dfs = []
            created_dfs = []

            for key, value in series_dict.items():
                splitted_key = list(value)[0].split('.', 1)
                series = Request('ECB').data(resource_id=splitted_key[0], key=splitted_key[1]).write()
                series.index = series.index.get_level_values('TIME_PERIOD')
                new_dataframe = pd.DataFrame(data=series)
                new_dataframe.index.name = None
                new_dataframe.rename(columns={'value': key}, inplace=True)
                new_dataframe.index = pd.to_datetime(new_dataframe.index, format='%Y-%m-%d')
                if list(value)[1] == 'billions':
                    new_dataframe[new_dataframe.select_dtypes(include=['number']).columns] *= 1000000000
                elif list(value)[1] == '':
                    pass
                elif list(value)[1] == 'millions':
                    new_dataframe[new_dataframe.select_dtypes(include=['number']).columns] *= 1000000
                if os.path.isfile('.' + sep + 'euro' + sep + key + sep + key + '.parquet'):
                    old_dataframe = pd.read_parquet('.' + sep + 'euro' + sep + key + sep + key + '.parquet')
                    if old_dataframe.equals(new_dataframe):
                        print(key + ' ya existe y es igual, NO se ha actualizado')
                        not_updated_dfs.append(key)
                    else:
                        new_dataframe.to_parquet('.' + sep + 'euro' + sep + key + sep + key + '.parquet')
                        print(key + ' actualizado')
                        updated_dfs.append(key)
                else:
                    print(key + ' es nuevo')
                    if not os.path.isdir('.' + sep + 'euro' + sep + key):
                        os.makedirs('.' + sep + 'euro' + sep + key)
                        print('Creado directorio para ' + key)
                    new_dataframe.to_parquet('.' + sep + 'euro' + sep + key + sep + key + '.parquet')
                    print('Creado nuevo parquet para ' + key)
                    created_dfs.append(key)

            print(len(not_updated_dfs), 'Dataframes existentes y NO actualizados ', not_updated_dfs)
            print(len(updated_dfs), 'Dataframes existentes y actualizados ', updated_dfs)
            print(len(created_dfs), 'Dataframes NO existentes y creados ', created_dfs)

    ecb_codes = {
        'M1': ['BSI.M.U2.N.V.M10.X.1.U2.2300.Z01.E', 'millions'],
        'M2': ['BSI.M.U2.N.V.M20.X.1.U2.2300.Z01.E', 'millions'],
        'M3': ['BSI.M.U2.N.V.M30.X.1.U2.2300.Z01.E', 'millions'],
        'ICP': ['ICP.M.U2.N.000000.4.INX', '']
        }

    #extractor = EcbExtractor()
    #extractor.ecb_data_updater(ecb_codes)

    class BdeExtractor():
        def __init__(self):
            pass

        @staticmethod
        def bde_data_updater(series_dict: dict):
            print('SPAIN BDE')
            not_updated_dfs = []
            updated_dfs = []
            created_dfs = []

            for key, value in series_dict.items():
                new_dataframe = pd.read_csv(list(value)[0], encoding="ISO-8859-1")
                new_dataframe = new_dataframe[['NOMBRE DE LA SERIE', list(value)[2]]]
                new_dataframe.set_index('NOMBRE DE LA SERIE', inplace=True)
                new_dataframe.index.name = None
                new_dataframe = new_dataframe.iloc[5:-2]
                new_dataframe.index = new_dataframe.index.str.replace('ENE', '1')
                new_dataframe.index = new_dataframe.index.str.replace('FEB', '2')
                new_dataframe.index = new_dataframe.index.str.replace('MAR', '3')
                new_dataframe.index = new_dataframe.index.str.replace('ABR', '4')
                new_dataframe.index = new_dataframe.index.str.replace('MAY', '5')
                new_dataframe.index = new_dataframe.index.str.replace('JUN', '6')
                new_dataframe.index = new_dataframe.index.str.replace('JUL', '7')
                new_dataframe.index = new_dataframe.index.str.replace('AGO', '8')
                new_dataframe.index = new_dataframe.index.str.replace('SEP', '9')
                new_dataframe.index = new_dataframe.index.str.replace('OCT', '10')
                new_dataframe.index = new_dataframe.index.str.replace('NOV', '11')
                new_dataframe.index = new_dataframe.index.str.replace('DIC', '12')
                new_dataframe.index = pd.to_datetime(new_dataframe.index, format='%m %Y')
                if list(value)[1] == 'billions':
                    new_dataframe[new_dataframe.select_dtypes(include=['number']).columns] *= 1000000000
                elif list(value)[1] == '':
                    pass
                elif list(value)[1] == 'millions':
                    new_dataframe[new_dataframe.select_dtypes(include=['number']).columns] *= 1000000
                if os.path.isfile('.' + sep + 'spain' + sep + key + sep + key + '.parquet'):
                    old_dataframe = pd.read_parquet('.' + sep + 'spain' + sep + key + sep + key + '.parquet')
                    if old_dataframe.equals(new_dataframe):
                        print(key + ' ya existe y es igual, NO se ha actualizado')
                        not_updated_dfs.append(key)
                    else:
                        new_dataframe.to_parquet('.' + sep + 'spain' + sep + key + sep + key + '.parquet')
                        print(key + ' actualizado')
                        updated_dfs.append(key)
                else:
                    print(key + ' es nuevo')
                    if not os.path.isdir('.' + sep + 'spain' + sep + key):
                        os.makedirs('.' + sep + 'spain' + sep + key)
                        print('Creado directorio para ' + key)
                    new_dataframe.to_parquet('.' + sep + 'spain' + sep + key + sep + key + '.parquet')
                    print('Creado nuevo parquet para ' + key)
                    created_dfs.append(key)

            print(len(not_updated_dfs), 'Dataframes existentes y NO actualizados ', not_updated_dfs)
            print(len(updated_dfs), 'Dataframes existentes y actualizados ', updated_dfs)
            print(len(created_dfs), 'Dataframes NO existentes y creados ', created_dfs)

    class IneExtractor():
        def __init__(self):
            pass

        @staticmethod
        def ine_data_updater(series_dict: dict):
            print('SPAIN INE')
            not_updated_dfs = []
            updated_dfs = []
            created_dfs = []

            for key, value in series_dict.items():
                url = 'https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/' + list(value)[0] + '?date=' + list(value)[2] + ':' + list(value)[3]
                new_dataframe = requests.get(url).json()['Data']
                with open('./data.json', 'w') as f:
                    json.dump(new_dataframe, f)
                new_dataframe = pd.read_json('./data.json')
                os.remove('./data.json')
                new_dataframe['FK_Periodo'] = new_dataframe['FK_Periodo'].astype(str) + ' ' + new_dataframe['Anyo'].astype(str)
                new_dataframe = new_dataframe[['FK_Periodo', 'Valor']]
                new_dataframe.set_index('FK_Periodo', inplace=True)
                new_dataframe.index = pd.to_datetime(new_dataframe.index, format='%m %Y')
                if list(value)[1] == 'billions':
                    new_dataframe[new_dataframe.select_dtypes(include=['number']).columns] *= 1000000000
                elif list(value)[1] == '':
                    pass
                elif list(value)[1] == 'millions':
                    new_dataframe[new_dataframe.select_dtypes(include=['number']).columns] *= 1000000
                if os.path.isfile('.' + sep + 'spain' + sep + key + sep + key + '.parquet'):
                    old_dataframe = pd.read_parquet('.' + sep + 'spain' + sep + key + sep + key + '.parquet')
                    if old_dataframe.equals(new_dataframe):
                        print(key + ' ya existe y es igual, NO se ha actualizado')
                        not_updated_dfs.append(key)
                    else:
                        new_dataframe.to_parquet('.' + sep + 'spain' + sep + key + sep + key + '.parquet')
                        print(key + ' actualizado')
                        updated_dfs.append(key)
                else:
                    print(key + ' es nuevo')
                    if not os.path.isdir('.' + sep + 'spain' + sep + key):
                        os.makedirs('.' + sep + 'spain' + sep + key)
                        print('Creado directorio para ' + key)
                    new_dataframe.to_parquet('.' + sep + 'spain' + sep + key + sep + key + '.parquet')
                    print('Creado nuevo parquet para ' + key)
                    created_dfs.append(key)

            print(len(not_updated_dfs), 'Dataframes existentes y NO actualizados ', not_updated_dfs)
            print(len(updated_dfs), 'Dataframes existentes y actualizados ', updated_dfs)
            print(len(created_dfs), 'Dataframes NO existentes y creados ', created_dfs)


    bde_codes = {
            'M1': ['https://www.bde.es/webbde/es/estadis/infoest/series/be0113.csv', 'millions', 'D_MESM1EELIPBIF'],
            'M2': ['https://www.bde.es/webbde/es/estadis/infoest/series/be0113.csv', 'millions', 'D_MESM2EELIPBIF'],
            'M3': ['https://www.bde.es/webbde/es/estadis/infoest/series/be0113.csv', 'millions', 'D_MESM3EELIPBIF']
        }

    ine_codes = {
                    'IPC': ['IPC206446', '', '19000101', '21000801'],
                    'IPC_ANNUAL_PERCENTAGE': ['IPC206448', '', '19000101', '21000101'],
                    'IPC_MONTHLY_PERCENTAGE': ['IPC206449', '', '19000101', '21000101']
    }

    #extractor = BdeExtractor()
    #extractor.bde_data_updater(bde_codes)

    extractor = IneExtractor()
    extractor.ine_data_updater(ine_codes)



if __name__ == '__main__':
    main()
