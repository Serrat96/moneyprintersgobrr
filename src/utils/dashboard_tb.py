import streamlit as st
import pandas as pd
from datetime import timedelta
import sqlite3

import sys, os

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep

current_folder = dirname(abspath(__file__))
for i in range(1): current_folder = dirname(abspath(current_folder))
sys.path.append(current_folder)

# Self-made packages
import utils.mining_data_tb as md
import utils.visualization_tb as vi

# Objects
plotter = vi.st_plotter
processor = md.processor

##################################################### FUNCTIONS #####################################################
#####
def double_ended_slider(df_dict, slider_title: str, key: str):

    concated_df = pd.concat(df_dict["dfs"], axis=1)

    concated_df=concated_df.dropna()

    try:
        format = 'MMM/YYYY'
        start_date = concated_df.index[0].date()
        end_date = concated_df.index[-1].date()
        start_date, end_date = st.sidebar.slider(slider_title, value=[start_date, end_date], format=format, key=key)
    except:
        start = concated_df.index[0].date()
        end = concated_df.index[-1].date()
        start_date, end_date = st.sidebar.date_input(slider_title, value=[start, end], key=key)

    return start_date, end_date

class front:
    @staticmethod
    def main_plots(plots_specs, start_date, end_date, cols, key):
        ######### DATA PREP #########
        right_plot, left_plot, specifics = plots_specs["left_plot"], plots_specs["right_plot"], plots_specs["specifics"]
        #target, independent = right_plot["dfs"]

        ######### LEFT PLOT #########
        with cols[0]:
            st.plotly_chart(
                    plotter.line_plotter(right_plot,
                                        start_date,
                                        end_date,
                                        palette = specifics["palette"],
                                        note = specifics["note"][0],
                                        x_annot = specifics["x_annot"][0],
                                        y_annot = specifics["y_annot"][0],
                                        x_legend = specifics["x_legend"][0],
                                        y_legend = specifics["y_legend"][0],
                                        title = specifics["title"][0],
                                        tickformat = specifics["tickformat"][0]),
                    use_container_width = True)

        ######### RIGHT PLOT #########
        with cols[1]:
            st.plotly_chart(
                    plotter.line_plotter(left_plot,
                                        start_date,
                                        end_date,
                                        palette = specifics["palette"],
                                        note = specifics["note"][1],
                                        x_annot = specifics["x_annot"][1],
                                        y_annot = specifics["y_annot"][1],
                                        x_legend = specifics["x_legend"][1],
                                        y_legend = specifics["y_legend"][1],
                                        title = specifics["title"][1],
                                        tickformat = specifics["tickformat"][1]),
                    use_container_width = True)

    @staticmethod
    def main_metrics(data, start_date, end_date, cols, quarterly = True, multiplier = 100, currency_name = ''): 
        absolute_data, percentage_data = data["left_plot"]["dfs"], data["right_plot"]["dfs"]
        names = data["left_plot"]["legends"]
        

        for ind in range(len(absolute_data)):
            with cols[0]:
                independent_absolute_current, independent_absolute_delta = processor.calculate_metrics(absolute_data[ind],
                start_date,
                end_date,
                quarterly = quarterly,
                currency_name = currency_name)

                # Plot
                st.metric(f'{names[ind]} value at ' + str(end_date), value = independent_absolute_current, delta = independent_absolute_delta)

            with cols[1]:
                independent_percentage_current, independent_percentage_delta = processor.calculate_metrics(percentage_data[ind],
                            start_date,
                            end_date,
                            multiplier = multiplier,
                            currency_name = '',
                            symbol = '%',
                            quarterly = False,
                            precision = 4)
                # Data extraction
                st.metric(f'{names[ind]} change at ' + str(end_date), value = str(round(float(independent_percentage_current), 2)) + '%')

            with cols[2]:
                value, delay = processor.get_best_quarterly_correlation(absolute_data[ind], absolute_data[ind], start_date, end_date)

                value_past_year, delay_past_year = processor.get_best_quarterly_correlation(absolute_data[ind], absolute_data[ind], start_date, end_date - timedelta(days=365))

                # Plot
                st.metric(f'{names[ind]} affects CPI within:', value = str(delay) + ' months',
                            delta = str(delay - delay_past_year) + ' months regard anterior year')

            with cols[3]:
                st.metric('With a correlation of:', value = str(round(value * 100, 1)) + ' %')