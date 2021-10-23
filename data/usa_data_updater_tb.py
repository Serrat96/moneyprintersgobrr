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
            engine = create_engine(
                "mysql+pymysql://administrador:Xit7WdQ3YniY6YttHzBu@moneyprintersgobrr.c8r7otayptqb.eu-west-3.rds.amazonaws.com/moneyprintersgobrr")
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
                           'UNRATENSA': 'pct',
                           # Porcentaje de personas desempleadas (respecto del total de la fuerza de trabajo) no estacional
                           'LNU03000000': 'thousands',  # Personas desempleadas no estacional
                           'CUUR0000SA0R': '',  # Poder adquisitivo no estacional
                           'M1V': '',  # Velocidad de la M1 no estacional quarterly
                           'M2V': '',  # Velocidad de la M2 no estacional quarterly
                           'GDP': 'billions',  # GDP estacional quarterly
                           'IPB50001N': '',  # Indice produccion industrial no estacional 2017=100

                           # HOUSING INDEX
                           'CUUR0000SEHA': '',
                           # Rent of Primary Residence in U.S. City Average Index 1982-1984=100 not seasonal
                           'USSTHPI': '',  # Indice precio vivienda USA 1980Q1 = 100 not seasonal
                           'SPCS20RSA': '',  # S&P/Case-Shiller 20-City Composite

                           # FUELS INDEX
                           'CUUR0000SETB01': '',  # Gasoline (All Types) in U.S. Index 1982-1984=100 not seasonal
                           'CUUR0000SEHE': '',  # Fuel Oil and Other Fuels Index 1982-1984=100 not seasonal
                           'CUUR0000SAH2': '',  # Fuels and Utilities Index 1982-1984=100 not seasonal
                           'CUUR0000SETB': '',  # Motor Fuel Index 1982-1984=100 not seasonal
                           'CUUS0000SEHE02': '',    # Propane, Kerosene, and Firewood Index Dec 1986=100 not seasonal

                           # MEDICAL SERVICES INDEX
                           'CUUR0000SAS': '',  # Services in U.S. not seasonal Index 1982-1984=100 not seasonal
                           'CUUR0000SEMD': '',  # Hospital and Related Services Index 1982-1984=100 not seasonal
                           'CUUR0000SAM2': '',  # Medical Care Services Index 1982-1984=100 not seasonal

                           # RECREATION SERVICES INDEX
                           'CUUS0000SARS': '',  # Recreation Services Index Dec 2009=100 not seasonal

                           # PROFESSIONAL SERVICES INDEX
                           'CUUR0000SEMC': '',  # Professional Services Index 1982-1984=100 not seasonal

                           # TRANSPORTATION SERVICES INDEX
                           'CPITRNSL': '',  # Transportation Index 1982-1984=100 not seasonal
                           'CUUR0000SAS4': '',  # Transportation Services Index 1982-1984=100 not seasonal
                           'WPU301301': '',  # Deep Sea Water Transportation Index Dec 2008=100 not seasonal
                           'PCU483211483211': '',  # Inland Water Freight Transportation Index Dec 1990=100 not seasonal
                           'PCU483483': '',  # Water Transportation Index Dec 2003=100 not seasonal

                           # IT SERVICES INDEX
                           'CUUR0000SEEE': '',
                           # Information Technology, Hardware Services Index Dec 1988=100 not seasonal
                           'CUUR0000SERA02': '',
                           # Cable and Satellite Television Service Index Dec 1983=100 not seasonal
                           'CUUR0000SEED': '',  # Telephone Services Index Dec 1997=100 not seasonal

                           # HYGIENE SERVICES INDEX
                           'CUUR0000SEGC': '',  # Personal care Services Index 1982-1984=100 not seasonal
                           'CUUR0000SEGD03': '',  # Laundry and Dry Cleaning Index Dec 1997 = 100 not seasonal
                           'CUUR0000SEHG': '',  # Water and Sewer and Trash Collection Index dec 1997=100 not seasonal

                           # MISCELLANEOUS SERVICES INDEX
                           'CUSR0000SEGD': '', # Miscellaneous Personal Services Index 1982-1984=100 not seasonal

                           # ELECTRICITY INDEX
                           'CUUR0000SEHF01': '',  # Electricity Index 1982-1984=100 not seasonal

                           # FOOD & BEVERAGES INDEX
                           'CPIFABNS': '',  # Food and Beverages Index 1982-1984=100 not seasonal
                           'CPIUFDNS': '',  # Food Index 1982-1984=100 not seasonal
                           'CUUR0000SAF11': '',  # Food at Home 1982-1984=100 not seasonal
                           'CUUR0000SEFV': '',  # Food Away from Home 1982-1984=100 not seasonal
                           'CUUS0000SEFR': '',  # Sugar and Sweets Index 1982-1984=100 not seasonal
                           'CUUR0000SEFR02': '',  # Candy and Chewing Gum Index Dec 1997=100 not seasonal
                           'CUUS0000SEFS': '',  # Fats and Oils Index 1982-1984=100 not seasonal
                           'CUUS0000SAF112': '',  # Meats, Poultry, Fish, and Eggs Index 1982-1984=100 not seasonal
                           'CUUR0000SS61031': '',   # Pet Food Index Dec 1997=100 not seasonal
                           'CUUR0000SEFP01': '',    # Coffee Index 1982-1984=100 not seasonal
                           'CUUS0000SAF111': '',    # Cereals and Bakery Products Index 1982-1984=100 not seasonal

                           #TRAVEL INDEX
                           'CUUR0000SETG01': '',    # Airline Fares Index 1982-1984=100 not seasonal

                           # RENT INDEX
                           'CUUR0000SEHA': '',  # Rent of Primary Residence 1982-1984=100 not seasonal
                           'CUUR0000SEHC01': '',  # Owners' Equivalent Rent of Primary Residence Index Dec 1982=100 not seasonal

                           # GOODS INDEX
                           'CUUR0000SAD': '',  # Durables 1982-1984=100 not seasonal
                           'CUUR0000SAN': '',  # Non durables 1982-1984=100 not seasonal
                           'M04186USM350NNBR': '',  # Durable Commodities Index 1957-1959 = 100 not seasonal

                           # WATER INDEX
                           'PCU3121123121120': '',  # Bottled Water Manufacturing Index Dec 2000=100 not seasonal
                           'WPU106601': '',  # Domestic Water Heaters Index 1982 = 100 not seasonal
                           'PCU32612232612213': '',  # Plastics Water Pipe Index Jun 1987=100 not seasonal

                           # HOUSEHOLD INDEX
                           'WPU122': '',  # Commercial Furniture Index 1982=100 not seasonal
                           'PCU33523352': '',  # Household Appliance Manufacturing Index Dec 1984=100 not seasonal
                           'WPU12': '',  # Furniture and Household Durables not seasonal
                           'CUUS0000SAH3': '',  # Household Furnishings and Operations Index 1982-1984=100 not seasonal

                           # FURNITURE INDEX
                           'CUUS0000SAH3': '',   #Household Furnishings Index 1982-1984=100 not seasonal

                           # APPAREL INDEX
                           'CPIAPPNS': '',  # Apparel Index 1982-1984=100 not seasonal
                           'CUUR0000SAH1': '',   # Shelter Index 1982-1984=100 not seasonal
                           'CUUR0000SAA2': '',  # Women's and Girls' Apparel Index 1982-1984=100 not seasonal
                           
                           # ALCOHOL INDEX
                           'CUUS0000SAF116': '',  # Alcoholic Beverages Index 1982-1984=100 not seasonal
                           'CUSR0000SEFW': '',  # Alcoholic Beverages at Home Index 1982-1984=100 not seasonal
                           'CUSR0000SEFX': '',  # Alcoholic Beverages Away from Home Index 1982-1984=100 not seasonal

                           # TOBACCO INDEX
                           'CUSR0000SEGA': '',  # Tobacco and Smoking Products Index 1982-1984=100 not seasonal

                           # VEHICLES INDEX
                           'CUSR0000SETA02': '',  # Used Cars and Trucks Index 1982-1984=100 not seasonal
                           'CUUR0000SETA01': '',    # New Vehicles Index 1982-1984=100 not seasonal
                           'CUUR0000SETC': '',  # Motor Vehicle Parts and Equipment Index 1982-1984=100 not seasonal
                           'CUUR0000SETD': '',  # Motor Vehicle Maintenance and Repair Index 1982-1984=100 not seasonal
                           'CUUR0000SETA': '',  # New and Used Motor Vehicles Index Dec 1997=100 not seasonal

                           # TOYS INDEX
                           'CUUR0000SERE01': '',    # Toys Index 1982-1984=100

                           # ORGANIZATIONS INDEX
                           'CUUR0000SERF01': '',    # Club Membership for Shopping Clubs, Fraternal, or Other Organizations, or Participant Sports Fees Index Dec 1997=100

                           # MUSIC INSTRUMENTS INDEX
                           'CUUR0000SERE03': '',  # Music Instruments and Accessories Index Dec 1997=100 not seasonal

                           # ELECTRONIC PRODUCTS INDEX
                           'CUUR0000SERAC': '',  # Video and Audio Products Index Dec 2009=100 not seasonal
                           'CUUR0000SEEE01': '',    # Computers, Peripherals, and Smart Home Assistants Index Dec 2007=100


                           }

    extractor = FredDataExtractor('a7eca89fdf2905baea21d67b942c9ef7')
    extractor.data_updater(fred_ns_series_dict)


if __name__ == '__main__':
    main()