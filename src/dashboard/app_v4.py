# Lanzar streamlit desde  C:\Users\serra\REPOSITORIOS\moneyprintersgobrr\src\dashboard
import streamlit as st
import time

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

##################################################### PREPARATION #####################################################
st.set_page_config(page_title='moneyprintersgobrr', page_icon='dollar', layout='wide',
                   initial_sidebar_state='expanded')

# Objects
plotter = vi.st_plotter
processor = md.processor
front = da.front


##################################################### INTERFACE #####################################################


def main():

    menu = st.sidebar.selectbox('Country', ct.countries_list, index = ct.countries_list.index("US"))

    st.title(f"Inflation metrics for {menu} :flag-{menu.lower()}:")

    # Load country settings
    json_path = '..' + sep + 'utils' + sep + "country_data.json"
    country_data = md.read_json_to_dict(json_path)[menu]
    ####### DATA EXTRACTION AND PROCESSING #######
    country = country_data["country"]
    target = country_data["target"]
    # UPDATE PER COUNTRY
    target_db_name = country_data["target_db_name"]
    # List of lists
    # Example: CPI vs M1 & M2 -> [[m1, m2]]
    independent_vars = country_data["independent_vars"]
    names = country_data["names"]
    tables = country_data["tables"]
    # Temporal lag
    temp_change = country_data["temp_change"]
    ####### PLOT FEATURES #######
    note = country_data["note"]
    x_annot = country_data["x_annot"]
    y_annot = country_data["y_annot"]
    x_legend = country_data["x_legend"]
    y_legend = country_data["y_legend"]
    # y-axis on the right
    secondary_ys = country_data["secondary_ys"]
    # Titles
    titles = country_data["titles"]
    titles_change = [title + " annual change" for title in titles]
    key = 0
    num = 0
    for ind1, vars_ in enumerate(independent_vars):
        ############ Loading data ############
        target_data = [md.get_data(target_db_name, country)]
        target_data_percentage = [target_data[0].pct_change(12).dropna()]   # Temporal lag
        independent_data = [md.get_data(tables[ind1][ind2], country) for ind2, var in enumerate(vars_)] # List of dfs
        independent_data_percentage = [data.pct_change(temp_change[ind1]).dropna() for data in independent_data]

        ############ Preprocessing ############
        l_dfs = target_data + independent_data  # All variables list
        r_dfs = target_data_percentage + independent_data_percentage
        legends = [target.upper()] + [var.upper() for var in vars_]
        name = [target.upper()] + [name for name in names[num]]
        num+=1
        slider_title = f"{target.upper()} vs " + "".join([f"{var.upper()}, " for var in vars_])
        # title1 = f"{target.upper()} vs " + "".join([f"{var.upper()}, " for var in vars_])
        # title2 = f"{target.upper()} vs " + "".join([f"{var.upper()}, " for var in vars_]) + " annual change"    

        # Plot specs
        plots_specs = {
            # Data and main plot characteristics
            "left_plot" : {
                    "dfs" : l_dfs,
                    "legends" : legends,
                    "secondary_ys" : [False] + secondary_ys[ind1],
                    "names" : name},
            "right_plot" : {
                    "dfs" : r_dfs,
                    "legends" : legends,
                    "secondary_ys" : [False] + secondary_ys[ind1],
                    "names" : name},
            # Plot specs
            "specifics" : {
                # General specs
                "slider_title" : slider_title,
                "palette" : ['#F63366', '#48A9A6', '#66D7D1'],
                "x_annot" : x_annot,
                "y_annot" : y_annot,
                # Plot specs [left, right]
                "note" : note,
                "x_legend" : x_legend,
                "y_legend" : y_legend,
                "title" : [titles[ind1], titles_change[ind1]],
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
        cols2 = st.columns(4)
        if ind1 == 0:
            front.main_metrics(plots_specs, start_date, end_date, cols2)
        else:
            plots_specs["left_plot"]["dfs"], plots_specs["right_plot"]["dfs"], plots_specs["left_plot"]["legends"] = plots_specs["left_plot"]["dfs"][1:], plots_specs["right_plot"]["dfs"][1:], plots_specs["left_plot"]["legends"][1:]
            front.main_metrics(plots_specs, start_date, end_date, cols2)



##################################################### EXECUTION #####################################################
if __name__ == "__main__":
    main()