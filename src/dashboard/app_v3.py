import streamlit as st
from datetime import timedelta
import sqlite3
import pandas as pd

import sys, os

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep

# Path modification
current_folder = dirname(abspath(__file__))
for i in range(1): current_folder = dirname(abspath(current_folder))
sys.path.append(current_folder)

# Self-made packages
import utils.constants_tb as ct
import utils.dashboard_tb as da
import utils.mining_data_tb as md
import utils.visualization_tb as vi
import utils.folder_tb as fo
import utils.models_tb as mo

##################################################### PREPARATION #####################################################
st.set_page_config(page_title='moneyprintersgobrr', page_icon='dollar', layout='wide',
                   initial_sidebar_state='collapsed')

# Database path
# database_path = fo.path_to_folder(2, "data") + "moneyprintersgobrr.db"
# connection = sqlite3.connect(database_path)

# Objects
plotter = vi.st_plotter
processor = md.processor


##################################################### INTERFACE #####################################################

def main():
    ##### MENU
    menu = 'US' #st.sidebar.selectbox('Country', ct.countries_list)

    if menu == 'US':
        st.title('Inflation metrics for USA :flag-us:')
        cols = st.columns(2)

        ############################## GDP ##############################
        ############### PLOTS ###############
        cpi_usa = md.get_data("CPIAUCNS", "usa")
        gdp_usa = md.get_data("NA000334Q", "usa")

        cpi_usa_percentage = cpi_usa.pct_change(12).dropna()
        gdp_usa_percentage = gdp_usa.pct_change(4).dropna()

        # Level 0
        cols_filler = {
            #### LEFT
            # Level 1
            0 : {
                # Level 2
                "title" : "CPI & GDP",        # Add this to to_plot dict -> update double_ended function
                # Level 3
                "to_plot" : {"dfs": [cpi_usa, gdp_usa],
                           "legends": ["CPI", "GDP"],
                           "secondary_ys": [False, True],
                           "names": ["CPI", "GDP"]},
                "note" : "CPI: Index 1982-1984=100",
                # Level 3
                "plot_params" : {
                    "x_annot" : 1,
                    "y_annot" : -0.12,
                    "x_legend" : 0,
                    "y_legend" : 0
                },
            },

            #### RIGHT
            1 : {
                # Level 2
                "title" : "Test",        # Add this to to_plot dict -> update double_ended function
                # Level 3
                "to_plot" : {"dfs": [cpi_usa, gdp_usa],
                           "legends": ["CPI", "GDP"],
                           "secondary_ys": [False, True],
                           "names": ["CPI", "GDP"]},
                "note" : "CPI: Index 1982-1984=100",
                # Level 3
                "plot_params" : {
                    "x_annot" : 1,
                    "y_annot" : -0.12,
                    "x_legend" : 0,
                    "y_legend" : 0
                }
            }
        }


        key = 0
        palette = ['#F63366', '#48A9A6', '#66D7D1']
        use_container_width = True
        start_date_col, end_date_col = da.double_ended_slider(cols_filler[0]["to_plot"], cols_filler[0]["title"], key = key)

        for ind, col in enumerate(cols):
            with col:
                st.plotly_chart(
                    plotter.line_plotter(
                        cols_filler[ind]["to_plot"],
                        start_date = start_date_col, end_date = end_date_col,
                        palette = palette,
                        note = cols_filler[ind]["note"],
                        x_annot = cols_filler[ind]["plot_params"]["x_annot"],
                        y_annot = cols_filler[ind]["plot_params"]["y_annot"],
                        # x_legend = cols_filler[ind]["plot_params"]["x_legend"],
                        # y_legend = cols_filler[ind]["plot_params"]["y_legend"],
                        title = cols_filler[ind]["title"]),
                    use_container_width = use_container_width)

                key += 1


    ############### METRICS ###############
    cols = st.columns(4)
    cols_filler = {
                0 : {"title" : "GDP value at ",
                    "calculate_metrics" : {
                            "df" : gdp_usa,
                            "start_date" : start_date_col,
                            "end_date" : end_date_col,
                            "precision" : 2,
                            "currency_name" : '$',
                            "symbol" : '',
                            "multiplier" : 1,
                            "quarterly" : False},
                    },

                1 : {"title" : "Test",
                    "calculate_metrics" : {
                            "df" : gdp_usa_percentage,
                            "start_date" : start_date_col,
                            "end_date" : end_date_col,
                            "precision" : 4,
                            "currency_name" : '%',
                            "symbol" : '',
                            "multiplier" : 100,
                            "quarterly" : True},
                    }
                }

    

    for ind, col in enumerate(cols):
        if ind < 2:
            with col:
                current, delta = processor.calculate_metrics(
                    cols_filler[ind]["calculate_metrics"]["df"],
                    cols_filler[ind]["calculate_metrics"]["start_date"],
                    cols_filler[ind]["calculate_metrics"]["end_date"],
                    multiplier = cols_filler[ind]["calculate_metrics"]["multiplier"],
                    currency_name = cols_filler[ind]["calculate_metrics"]["currency_name"],
                    symbol = cols_filler[ind]["calculate_metrics"]["symbol"],
                    quarterly = cols_filler[ind]["calculate_metrics"]["quarterly"],
                    precision = cols_filler[ind]["calculate_metrics"]["precision"])

                st.metric(cols_filler[ind]["title"] + str(cols_filler[ind]["calculate_metrics"]["end_date"]), value = current, delta = delta)
        
        if ind == 2:
            value, delay = processor.get_best_quarterly_correlation(
                        cols_filler[0]["calculate_metrics"]["df"],
                        cpi_usa,
                        cols_filler[0]["calculate_metrics"]["start_date"],
                        cols_filler[0]["calculate_metrics"]["end_date"])
            with col:
                st.metric('GDP affects CPI within:', value=str(delay) + ' months')
   
        if ind == 3:
            with col:
                st.metric('With a correlation of:', value = str(round(value * 100, 1)) + ' %')

        

if __name__ == '__main__':
    main()
