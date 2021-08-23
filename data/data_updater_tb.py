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
        def fred_data_updater(self, series_list: list):
            not_updated_dfs = []
            updated_dfs = []
            created_dfs = []
            for element in series_list:
                fred = Fred(api_key=self.api_key)
                series = fred.get_series(element)
                new_dataframe = pd.DataFrame(series, columns=['Value'])
                if os.path.isfile('.' + sep + element + sep + element + '.parquet'):
                    old_dataframe = pd.read_parquet('.' + sep + element + sep + element + '.parquet')
                    if old_dataframe.equals(new_dataframe):
                        print(element + ' ya existe y es igual, NO se ha actualizado')
                        not_updated_dfs.append(element)
                    else:
                        new_dataframe.to_parquet('.' + sep + element + sep + element + '.parquet')
                        print(element + ' actualizado')
                        updated_dfs.append(element)
                else:
                    print(element + ' es nuevo')
                    if not os.path.isdir('.' + sep + element):
                        os.mkdir('.' + sep + element)
                        print('Creado directorio para ' + element)
                    new_dataframe.to_parquet('.' + sep + element + sep + element + '.parquet')
                    print('Creado nuevo parquet para ' + element)
                    created_dfs.append(element)

            print(len(not_updated_dfs), 'Dataframes existentes y NO actualizados ', not_updated_dfs)
            print(len(updated_dfs), 'Dataframes existentes y actualizados ', updated_dfs)
            print(len(created_dfs), 'Dataframes NO existentes y creados ', created_dfs)


    fred_codes = ['M2NS', 'CPIAUCNS', 'PCEPI', 'M1NS']
    extractor = Extractor('a7eca89fdf2905baea21d67b942c9ef7')
    extractor.fred_data_updater(fred_codes)

if __name__ == '__main__':
    main()