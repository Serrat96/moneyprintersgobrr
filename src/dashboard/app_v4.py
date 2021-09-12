import streamlit as st

from datetime import timedelta
import mariadb
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

##################################################### PREPARATION #####################################################
st.set_page_config(page_title='moneyprintersgobrr', page_icon='dollar', layout='wide',
                   initial_sidebar_state='collapsed')

# Objects
plotter = vi.st_plotter
processor = md.processor
front = da.front

##################################################### INTERFACE #####################################################

def main():
    menu = "US"

    if menu == "US":
        st.title(f"Inflation metrics for {menu} :flag-{menu.lower()}:")

        # Generic information and parameters
        country = "USA"
        target = "cpi"
        independent_vars = [["gdp"], ["m1", "m2"], ["ipi"], ["m1v", "m2v"]]
        tables = [["NA000334Q"], ["M1NS", "M2NS"], ["USSTHPI"], ["M1V", "M2V"]]
        secondary_ys = [[True], [True, True], [True], [True, True]]
        temp_change = [4, 12, 12, 4]
        key = 0


        for ind1, vars_ in enumerate(independent_vars):
            # Loading data
            target_data = [md.get_data("CPIAUCNS", country)]
            target_data_percentage = [target_data[0].pct_change(12).dropna()]
            independent_data = [md.get_data(tables[ind1][ind2], country) for ind2, var in enumerate(vars_)]
            independent_data_percentage = [data.pct_change(temp_change[ind1]).dropna() for data in independent_data]

            l_dfs = target_data + independent_data
            r_dfs = target_data_percentage + independent_data_percentage
            legends = [target.upper()] + [var.upper() for var in vars_]
            slider_title = f"{target.upper()} vs " + "".join([f"{var.upper()}, " for var in vars_])
            title1 = f"{target.upper()} vs " + "".join([f"{var.upper()}, " for var in vars_])
            title2 = f"{target.upper()} vs " + "".join([f"{var.upper()}, " for var in vars_]) + " annual change"    

            # Plot specs
            plots_specs = {
                # Data and main plot characteristics
                "left_plot" : {
                        "dfs" : l_dfs,
                        "legends" : legends,
                        "secondary_ys" : [False] + secondary_ys[ind1],
                        "names" : legends},
                "right_plot" : {
                        "dfs" : r_dfs,
                        "legends" : legends,
                        "secondary_ys" : [False] + secondary_ys[ind1],
                        "names" : legends},
                # Plot specs
                "specifics" : {
                    # General specs
                    "slider_title" : slider_title,
                    "palette" : ['#F63366', '#48A9A6', '#66D7D1'],
                    "x_annot" : [1, 0],
                    "y_annot" : [-.12, 0],
                    # Plot specs [left, right]
                    "note" : ["CPI: Index 1982-1984=100", ""],
                    "x_legend" : [1, .1],
                    "y_legend" : [-.12, 1],
                    "title" : [title1, title2],
                    "tickformat" : ["", ".2%"],
                }
            }
            
            # Left bar slider
            start_date, end_date = da.double_ended_slider(plots_specs["left_plot"], plots_specs["specifics"]["slider_title"], key)
            ###### PLOTS ######
            cols = st.columns(2)
            front.main_plots(plots_specs, start_date, end_date, cols, key)
            key += 1

            ###### METRICS ######
            cols = st.columns(4)
            front.main_metrics(plots_specs, start_date, end_date, cols)


##################################################### EXECUTION #####################################################
if __name__ == "__main__":
    main()