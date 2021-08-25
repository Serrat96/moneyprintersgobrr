import pandas as pd
from fredapi import Fred
import sys, os

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep

# Path modification
current_folder = dirname(abspath(__file__))
for i in range(1): current_folder = dirname(abspath(current_folder))
sys.path.append(current_folder)

def main():
    class Extractor:
        def __init__(self, api_key):
            self.api_key = api_key

        #####
        def fred_data_updater(self, series_dict: dict):
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
                if os.path.isfile('.' + sep + key + sep + key + '.parquet'):
                    old_dataframe = pd.read_parquet('.' + sep + key + sep + key + '.parquet')
                    if old_dataframe.equals(new_dataframe):
                        print(key + ' ya existe y es igual, NO se ha actualizado')
                        not_updated_dfs.append(key)
                    else:
                        new_dataframe.to_parquet('.' + sep + key + sep + key + '.parquet')
                        print(key + ' actualizado')
                        updated_dfs.append(key)
                else:
                    print(key + ' es nuevo')
                    if not os.path.isdir('.' + sep + key):
                        os.mkdir('.' + sep + key)
                        print('Creado directorio para ' + key)
                    new_dataframe.to_parquet('.' + sep + key + sep + key + '.parquet')
                    print('Creado nuevo parquet para ' + key)
                    created_dfs.append(key)

            print(len(not_updated_dfs), 'Dataframes existentes y NO actualizados ', not_updated_dfs)
            print(len(updated_dfs), 'Dataframes existentes y actualizados ', updated_dfs)
            print(len(created_dfs), 'Dataframes NO existentes y creados ', created_dfs)


    fred_codes = {'M2NS': 'billions',
                  'CPIAUCNS': '',
                  'PCEPI': '',
                  'M1NS': 'billions'}
    extractor = Extractor('a7eca89fdf2905baea21d67b942c9ef7')
    extractor.fred_data_updater(fred_codes)

if __name__ == '__main__':
    main()