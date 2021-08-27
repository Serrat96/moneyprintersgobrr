import streamlit as st
from datetime import timedelta

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

@st.cache
def get_data():
    data_path = fo.path_to_folder(2, "data")

    # Raw data
    m1_usa = md.read_data(data_path + "M1NS" + sep +"M1NS.parquet")
    m2_usa = md.read_data(data_path + "M2NS" + sep +"M2NS.parquet")
    cpi_usa = md.read_data(data_path + 'CPIAUCNS' + sep +"CPIAUCNS.parquet")
    pce_usa = md.read_data(data_path + 'PCEPI' + sep +"PCEPI.parquet")
    
    # Transformed data
    m2_usa_percentage = m2_usa.pct_change(12).dropna()
    m1_usa_percentage = m1_usa.pct_change(12).dropna()
    cpi_usa_percentage = cpi_usa.pct_change(12).dropna()
    pce_usa_percentage = pce_usa.pct_change(12).dropna()

    return m1_usa, m2_usa, cpi_usa, pce_usa, m1_usa_percentage, m2_usa_percentage, cpi_usa_percentage, pce_usa_percentage

m1_usa, m2_usa, cpi_usa, pce_usa, m1_usa_percentage, m2_usa_percentage, cpi_usa_percentage, pce_usa_percentage = get_data()

# Objects
plotter = vi.st_plotter
processor = md.processor

##################################################### INTERFACE #####################################################

def main():
    menu = 'US'#st.sidebar.selectbox('Country', ct.countries_list)

    # UNITED STATES, US
    if menu == 'US':
        st.title('Inflation metrics for USA :flag-us:')
        col1, col2 = st.columns(2)

        ################# PLOTS #################
        #### LEFT COL
        with col1:

            to_plot = {
                "dfs": [m1_usa, m2_usa, cpi_usa, pce_usa],
                "legends": ["M1", "M2", "CPI", "PCE"],
                "secondary_ys": [False, False, True, True],
                "names": ["MONETARY AGGREGATES", "CPI & PCE"]
            }

            start_date_col1, end_date_col1 = da.double_ended_slider(to_plot, 'Monetary aggregates & CPI', key='1')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col1, end_date=end_date_col1,
                                    palette=ct.four_line_palette, title="Monetary aggregates & CPI"),
                use_container_width=True)
            
        #### RIGHT COL
        with col2:
            to_plot = {
                "dfs": [m2_usa_percentage, cpi_usa_percentage, pce_usa_percentage],
                "legends": ["M2", "CPI", 'PCE'],
                "secondary_ys": [False, True, True],
                "names": ["M2", "CPI & PCE"]
            }

            start_date_col2, end_date_col2 = da.double_ended_slider(to_plot, 'M2 & CPI annual change', key='2')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col2, end_date = end_date_col2,
                                     palette=ct.three_line_palette, title = "M2 & CPI annual change", tickformat = "%"),
                use_container_width=True)


        ################# METRICS #################
        col_1, col_2, col_3, col_4 = st.columns(4)

        #### LEFT COL
        with col_1:
            # Data extraction
            m2_current_value, m2_delta_value = processor.calculate_metrics(m2_usa, start_date_col1, end_date_col1)
            m1_current_value, m1_delta_value = processor.calculate_metrics(m1_usa, start_date_col1, end_date_col1)
            
            # Plot
            st.metric('M2 nominal value', value=m2_current_value, delta=m2_delta_value, delta_color='inverse')
            st.metric('M1 nominal value', value=m1_current_value, delta=m1_delta_value, delta_color='inverse')

        with col_2:
            # Data extraction
            cpi_current_value, cpi_delta_value = processor.calculate_metrics(cpi_usa, start_date_col1, end_date_col1,
                                                                             multiplier=1, currency_name='', precision=2)
            pce_current_value, pce_delta_value = processor.calculate_metrics(pce_usa, start_date_col1, end_date_col1,
                                                                             multiplier=1, currency_name='')
            
            # Plot
            st.metric('CPI nominal value', value=cpi_current_value, delta=cpi_delta_value, delta_color='inverse')
            st.metric('PCE nominal value', value=pce_current_value, delta=pce_delta_value, delta_color='inverse')


        #### RIGHT COL
        with col_3:
            # Data extraction
            value, delay = processor.get_best_correlation(m2_usa, cpi_usa, start_date_col2, end_date_col2)
            value_past_year, delay_past_year = processor.get_best_correlation(m2_usa, cpi_usa, start_date_col2, end_date_col2-timedelta(days=365))
            value_pce, delay_pce = processor.get_best_correlation(m2_usa, pce_usa, start_date_col2, end_date_col2)
            value_past_year_pce, delay_past_year_pce = processor.get_best_correlation(m2_usa, pce_usa, start_date_col2,
                                                                              end_date_col2 - timedelta(days=365))

            # Plot
            st.metric('Changes in M2 affect CPI within:', value=str(delay) + ' months',
                      delta=str(delay-delay_past_year) + ' months regard anterior year')
            st.metric('Changes in M2 affect PCE within:', value=str(delay_pce) + ' months',
                      delta=str(delay_pce-delay_past_year_pce) + ' months regard anterior year')

        with col_4:
            st.metric('With a correlation of:', value=str(round(value*100, 1)) + ' %',
                      delta=str(round((value-value_past_year)*100, 2)) + '% regard anterior year')
            st.metric('With a correlation of:', value=str(round(value_pce * 100, 1)) + ' %',
                      delta=str(round((value_pce - value_past_year_pce) * 100, 2)) + '% regard anterior year')

        ################# ANNOTATIONS #################
        col_1, col_2 = st.columns(2)

        with col_1.expander(label='What´s the meaning of the metrics?'):
            st.write('All the metrics represent the nominal value of itself in the lastest date selected on the sidebar and his variation regard the anterior year')

        with col_2.expander(label='What is being calculated here?'):
            st.write('Basically, how long does it take for a variation of M2 to affect the CPI & PCE for the selected period in the side menu slidebar')

        regression = mo.AutomaticLinearRegression('Prueba', [m1_usa], cpi_usa)
        model_metrics_dict = regression.linear_regression(start_date_col1, end_date_col1)
        st.write(model_metrics_dict)

if __name__ == '__main__':
    main()