import pandas as pd
import sys, os
from pandasdmx import Request
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

    class EcbDataExtractor():
        def __init__(self):
            pass

        def data_updater(self, ecb_series_dict: dict):
            engine = create_engine("mysql+pymysql://administrador:Xit7WdQ3YniY6YttHzBu@moneyprintersgobrr.c8r7otayptqb.eu-west-3.rds.amazonaws.com/EU")
            for key, value in ecb_series_dict.items():
                splitted_key = list(value)[0].split('.', 1)
                series = Request('ECB').data(resource_id=splitted_key[0], key=splitted_key[1]).write()
                series.index = series.index.get_level_values('TIME_PERIOD')
                new_df = pd.DataFrame(data=series)
                new_df.index.name = None
                new_df.rename(columns={'value': key}, inplace=True)
                new_df.index = pd.to_datetime(new_df.index, format='%Y-%m-%d')
                value_ = list(value)
                if value_[1] == '':
                    pass
                elif value_[1] == 'percentage':
                    new_df[new_df.select_dtypes(include=['number']).columns] /= 100
                elif value_[1] == 'thousands':
                    new_df[new_df.select_dtypes(include=['number']).columns] *= 1000
                elif value[1] == 'millions':
                    new_df[new_df.select_dtypes(include=['number']).columns] *= 1000000
                elif value[1] == 'billions':
                    new_df[new_df.select_dtypes(include=['number']).columns] *= 1000000000

                new_df.to_sql(key, con=engine, if_exists='replace')

    eu_ns_series_dict = {
            'M1': ['BSI.M.U2.N.V.M10.X.1.U2.2300.Z01.E', 'millions'],
            'M2': ['BSI.M.U2.N.V.M20.X.1.U2.2300.Z01.E', 'millions'],
            'M3': ['BSI.M.U2.N.V.M30.X.1.U2.2300.Z01.E', 'millions'],
            'ICP': ['ICP.M.U2.N.000000.4.INX', '']
    }

    extractor = EcbDataExtractor()
    extractor.data_updater(eu_ns_series_dict)

if __name__ == '__main__':
    main()