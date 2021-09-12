import pandas as pd
from fredapi import Fred
import sys, os
from sqlalchemy import create_engine

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep

# Path modification
current_folder = dirname(abspath(__file__))
for i in range(1):
    current_folder = dirname(abspath(current_folder))
sys.path.append(current_folder)


def main():
    class FredDataExtractor():
        def __init__(self, api_key: str):
            self.api_key = api_key

        def data_updater(self, fred_series_dict: dict):
            fred = Fred(self.api_key)
            engine = create_engine("mysql+pymysql://administrador:Xit7WdQ3YniY6YttHzBu@moneyprintersgobrr.c8r7otayptqb.eu-west-3.rds.amazonaws.com/moneyprintersgobrr")
            db_df = pd.DataFrame()
            for key, value in fred_series_dict.items():
                series = fred.get_series(key)
                new_df = pd.DataFrame(series, columns=['Value'])
                new_df.rename(columns={'Value': key}, inplace=True)
                if value == '':
                    pass
                elif value == 'pct':
                    new_df[new_df.select_dtypes(include=['number']).columns] /= 100
                elif value == 'thousands':
                    new_df[new_df.select_dtypes(include=['number']).columns] *= 1000
                elif value == 'millions':
                    new_df[new_df.select_dtypes(include=['number']).columns] *= 1000000
                elif value == 'billions':
                    new_df[new_df.select_dtypes(include=['number']).columns] *= 1000000000

                db_df = pd.concat([db_df, new_df], axis=1)

            db_df.reset_index(inplace=True)
            db_df = db_df.rename({"index": "date"}, axis=1)
            db_df.to_sql('USA', con=engine, if_exists='replace', index=False)

    fred_ns_series_dict = {'M2NS': 'billions',  # M2 no estacional
                        'CPIAUCNS': '',  # CPI no estacional
                        'PCEPI': '',  # PCE no estacional
                        'M1NS': 'billions',  # M1 no estacional
                        'UNRATENSA': 'pct', # Porcentaje de personas desempleadas (respecto del total de la fuerza de trabajo) no estacional
                        'LNU03000000': 'thousands',  # Personas desempleadas no estacional
                        'CUUR0000SA0R': '',  # Poder adquisitivo no estacional
                        'M1V': '',  # Velocidad de la M1 no estacional quarterly
                        'M2V': '',  # Velocidad de la M2 no estacional quarterly
                        'GDP': 'billions',  # GDP estacional quarterly
                        'IPB50001N': '',  # Indice produccion industrial no estacional 2017=100
                        'USSTHPI': '',  # Indice precio vivienda USA 1980Q1 = 100
                        }

    extractor = FredDataExtractor('a7eca89fdf2905baea21d67b942c9ef7')
    extractor.data_updater(fred_ns_series_dict)

if __name__ == '__main__':
    main()