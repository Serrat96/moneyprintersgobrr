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

usa_data_path = fo.path_to_folder(2, "data" + sep + "usa")


@st.cache
def get_usa_data():
    usa_data_path = fo.path_to_folder(2, "data" + sep + "usa")

    # Raw data
    m1_usa = md.read_data_(usa_data_path + "M1NS" + sep + "M1NS.parquet")
    m2_usa = md.read_data_(usa_data_path + "M2NS" + sep + "M2NS.parquet")
    cpi_usa = md.read_data_(usa_data_path + 'CPIAUCNS' + sep + "CPIAUCNS.parquet")
    pce_usa = md.read_data_(usa_data_path + 'PCEPI' + sep + "PCEPI.parquet")
    unemployment_usa = md.read_data_(usa_data_path + 'LNU03000000' + sep + 'LNU03000000.parquet')
    unemployment_usa_percentage = md.read_data_(usa_data_path + 'UNRATENSA' + sep + "UNRATENSA.parquet")
    adq_usa = md.read_data_(usa_data_path + 'CUUR0000SA0R' + sep + "CUUR0000SA0R.parquet")
    m1_velocity_usa = md.read_data_(usa_data_path + 'M1V' + sep + "M1V.parquet")
    m2_velocity_usa = md.read_data_(usa_data_path + 'M2V' + sep + "M2V.parquet")

    # Transformed data
    m2_usa_percentage = m2_usa.pct_change(12).dropna()
    m1_usa_percentage = m1_usa.pct_change(12).dropna()
    cpi_usa_percentage = cpi_usa.pct_change(12).dropna()
    pce_usa_percentage = pce_usa.pct_change(12).dropna()
    adq_usa_percentage = adq_usa.pct_change(12).dropna()
    m1_velocity_usa_percentage = m1_velocity_usa.pct_change(12).dropna()
    m2_velocity_usa_percentage = m2_velocity_usa.pct_change(12).dropna()
    return m1_usa, m2_usa, cpi_usa, pce_usa, m1_usa_percentage, m2_usa_percentage, cpi_usa_percentage, pce_usa_percentage, unemployment_usa, unemployment_usa_percentage, adq_usa, adq_usa_percentage, \
           m1_velocity_usa, m1_velocity_usa_percentage, m2_velocity_usa, m2_velocity_usa_percentage


@st.cache
def get_eur_data():
    eur_data_path = fo.path_to_folder(2, "data" + sep + "euro")

    # Raw data
    m1_eur = md.read_data_(abspath(eur_data_path + "M1" + sep + "M1.parquet"))
    m2_eur = md.read_data_(eur_data_path + "M2" + sep + "M2.parquet")
    m3_eur = md.read_data_(eur_data_path + 'M3' + sep + "M3.parquet")
    icp_eur = md.read_data_(eur_data_path + 'ICP' + sep + "ICP.parquet")

    # Transformed data
    m1_eur_percentage = m1_eur.pct_change(12).dropna()
    m2_eur_percentage = m1_eur.pct_change(12).dropna()
    m3_eur_percentage = m3_eur.pct_change(12).dropna()
    icp_eur_percentage = icp_eur.pct_change(12).dropna()

    return m1_eur, m2_eur, m3_eur, icp_eur, m1_eur_percentage, m2_eur_percentage, m3_eur_percentage, icp_eur_percentage


m1_usa, m2_usa, cpi_usa, pce_usa, m1_usa_percentage, m2_usa_percentage, cpi_usa_percentage, pce_usa_percentage, unemployment_usa, unemployment_usa_percentage, adq_usa, adq_usa_percentage, \
m1_velocity_usa, m1_velocity_usa_percentage, m2_velocity_usa, m2_velocity_usa_percentage = get_usa_data()

m1_eur, m2_eur, m3_eur, icp_eur, m1_eur_percentage, m2_eur_percentage, m3_eur_percentage, icp_eur_percentage = get_eur_data()


# Objects
plotter = vi.st_plotter
processor = md.processor


##################################################### INTERFACE #####################################################

def main():
    menu = st.sidebar.selectbox('Country', ct.countries_list)

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
                "secondary_ys": [True, True, False, False],
                "names": ["CPI & PCE", "MONETARY AGGREGATES"]
            }

            start_date_col1, end_date_col1 = da.double_ended_slider(to_plot, 'CPI, PCE & monetary aggregates', key='1')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col1, end_date=end_date_col1,
                                     palette=ct.four_line_palette,
                                     note='CPI: Index 1982-1984=100<br>PCE: Index 2012=100',
                                     x_annot=1, y_annot=-0.17, x_legend=0, y_legend=1,
                                     title="CPI, PCE & monetary aggregates"),
                use_container_width=True)

        #### RIGHT COL
        with col2:
            to_plot = {
                "dfs": [m2_usa_percentage, cpi_usa_percentage, pce_usa_percentage],
                "legends": ["M2", "CPI", 'PCE'],
                "secondary_ys": [True, False, False],
                "names": ["CPI & PCE", "M2"]
            }

            start_date_col2, end_date_col2 = da.double_ended_slider(to_plot, 'CPI, PCE & M2 annual change', key='2')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col2, end_date=end_date_col2,
                                     palette=ct.three_line_palette, x_legend=0, y_legend=1,
                                     title="CPI, PCE & M2 annual change",
                                     tickformat=".2%"),
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
                                                                             multiplier=1, currency_name='',
                                                                             precision=2)
            pce_current_value, pce_delta_value = processor.calculate_metrics(pce_usa, start_date_col1, end_date_col1,
                                                                             multiplier=1, currency_name='')

            # Plot
            st.metric('CPI nominal value', value=cpi_current_value, delta=cpi_delta_value, delta_color='inverse')
            st.metric('PCE nominal value', value=pce_current_value, delta=pce_delta_value, delta_color='inverse')

        #### RIGHT COL
        with col_3:
            # Data extraction
            value, delay = processor.get_best_correlation(m2_usa, cpi_usa, start_date_col2, end_date_col2)
            value_past_year, delay_past_year = processor.get_best_correlation(m2_usa, cpi_usa, start_date_col2,
                                                                              end_date_col2 - timedelta(days=365))
            value_pce, delay_pce = processor.get_best_correlation(m2_usa, pce_usa, start_date_col2, end_date_col2)
            value_past_year_pce, delay_past_year_pce = processor.get_best_correlation(m2_usa, pce_usa, start_date_col2,
                                                                                      end_date_col2 - timedelta(
                                                                                          days=365))

            # Plot
            st.metric('Changes in M2 affect CPI within:', value=str(delay) + ' months',
                      delta=str(delay - delay_past_year) + ' months regard anterior year')
            st.metric('Changes in M2 affect PCE within:', value=str(delay_pce) + ' months',
                      delta=str(delay_pce - delay_past_year_pce) + ' months regard anterior year')

        with col_4:
            st.metric('With a correlation of:', value=str(round(value * 100, 1)) + ' %',
                      delta=str(round((value - value_past_year) * 100, 2)) + '% regard anterior year')
            st.metric('With a correlation of:', value=str(round(value_pce * 100, 1)) + ' %',
                      delta=str(round((value_pce - value_past_year_pce) * 100, 2)) + '% regard anterior year')

        ################# ANNOTATIONS #################
        col_1, col_2 = st.columns(2)

        with col_1.expander(label='What´s the meaning of the metrics?'):
            st.write(
                'All the metrics represent the nominal value of itself in the lastest date selected on the sidebar and his variation regard the anterior year.\n\n'
                'M1: the sum of currency held by the public and transaction deposits at depository institutions (which are financial institutions that obtain their '
                'funds mainly through deposits from the public, such as commercial banks, savings and loan associations, savings banks, and credit unions)\n\n'
                'M2: M1 plus savings deposits, small-denomination time deposits (those issued in amounts of less than $100,000), and retail money market mutual fund shares.')

        with col_2.expander(label='What is being calculated here?'):
            st.write(
                'Basically, how long does it take for a variation of M2 to affect the CPI & PCE for the selected period in the side menu slidebar.\n\n'
                'It is calculated shifting month by month the dataframes, and calculating the correlation for each iteration. Best correlation is showed '
                'with the neccesary shifting periods (months) needed to get that correlation.')

        col_1, col_2 = st.columns(2)

        with col_1:
            to_plot = {
                "dfs": [cpi_usa, unemployment_usa],
                "legends": ["CPI", "UNEMPLOYED"],
                "secondary_ys": [False, True],
                "names": ["CPI", "UNEMPLOYED"]
            }

            start_date_col1, end_date_col1 = da.double_ended_slider(to_plot, 'CPI & Unemployed people', key='3')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col1, end_date=end_date_col1,
                                     palette=ct.two_line_palette, note='CPI: Index 1982-1984=100',
                                     x_annot=1, y_annot=-0.12, title="CPI & Unemployed people"),
                use_container_width=True)

        with col_2:
            to_plot = {
                "dfs": [cpi_usa_percentage, unemployment_usa_percentage],
                "legends": ["CPI", "UNEMPLOYMENT"],
                "secondary_ys": [False, True],
                "names": ["CPI", "UNEMPLOYMENT"]
            }

            start_date_col1, end_date_col1 = da.double_ended_slider(to_plot, 'CPI & Unemployment', key='4')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col1, end_date=end_date_col1,
                                     palette=ct.two_line_palette,
                                     note='CPI: Change respect anterior year<br>Unemployment: Percentage of the labor force',
                                     x_annot=1, y_annot=-0.17, title="CPI & Unemployment<br>percentage",
                                     tickformat='.2%'),
                use_container_width=True)

        col_1, col_2, col_3, col_4 = st.columns(4)

        #### LEFT COL
        with col_1:
            # Data extraction
            une_current_value, une_delta_value = processor.calculate_metrics(unemployment_usa, start_date_col1,
                                                                             end_date_col1, currency_name='')

            # Plot
            st.metric('Unemployed people', value=une_current_value, delta=une_delta_value, delta_color='inverse')

        with col_2:
            # Data extraction
            unemployment_usa_percentage_current_value, unemployment_usa_percentage_delta_value = processor.calculate_metrics(
                unemployment_usa_percentage, start_date_col1, end_date_col1,
                multiplier=100, currency_name='', symbol='%',
                precision=4)

            # Plot
            st.metric('Unemployment pct', value=str(float(unemployment_usa_percentage_current_value)) + ' %',
                      delta=unemployment_usa_percentage_delta_value, delta_color='inverse')

        #### RIGHT COL
        with col_3:
            # Data extraction
            value, delay = processor.get_best_correlation(unemployment_usa_percentage, cpi_usa, start_date_col2,
                                                          end_date_col2)
            value_past_year, delay_past_year = processor.get_best_correlation(unemployment_usa_percentage, cpi_usa,
                                                                              start_date_col2,
                                                                              end_date_col2 - timedelta(days=365))

            # Plot
            st.metric('Unemployment pct affects CPI within:', value=str(delay) + ' months',
                      delta=str(delay - delay_past_year) + ' months regard anterior year')

        with col_4:
            st.metric('With a correlation of:', value=str(round(value * 100, 1)) + ' %',
                      delta=str(round((value - value_past_year) * 100, 2)) + '% regard anterior year')

        col_1, col_2 = st.columns(2)

        with col_1:
            to_plot = {
                "dfs": [cpi_usa, adq_usa],
                "legends": ["CPI", "USD PURCHASING POWER"],
                "secondary_ys": [False, True],
                "names": ["CPI", "USD PURCHASING POWER"]
            }

            start_date_col1, end_date_col1 = da.double_ended_slider(to_plot, 'CPI & USD purchasing power', key='5')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col1, end_date=end_date_col1,
                                     palette=ct.two_line_palette,
                                     note='CPI: Index 1982-1984=100<br>Purchasing power: Index 1982-1984=100',
                                     x_annot=1, y_annot=-0.17, x_legend=0.05, title="CPI & USD purchasing power"),
                use_container_width=True)

        with col_2:
            to_plot = {
                "dfs": [cpi_usa_percentage, adq_usa_percentage],
                "legends": ["CPI", "USD PURCHASING POWER"],
                "secondary_ys": [False, True],
                "names": ["CPI", "USD PURCHASING POWER"]
            }

            start_date_col1, end_date_col1 = da.double_ended_slider(to_plot, 'CPI & USD purchasing power annual change',
                                                                    key='6')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col1, end_date=end_date_col1,
                                     palette=ct.two_line_palette,
                                     note='CPI: Change respect anterior year<br>USD purchasing power: Change respect anterior year',
                                     x_annot=1, y_annot=-0.17, x_legend=0.1,
                                     title="CPI & USD purchasing power<br>annual change",
                                     tickformat='.2%'),
                use_container_width=True)

        col_1, col_2, col_3, col_4 = st.columns(4)

        #### LEFT COL
        with col_1:
            # Data extraction
            adq_usa_current_value, adq_usa_delta_value = processor.calculate_metrics(adq_usa, start_date_col1,
                                                                                     end_date_col1, currency_name='')

            # Plot
            st.metric('USD purchasing power', value=adq_usa_current_value, delta=adq_usa_delta_value)

        with col_2:
            # Data extraction
            adq_usa_percentage_current_value, adq_usa_percentage_delta_value = processor.calculate_metrics(
                adq_usa_percentage, start_date_col1, end_date_col1,
                multiplier=100, currency_name='', symbol='%',
                precision=4)

            # Plot
            st.metric('Puchasing power change', value=str(round(float(adq_usa_percentage_current_value), 2)) + '%',
                      delta=adq_usa_percentage_delta_value)

        #### RIGHT COL
        with col_3:
            # Data extraction
            value, delay = processor.get_best_correlation(adq_usa_percentage, cpi_usa, start_date_col2,
                                                          end_date_col2)
            value_past_year, delay_past_year = processor.get_best_correlation(adq_usa_percentage, cpi_usa,
                                                                              start_date_col2,
                                                                              end_date_col2 - timedelta(days=365))

            # Plot
            st.metric('USD purchasing power affects CPI within:', value=str(delay) + ' months',
                      delta=str(delay - delay_past_year) + ' months regard anterior year')

        with col_4:
            st.metric('With a correlation of:', value=str(round(value * 100, 1)) + ' %',
                      delta=str(round((value - value_past_year) * 100, 2)) + '% regard anterior year')

        col_1, col_2 = st.columns(2)

        with col_1:
            to_plot = {
                "dfs": [cpi_usa, m1_velocity_usa, m2_velocity_usa],
                "legends": ["CPI", "M1 VELOCITY", "M2 VELOCITY"],
                "secondary_ys": [False, True, True],
                "names": ["CPI", "M1 & M2 VELOCITY"]
            }

            start_date_col1, end_date_col1 = da.double_ended_slider(to_plot, 'CPI, M1 & M2 velocity', key='7')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col1, end_date=end_date_col1,
                                     palette=ct.three_line_palette,
                                     note='CPI: Index 1982-1984=100',
                                     x_annot=1, y_annot=-0.12, x_legend=0.05, title="CPI, M1 & M2 velocity"),
                use_container_width=True)

        with col_2:
            to_plot = {
                "dfs": [cpi_usa_percentage, m1_velocity_usa_percentage, m2_velocity_usa_percentage],
                "legends": ["CPI", "M1 VELOCITY", "M2 VELOCITY"],
                "secondary_ys": [False, True, True],
                "names": ["CPI", "M1 & M2 VELOCITY CHANGE"]
            }

            start_date_col1, end_date_col1 = da.double_ended_slider(to_plot, 'CPI, M1 & M2 velocity annual change',
                                                                    key='8')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col1, end_date=end_date_col1,
                                     palette=ct.three_line_palette,
                                     note='',
                                     x_legend=0, y_legend=0,
                                     title="CPI & USD purchasing power<br>annual change",
                                     tickformat='.2%'),
                use_container_width=True)

        col_1, col_2, col_3, col_4 = st.columns(4)

        #### LEFT COL
        with col_1:
            # Data extraction
            m1_velocity_usa_current_value, m1_velocity_usa_delta_value = processor.calculate_metrics(m1_velocity_usa, start_date_col1,
                                                                                     end_date_col1, currency_name='')

            # Plot
            st.metric('M1 money velocity', value=m1_velocity_usa_current_value, delta=m1_velocity_usa_delta_value)

            # Data extraction
            m1_velocity_usa_percentage_current_value, m1_velocity_usa_percentage_delta_value = processor.calculate_metrics(m1_velocity_usa_percentage,
                                                                                                     start_date_col1,
                                                                                                     end_date_col1,
                                                                                                    multiplier=100,
                                                                                                     currency_name='', symbol='%')

            # Plot
            st.metric('M1 money velocity has changed', value=m1_velocity_usa_percentage_current_value + '%', delta=m1_velocity_usa_percentage_delta_value)

        with col_2:
            # Data extraction
            m2_velocity_usa_current_value, m2_velocity_usa_delta_value = processor.calculate_metrics(
                m2_velocity_usa, start_date_col1, end_date_col1,
                multiplier=100, currency_name='',
                precision=4)

            # Plot
            st.metric('M2 money velocity', value=str(float(m2_velocity_usa_current_value)),
                      delta=m2_velocity_usa_delta_value)

            # Data extraction
            m2_velocity_usa_percentage_current_value, m2_velocity_usa_percentage_delta_value = processor.calculate_metrics(
                m2_velocity_usa_percentage,
                start_date_col1,
                end_date_col1,
                multiplier=100,
                currency_name='', symbol='%')

            # Plot
            st.metric('M1 money velocity has changed', value=m2_velocity_usa_percentage_current_value + '%',
                      delta=m2_velocity_usa_percentage_delta_value + '%')

        #### RIGHT COL
        with col_3:
            # Data extraction
            value, delay = processor.get_best_correlation(m1_velocity_usa, cpi_usa, start_date_col2,
                                                          end_date_col2)
            value_past_year, delay_past_year = processor.get_best_correlation(m1_velocity_usa, cpi_usa,
                                                                              start_date_col2,
                                                                              end_date_col2 - timedelta(days=365))

            value_2, delay_2 = processor.get_best_correlation(m2_velocity_usa, cpi_usa, start_date_col2,
                                                          end_date_col2)
            value_past_year_2, delay_past_year_2 = processor.get_best_correlation(m2_velocity_usa, cpi_usa,
                                                                              start_date_col2,
                                                                              end_date_col2 - timedelta(days=365))

            # Plot
            st.metric('M1 velocity afects CPI within:', value=str(delay) + ' months',
                      delta=str(delay - delay_past_year) + ' months regard anterior year')
            st.metric('M2 velocity afects CPI within:', value=str(delay_2) + ' months',
                      delta=str(delay_2 - delay_past_year_2) + ' months regard anterior year')

        with col_4:
            st.metric('With a correlation of:', value=str(round(value * 100, 1)) + ' %',
                      delta=str(round((value - value_past_year) * 100, 2)) + '% regard anterior year')
            st.metric('With a correlation of:', value=str(round(value_2 * 100, 1)) + ' %',
                      delta=str(round((value_2 - value_past_year_2) * 100, 2)) + '% regard anterior year')

    ###################################################################################################################
    # EUROPEAN UNION, EUR##############################################################################################
    if menu == 'EUR':
        st.title('Inflation metrics for EUR :flag-eu:')
        col1, col2 = st.columns(2)

        ################# PLOTS #################
        #### LEFT COL
        with col1:
            to_plot = {
                "dfs": [m1_eur, m2_eur, m3_eur, icp_eur],
                "legends": ["M1", "M2", "M3", "ICP"],
                "secondary_ys": [False, False, False, True],
                "names": ["MONETARY AGGREGATES", "ICP"]
            }

            start_date_col1, end_date_col1 = da.double_ended_slider(to_plot, 'Monetary aggregates & ICP', key='1')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col1, end_date=end_date_col1,
                                     palette=ct.four_line_palette, title="Monetary aggregates & ICP", tickformat=''),
                use_container_width=True)

        #### RIGHT COL
        with col2:
            to_plot = {
                "dfs": [m1_eur_percentage, m2_eur_percentage, m3_eur_percentage, icp_eur_percentage],
                "legends": ["M1", "M2", 'M3', 'ICP'],
                "secondary_ys": [False, False, False, True],
                "names": ["MONETARY AGGREGATES", "ICP"]
            }

            start_date_col2, end_date_col2 = da.double_ended_slider(to_plot, 'Monetary aggregates & ICP annual change',
                                                                    key='2')

            st.plotly_chart(
                plotter.line_plotter(to_plot, start_date=start_date_col2, end_date=end_date_col2,
                                     palette=ct.three_line_palette, title="Mon. agg. & ICP annual change",
                                     tickformat=".2%"),
                use_container_width=True)

        ################# METRICS #################
        col_1, col_2, col_3, col_4 = st.columns(4)

        #### LEFT COL
        with col_1:
            # Data extraction
            m1_current_value, m1_delta_value = processor.calculate_metrics(m1_eur, start_date_col1, end_date_col1)
            m2_current_value, m2_delta_value = processor.calculate_metrics(m2_eur, start_date_col1, end_date_col1)
            m3_current_value, m3_delta_value = processor.calculate_metrics(m3_eur, start_date_col1, end_date_col1)

            # Plot
            st.metric('M3 nominal value', value=m3_current_value, delta=m3_delta_value, delta_color='inverse')
            st.metric('M2 nominal value', value=m2_current_value, delta=m2_delta_value, delta_color='inverse')

        with col_2:
            st.metric('M1 nominal value', value=m1_current_value, delta=m1_delta_value, delta_color='inverse')
            # Data extraction
            cpi_current_value, cpi_delta_value = processor.calculate_metrics(icp_eur, start_date_col1, end_date_col1,
                                                                             multiplier=1, currency_name='',
                                                                             precision=2)

            # Plot
            st.metric('ICP nominal value', value=cpi_current_value, delta=cpi_delta_value, delta_color='inverse')

        #### RIGHT COL
        with col_3:
            # Data extraction
            value, delay = processor.get_best_correlation(m3_eur, icp_eur, start_date_col2, end_date_col2)
            value_past_year, delay_past_year = processor.get_best_correlation(m3_eur, icp_eur, start_date_col2,
                                                                              end_date_col2 - timedelta(days=365))
            value_pce, delay_pce = processor.get_best_correlation(m2_eur, icp_eur, start_date_col2, end_date_col2)
            value_past_year_pce, delay_past_year_pce = processor.get_best_correlation(m2_eur, icp_eur, start_date_col2,
                                                                                      end_date_col2 - timedelta(
                                                                                          days=365))

            # Plot
            st.metric('Changes in M3 affect ICP within:', value=str(delay) + ' months',
                      delta=str(delay - delay_past_year) + ' months regard anterior year')
            st.metric('Changes in M2 affect ICP within:', value=str(delay_pce) + ' months',
                      delta=str(delay_pce - delay_past_year_pce) + ' months regard anterior year')

        with col_4:
            st.metric('With a correlation of:', value=str(round(value * 100, 1)) + ' %',
                      delta=str(round((value - value_past_year) * 100, 2)) + '% regard anterior year')
            st.metric('With a correlation of:', value=str(round(value_pce * 100, 1)) + ' %',
                      delta=str(round((value_pce - value_past_year_pce) * 100, 2)) + '% regard anterior year')

        ################# ANNOTATIONS #################
        col_1, col_2 = st.columns(2)

        with col_1.expander(label='What´s the meaning of the metrics?'):
            st.write(
                'All the metrics represent the nominal value of itself in the lastest date selected on the sidebar and his variation regard the anterior year')

        with col_2.expander(label='What is being calculated here?'):
            st.write(
                'Basically, how long does it take for a variation of M3 & M2 to affect the ICP for the selected period in the side menu slidebar')


if __name__ == '__main__':
    main()
