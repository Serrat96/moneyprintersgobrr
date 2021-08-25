import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime

import sys, os

import utils.mining_data_tb as md

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep
models_path = '..' + sep + 'models' + sep

# Path modification
current_folder = dirname(abspath(__file__))
for i in range(1): current_folder = dirname(abspath(current_folder))
sys.path.append(current_folder)

class AutomaticLinearRegression():
    def __init__(self, name: str, regressor_variables: list, target_variable: pd.Series):
        self.name = name
        self.regressor_variables = regressor_variables
        self.target_variable = target_variable

    def linear_regression(self, start_date, end_date, train_size=0.8, random_state=None, shuffle=False, save_model=False,
                          standarize=False):
        str_start_date = str(start_date)
        str_end_date = str(end_date)
        if len(self.regressor_variables) > 1:
            regressor_variables_df = pd.DataFrame()
            for df in self.regressor_variables:
                df = md.processor.filter_between_dates(df, str_start_date, str_end_date)
                regressor_variables_df = pd.concat([regressor_variables_df, df], axis=1)
                regression_df = pd.concat([regressor_variables_df, df], axis=1)
            filter_df = pd.concat([regressor_variables_df, self.target_variable], axis=1).dropna()
            regressor_variables_df = filter_df.iloc[:,0:-1]
            self.target_variable = filter_df.iloc[:,-1]
        else:
            regressor_variables_df = md.processor.filter_between_dates(self.regressor_variables[0], str_start_date,
                                                                       str_end_date)
            filter_df = pd.concat([regressor_variables_df, self.target_variable], axis=1).dropna()
            regressor_variables_df = filter_df.iloc[:, 0:-1]
            self.target_variable = filter_df.iloc[:, -1]
            regressor_variables_df = regressor_variables_df.values.reshape(-1, 1)



        self.target_variable = md.processor.filter_between_dates(self.target_variable, str_start_date, str_end_date)
        self.target_variable.reset_index(drop=True, inplace=True)


        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(regressor_variables_df,
                                                            self.target_variable.values.reshape(-1, 1),
                                                            train_size=train_size,
                                                            shuffle=shuffle,
                                                            random_state=random_state,
                                                            )

        if standarize:
            std_scale = StandardScaler()
            std_scale.fit(X_train)

            X_train = std_scale.transform(X_train)
            X_test = std_scale.transform(X_test)

        # Train
        model = LinearRegression()
        model.fit(X_train, y_train)
        intercept = model.intercept_
        if len(self.regressor_variables) > 1:
            coefficients = list(zip(regressor_variables_df.columns, model.coef_.flatten()))
        else:
            coefficients = model.coef_.flatten()
        score = model.score(regressor_variables_df, self.target_variable)

        # Predict
        predictions = model.predict(X=X_test)

        rmse = mean_squared_error(y_true=y_test,
                                  y_pred=predictions,
                                  squared=False
                                  )

        mse = mean_squared_error(y_true=y_test,
                                  y_pred=predictions,
                                  squared=True
                                  )

        model_metrics_dict = {'intercept': intercept,
                              'coefficients': coefficients,
                              'score': score,
                              'rmse': rmse,
                              'mse': mse
        }

        if save_model:
            now = str(datetime.now())
            now = now.split('.')[0]
            now = now.replace(':', '.')
            now = now.replace(' ', '_')
            joblib.dump(model, models_path + self.name + now + "linear_regression_model.pkl")

        return model_metrics_dict
