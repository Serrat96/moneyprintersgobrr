import streamlit as st
import os
from datetime import timedelta
import pandas as pd
from millify import millify

try:
    os.chdir(r'C:\Users\serra\REPOSITORIOS\moneyprintersgobrr\04-Webpage')
except:
    try:
        os.chdir(r'/home/josest/Documents/GitHub/moneyprintersgobrr/04-Webpage')
    except:
        try:
            os.chdir(r'/Users/joseserrat/Documents/GitHub/moneyprintersgobrr/04-Webpage')
        except:
            pass

import functions as ft
import constants as ct

st.set_page_config(page_title='moneyprintersgobrr', page_icon='dollar', layout='wide',
                   initial_sidebar_state='collapsed')

# READ DATA
# USA

m1_usa = ft.read_data(r'../02-Data/M1/m1_usa.parquet')
m2_usa = ft.read_data(r'../02-Data/M2/m2.parquet')
cpi_usa = ft.read_data(r'../02-Data/CPI/cpi.parquet')
pce_usa = ft.read_data(r'../02-Data/PCE/pce_adjusted.parquet')

# DATA TRANSFORMATIONS
m2_usa_percentage = m2_usa.pct_change(12).dropna()
cpi_usa_percentage = cpi_usa.pct_change(12).dropna()


def main():
    menu = st.sidebar.selectbox('Country', ct.countries_list)

    # UNITED STATES, US
    if menu == 'US':
        st.markdown('# Inflation metrics for USA :flag-us:')
        col1, col2 = st.columns(2)
        with col1:
            start_date_col1, end_date_col1 = ft.double_ended_slider(m2_usa, 'Monetary aggregates & CPI', key='1')
            st.plotly_chart(
                ft.four_plots(cpi_usa, pce_usa, m1_usa, m2_usa, start_date_col1, end_date_col1,
                              legend_graph_one='CPI', secondary_y_df1=True,
                              legend_graph_two='PCE', secondary_y_df2=True,
                              legend_graph_three='M1', secondary_y_df3=False,
                              legend_graph_four='M2', secondary_y_df4=False,
                              principal_title='Monetary aggregates & CPI',
                              name_graph_one='MONETARY AGGREGATES',
                              name_graph_two='CPI & PCE', tickformat=''), use_container_width=True)

        with col2:
            start_date_col2, end_date_col2 = ft.double_ended_slider(m2_usa, 'M2 & CPI annual change', key='2')
            st.plotly_chart(
                ft.two_plots(m2_usa_percentage, cpi_usa_percentage, start_date=start_date_col2, end_date=end_date_col2,
                             legend_graph_one='M2',
                             legend_graph_two='CPI', principal_title='M2 & CPI anual change', name_graph_one='M2',
                             name_graph_two='CPI'), use_container_width=True)

        col_1, col_2, col_3, col_4 = st.columns(4)

        with col_1:
            m2_current_value, m2_delta_value = ft.billion_nominal_metrics(m2_usa, start_date_col1, end_date_col1)
            st.metric('M2 nominal value', value=m2_current_value, delta=m2_delta_value, delta_color='inverse')
            m1_current_value, m1_delta_value = ft.billion_nominal_metrics(m1_usa, start_date_col1, end_date_col1)
            st.metric('M1 nominal value', value=m1_current_value, delta=m1_delta_value, delta_color='inverse')


        with col_2:
            cpi_current_value, cpi_delta_value = ft.nominal_metrics(cpi_usa, start_date_col1, end_date_col1, currency_name='')
            st.metric('CPI nominal value', value=cpi_current_value, delta=cpi_delta_value, delta_color='inverse')

            pce_current_value, pce_delta_value = ft.nominal_metrics(pce_usa, start_date_col1, end_date_col1, currency_name='')
            st.metric('PCE nominal value', value=pce_current_value, delta=pce_delta_value, delta_color='inverse')

        with col_3:
            value, delay = ft.get_best_correlation(m2_usa, cpi_usa, start_date_col2, end_date_col2)
            value_past_year, delay_past_year = ft.get_best_correlation(m2_usa, cpi_usa, start_date_col2, end_date_col2-timedelta(days=365))
            st.metric('Changes in M2 affect CPI within:', value=str(delay) + ' months', delta=str(delay-delay_past_year) + ' months regard anterior year')

        with col_4:
            st.metric('With a correlation of:', value=str(round(value*100, 1)) + ' %', delta=str(round((value-value_past_year)*100, 2)) + '% regard anterior year')

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
