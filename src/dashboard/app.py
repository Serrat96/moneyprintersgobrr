import streamlit as st
from datetime import timedelta
import pandas as pd
from millify import millify

import sys, os

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep

# Path modification
current_folder = dirname(abspath(__file__))
for i in range(1): current_folder = dirname(abspath(current_folder))
sys.path.append(current_folder)

# Self-made packages
import utils.constants_tb as ct
import utils.dashboard_tb as da
import utils.mining_data_tb as md
import utils.visualization_tb as vi
import utils.folder_tb as fo


##################################################### PREPARATION #####################################################
st.set_page_config(page_title='moneyprintersgobrr', page_icon='dollar', layout='wide',
                   initial_sidebar_state='collapsed')

@st.cache
def get_data():
    data_path = fo.path_to_folder(2, "data")

    # Raw data
    m1_usa = md.read_data(data_path + "M1" + sep +"m1_usa.parquet")
    m2_usa = md.read_data(data_path + "M2" + sep +"m2.parquet")
    cpi_usa = md.read_data(data_path + "CPI" + sep +"cpi.parquet")
    pce_usa = md.read_data(data_path + "PCE" + sep +"pce_adjusted.parquet")
    
    # Transformed data
    m2_usa_percentage = m2_usa.pct_change(12).dropna()
    cpi_usa_percentage = cpi_usa.pct_change(12).dropna()

    return m1_usa, m2_usa, cpi_usa, pce_usa, m2_usa_percentage, cpi_usa_percentage

m1_usa, m2_usa, cpi_usa, pce_usa, m2_usa_percentage, cpi_usa_percentage = get_data()

# Objects
plotter = vi.st_plotter
processor = md.processor

##################################################### INTERFACE #####################################################

def main():
    menu = st.sidebar.selectbox('Country', ct.countries_list)

    # UNITED STATES, US
    if menu == 'US':
        st.markdown('# Inflation metrics for USA :flag-us:')
        col1, col2 = st.columns(2)

        ################# PLOTS #################
        #### LEFT COL
        with col1:
            start_date_col1, end_date_col1 = da.double_ended_slider(m2_usa, 'Monetary aggregates & CPI', key='1')

            to_plot = {
                "dfs" : [cpi_usa, pce_usa, m1_usa, m2_usa],
                "legends" : ["CPI", "PCE", "M1", "M2"],
                "secondary_ys" : [False, False, True, True],
                "names" : ["CPI & PCE", "MONETARY AGGREGATES"]
            }

            
            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date = start_date_col1, end_date = end_date_col1, title = "Monetary aggregates & CPI")
                , use_container_width=True)
            
        #### RIGHT COL
        with col2:
            start_date_col2, end_date_col2 = da.double_ended_slider(m2_usa, 'M2 & CPI annual change', key='2')

            to_plot = {
                "dfs" : [m2_usa_percentage, cpi_usa_percentage],
                "legends" : ["M2", "CPI"],
                "secondary_ys" : [False, True],
                "names" : ["M2", "CPI"]
            }

            
            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date = start_date_col2, end_date = end_date_col2, title = "M2 & CPI anual change", tickformat = "%")
                , use_container_width=True)


        ################# METRICS #################
        col_1, col_2, col_3, col_4 = st.columns(4)

        #### LEFT COL
        with col_1:
            # Data extraction
            m2_current_value, m2_delta_value = processor.calculate_metrics(m2_usa, start_date_col1, end_date_col1)
            m1_current_value, m1_delta_value = processor.calculate_metrics(m1_usa, start_date_col1, end_date_col1)
            
            # Plot
            st.metric('M2 nominal value', value=m2_current_value, delta=m2_delta_value, delta_color='inverse')
            st.metric('M1 nominal value', value=m1_current_value, delta=m1_delta_value, delta_color='inverse')

        with col_2:
            # Data extraction
            cpi_current_value, cpi_delta_value = processor.calculate_metrics(cpi_usa, start_date_col1, end_date_col1)
            pce_current_value, pce_delta_value = processor.calculate_metrics(pce_usa, start_date_col1, end_date_col1)
            
            # Plot
            st.metric('CPI nominal value', value=cpi_current_value, delta=cpi_delta_value, delta_color='inverse')
            st.metric('PCE nominal value', value=pce_current_value, delta=pce_delta_value, delta_color='inverse')


        #### RIGHT COL
        with col_3:
            # Data extraction
            value, delay = processor.get_best_correlation(m2_usa, cpi_usa, start_date_col2, end_date_col2)
            value_past_year, delay_past_year = processor.get_best_correlation(m2_usa, cpi_usa, start_date_col2, end_date_col2-timedelta(days=365))

            # Plot
            st.metric('Changes in M2 affect CPI within:', value=str(delay) + ' months', delta=str(delay-delay_past_year) + ' months regard anterior year')

        with col_4:
            st.metric('With a correlation of:', value=str(round(value*100, 1)) + ' %', delta=str(round((value-value_past_year)*100, 2)) + '% regard anterior year')


        ################# ANNOTATIONS #################
        col_1, col_2 = st.columns(2)

        with col_1.expander(label='What is being calculated here?'):
            st.write('Just a normal correlation of M2 and CPI nominal values for the selected period in the side menu slidebar')

        with col_2.expander(label='What is being calculated here?'):
            st.write('Basically, how long does it take for a variation of M2 to affect the CPI for the selected period in the side menu slidebar')
        with col_2.expander(label='How it is calculated?'):
            st.write('First of all two DataFrame with nominal values is constructed (concatenated for space reasons):')
            st.write(pd.concat([m2_usa.rename(columns={'Value': 'M2 nominal values'}), cpi_usa.rename(columns={'Value': 'CPI nominal values'})], axis=1))
            st.write('Then, we calculate the annual variation percentages:')
            st.write(pd.concat([m2_usa_percentage.rename(columns={'Value': 'M2 annual % variation'})*100, cpi_usa_percentage.rename(columns={'Value': 'CPI annual % variation'})*100], axis=1))
            st.write('Then, CPI variation is shifted in a for loop and calculate correlation for each iteration in a code '
                     'like this, where highest value is extracted with his index in order to know the months that we shifted to get that value:')
            code = '''def get_best_correlation(m2_annual_variation_df, cpi_annual_variation_df, start_date, end_date):
    list_correlations = []
    for i in range(0, 120):
        start_date_str = str(start_date)
        end_date_str = str(end_date)

        m2_annual_variation_df_filtered = filter_between_dates(m2_annual_variation_df, start_date_str, end_date_str)
        cpi_annual_variation_df_filtered = filter_between_dates(cpi_annual_variation_df, start_date_str, end_date_str)

        cpi_annual_variation_df_shifted = cpi_annual_variation_df_filtered.pct_change(12).shift(-i)
        m2_annual_variation_df_pct = m2_annual_variation_df_filtered.pct_change(12)

        df = pd.concat([m2_annual_variation_df_pct, cpi_annual_variation_df_shifted], axis=1).dropna()

        df_corr = df.corr()

        list_correlations.append(df_corr.iloc[1, 0])

    return max(list_correlations), list_correlations.index(max(list_correlations)) + 1'''
            st.code(code, language='python')

if __name__ == '__main__':
    main()