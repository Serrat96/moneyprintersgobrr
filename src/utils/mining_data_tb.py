import numpy as np
import pandas as pd
import sqlite3
import json

from datetime import *
from fredapi import Fred

from millify import millify

from sklearn.model_selection import train_test_split

import sys, os

from sqlalchemy import create_engine

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep

# Self-made packages
import utils.folder_tb as fo

# Database connection
database_path = fo.path_to_folder(2, "data") + "moneyprintersgobrr.db"
#connection = sqlite3.connect(database_path)
engine = create_engine("mariadb+mariadbconnector://administrador:Xit7WdQ3YniY6YttHzBu@moneyprintersgobrr.c8r7otayptqb.eu-west-3.rds.amazonaws.com:3306/moneyprintersgobrr")


##################################################### FUNCTIONS #####################################################
#####
class extractor:
    def __init__(self, api_key):
        self.api_key = api_key

    #####
    def get_fred_data(self, series: str):
        fred = Fred(api_key=self.api_key)
        series = fred.get_series(series)
        series = pd.DataFrame(series, columns=['Value'])
        return series

    #####
    def filter_from_date(self, df, from_date, date_format='%Y-%m-%d'):
        mask = (df.index >= datetime.strptime(from_date, date_format))

        filtered_df = df.loc[mask]

        return filtered_df

    #####
    def get_and_filter(self, series: list, from_date, date_format='%Y-%m-%d'):
        data = {}

        for serie in series:
            s = self.get_fred_data(serie)
            filtered_s = self.filter_from_date(s, from_date)
            data[str(serie)] = filtered_s

        return data


#####
class processor:
    @staticmethod
    def merger(y, X, column_names):
        # Merge y with the first X
        df = pd.merge(y, X[0], how="outer", left_index=True, right_index=True)

        # Then try to iterate over the rest of the Xs
        # The try/except is in case we only have 1 X, then it will go on to return the df
        try:
            for data in X[1:]:
                df = pd.merge(df, data, how="outer", left_index=True, right_index=True)
        except:
            pass

        df.columns = column_names
        return df

    @staticmethod
    def time_shifter(df, target_variable, n_periods):
        # Empty list to save all the values per column
        new_columns = []
        #  Get the target variable first and add it to the list
        target = list(df.loc[:, target_variable].values[n_periods:])
        new_columns.append(target)

        #  Get Xs from the data
        xs = df.drop(target_variable, axis=1)
        #  Iterate over all Xs and append the shifted data to the list
        for column in xs.columns:
            new_columns.append(list(df.loc[:, column].values[:-n_periods]))

        #  Transform the list into a (transposed) dataframe
        new_df = pd.DataFrame(new_columns).T
        # Rename columns
        new_df.columns = df.columns
        return new_df

    @staticmethod
    def data_prep(df, target_variable, scaler=None, test_size=.2, seed=42):
        X = df.drop(target_variable, axis=1)
        y = df.loc[:, target_variable]

        X = np.array(X)
        y = np.array(y).reshape(-1, 1)

        if scaler:
            X = scaler.fit_transform(X)

        return train_test_split(X, y, random_state=seed)

    @staticmethod
    def filter_between_dates(df, from_date, to_date, date_format='%Y-%m-%d'):

        mask = (df.index >= datetime.strptime(from_date, date_format)) & \
               (df.index <= datetime.strptime(to_date, date_format))

        filtered_df = df.loc[mask]

        return filtered_df

    @staticmethod
    def two_variables_correlation(df1, df2, start_date, end_date, percentage=True, n_periods=0):
        start_date_str = str(start_date)
        end_date_str = str(end_date)

        df1_filtered = processor.filter_between_dates(df1, start_date_str, end_date_str)
        df2_filtered = processor.filter_between_dates(df2, start_date_str, end_date_str)

        df = pd.concat([df1_filtered, df2_filtered], axis=1)

        if percentage:
            df2_shifted = df2_filtered.pct_change(12).shift(-n_periods)
            df1_pct = df1_filtered.pct_change(12)
            df = pd.concat([df1_pct, df2_shifted], axis=1).dropna()

        corr_df = df.corr()

        return corr_df.iloc[0, 1]

    @staticmethod
    def get_best_correlation(df1, df2, start_date, end_date, percentage=True, periods_range=range(0, 120)):
        correlations_list = []

        for n_period in periods_range:
            corr = processor.two_variables_correlation(df1, df2, start_date, end_date, percentage=percentage,
                                                       n_periods=n_period)

            correlations_list.append(corr)

        maxim = abs(max(correlations_list))

        minim = abs(min(correlations_list))

        if maxim > minim:
            return max(correlations_list), correlations_list.index(max(correlations_list)) + 1
        else:
            return min(correlations_list), correlations_list.index(min(correlations_list)) + 1

    @staticmethod
    def get_best_quarterly_correlation(df1, df2, start_date, end_date, percentage=True, periods_range=range(0, 120)):
        df2_q = df2.asfreq('QS')
        correlations_list = []

        for n_period in periods_range:
            corr = processor.two_variables_correlation(df1, df2_q, start_date, end_date, percentage=percentage,
                                                       n_periods=n_period)

            correlations_list.append(corr)

        maxim = abs(max(correlations_list))

        minim = abs(min(correlations_list))

        if maxim > minim:
            return max(correlations_list), correlations_list.index(max(correlations_list)) + 1
        else:
            return min(correlations_list), correlations_list.index(min(correlations_list)) + 1


    @staticmethod
    def calculate_metrics(df, start_date, end_date, precision=2, currency_name='$', symbol='', multiplier=1, quarterly=False):
        start_date_str = str(start_date)
        end_date_str = str(end_date)
        df_filtered = processor.filter_between_dates(df, start_date_str, end_date_str)

        current_value = str(millify(df_filtered.iloc[-1] * multiplier, precision=precision)) + currency_name
        if quarterly:
            delta_value = str(millify((df_filtered.iloc[-1] * multiplier) - df_filtered.iloc[-5] * multiplier,
                                  precision=precision)) + currency_name + symbol + ' regard anterior year'
        else:
            delta_value = str(millify((df_filtered.iloc[-1] * multiplier) - df_filtered.iloc[-13] * multiplier,
                                      precision=precision)) + currency_name + symbol + ' regard anterior year'

        return current_value, delta_value

##### TO CHECK
def read_data_(path: str):
    try:
        return pd.read_parquet(path)
    except:
        print(path)
        initial_path = r'/app/moneyprintersgobrr/'
        path_2 = path[3:]
        return pd.read_parquet(initial_path + path_2)

# To query database
# def get_data(x, country):
#     query = f'''
#     SELECT date, {x}
#     FROM {country}
#     '''

#     result = pd.read_sql_query(query, connection).dropna()
#     result.date = pd.to_datetime(result.date)
#     return result.set_index("date")

def get_data(x, country):
    query = f'''
    SELECT date, {x}
    FROM {country}
    '''

    result = pd.read_sql_query(query, engine).dropna()
    result.date = pd.to_datetime(result.date)
    return result.set_index("date")


##################################################### SUPPORT #####################################################
def read_json(fullpath):
    '''
    This function reads the json an returns it in a format we can work with it

    args : fullpath -> path to the json to be read
    '''
    with open(fullpath, "r") as json_file:
        read_json_ = json.load(json_file)

    return read_json_

#########
def read_json_to_dict(json_fullpath):
    """
    Read a json and return a object created from it.
    Args:
        json_fullpath: json fullpath

    Returns: json object.
    """
    try:
        with open(json_fullpath, 'r+') as outfile:
            read_json = json.load(outfile)
        return read_json
    except Exception as error:
        raise ValueError(error)