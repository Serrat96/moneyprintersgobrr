from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import *
import plotly.express as px
import pandas as pd
from fredapi import Fred
import streamlit as st
from millify import millify

# Funcion para filtrar desde una fecha
def filter_from_date(df, from_date, date_format='%Y-%m-%d'):
    mask = (df.index >= datetime.strptime(from_date, date_format))

    filtered_df = df.loc[mask]

    return filtered_df


# Funcion para filtrar entre dos fechas
def filter_between_dates(df, from_date, to_date, date_format='%Y-%m-%d'):
    mask = (df.index >= datetime.strptime(from_date, date_format)) & \
           (df.index <= datetime.strptime(to_date, date_format))

    filtered_df = df.loc[mask]

    return filtered_df


# Funcion para crear un gráfico con dos líneas
def two_plots(df1, df2, start_date, end_date, legend_graph_one='Legend<br>graph<br>one',
              legend_graph_two='Legend<br>graph<br>two',
              principal_title='principal title', name_graph_one='name_graph_one', name_graph_two='name_graph_two',
              tickformat='%'):
    start_date_str = str(start_date)
    end_date_str = str(end_date)
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df1_filter_1 = filter_between_dates(df1, start_date_str, end_date_str)
    df2_filter_2 = filter_between_dates(df2, start_date_str, end_date_str)
    fig.add_trace(go.Scatter(x=df1_filter_1.index, y=df1_filter_1['Value'], name=legend_graph_one, line=dict(color="#66D7D1")), secondary_y=False)
    fig.add_trace(go.Scatter(x=df2_filter_2.index, y=df2_filter_2['Value'], name=legend_graph_two, line=dict(color="#F63366")), secondary_y=True)

    fig.update_layout(title=principal_title, xaxis_rangeslider_visible=True,
                      title_font_size=30)  # , width=850, height=600)

    fig.update_xaxes(rangeslider_thickness=0.1, showgrid=False)

    fig.update_yaxes(title_text=name_graph_one, tickformat=tickformat, secondary_y=False, showgrid=False,
                     zeroline=False)
    fig.update_yaxes(title_text=name_graph_two, tickformat=tickformat, secondary_y=True, showgrid=False, zeroline=False)

    return fig


def four_plots(df1, df2, df3, df4, start_date, end_date, legend_graph_one='Legend<br>graph<br>one',
               legend_graph_two='Legend<br>graph<br>two',
               legend_graph_three='Legend<br>graph<br>three', legend_graph_four='Legend<br>graph<br>four',
               principal_title='principal title', name_graph_one='name_graph_one', name_graph_two='name_graph_two',
               tickformat='%', secondary_y_df1=False, secondary_y_df2=False, secondary_y_df3=False,
               secondary_y_df4=False):
    start_date_str = str(start_date)
    end_date_str = str(end_date)

    df1_filter = filter_between_dates(df1, start_date_str, end_date_str)
    df2_filter = filter_between_dates(df2, start_date_str, end_date_str)
    df3_filter = filter_between_dates(df3, start_date_str, end_date_str)
    df4_filter = filter_between_dates(df4, start_date_str, end_date_str)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=df1_filter.index, y=df1_filter['Value'], name=legend_graph_one, line=dict(color="#F63366")),
                  secondary_y=secondary_y_df1)

    fig.add_trace(go.Scatter(x=df2_filter.index, y=df2_filter['Value'], name=legend_graph_two, line=dict(color="#F97699")),
                  secondary_y=secondary_y_df2)

    fig.add_trace(go.Scatter(x=df3_filter.index, y=df3_filter['Value'], name=legend_graph_three, line=dict(color="#48A9A6")),
                  secondary_y=secondary_y_df3)

    fig.add_trace(go.Scatter(x=df4_filter.index, y=df4_filter['Value'], name=legend_graph_four, line=dict(color="#66D7D1")),
                  secondary_y=secondary_y_df4)

    fig.update_yaxes(title_text=name_graph_two, tickformat=tickformat, secondary_y=True, showgrid=False, zeroline=False)

    fig.update_yaxes(title_text=name_graph_one, tickformat=tickformat, secondary_y=False, showgrid=False,
                     zeroline=False)

    fig.update_layout(title=principal_title, xaxis_rangeslider_visible=True,
                      title_font_size=30)  # , width=850, height=600)

    fig.update_xaxes(rangeslider_thickness=0.1, showgrid=False)

    return fig


def three_plots(df1, df2, df3, start_date, end_date, legend_graph_one='Legend<br>graph<br>one',
                legend_graph_two='Legend<br>graph<br>two',
                legend_graph_three='Legend<br>graph<br>three',
                principal_title='principal title', name_graph_one='name_graph_one', name_graph_two='name_graph_two',
                tickformat='%', secondary_y_df1=False, secondary_y_df2=False, secondary_y_df3=False):
    start_date_str = str(start_date)
    end_date_str = str(end_date)

    df1_filter = filter_between_dates(df1, start_date_str, end_date_str)
    df2_filter = filter_between_dates(df2, start_date_str, end_date_str)
    df3_filter = filter_between_dates(df3, start_date_str, end_date_str)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=df1_filter.index, y=df1_filter['Value'], name=legend_graph_one),
                  secondary_y=secondary_y_df1)

    fig.add_trace(go.Scatter(x=df2_filter.index, y=df2_filter['Value'], name=legend_graph_two),
                  secondary_y=secondary_y_df2)

    fig.add_trace(go.Scatter(x=df3_filter.index, y=df3_filter['Value'], name=legend_graph_three),
                  secondary_y=secondary_y_df3)

    fig.update_yaxes(title_text=name_graph_two, tickformat=tickformat, secondary_y=True, showgrid=False, zeroline=False)

    fig.update_yaxes(title_text=name_graph_one, tickformat=tickformat, secondary_y=False, showgrid=False,
                     zeroline=False)

    fig.update_layout(title=principal_title, xaxis_rangeslider_visible=True,
                      title_font_size=30)  # , width=850, height=600)

    fig.update_xaxes(rangeslider_thickness=0.1, showgrid=False)

    return fig


# Gráfico de línea simple
def one_plot(df, graph_title='graph_title', x_axis='Date', y_axis='y_axis'):
    fig = px.line(df, labels={"Date": x_axis, "value": y_axis})

    fig.update_layout(title=graph_title, xaxis_rangeslider_visible=True, showlegend=False, title_font_size=30)

    fig.update_xaxes(rangeslider_thickness=0.1, showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False)

    return fig


# Para leer datos de los parquet
def read_data(path: str):
    try:
        return pd.read_parquet(path)
    except:
        initial_path = r'/app/moneyprintersgobrr/'
        path_2 = path[3:]
        return pd.read_parquet(initial_path + path_2)


# Obtener datos de la FED
def get_fred_data(api_key: str, series: str):
    fred = Fred(api_key=api_key)
    series = fred.get_series(series)
    series = pd.DataFrame(series, columns=['Value'])
    return series


# Correlacion entre dos variables
def two_variables_correlation(df1, df2, start_date, end_date):
    start_date_str = str(start_date)
    end_date_str = str(end_date)

    df1_filter = filter_between_dates(df1, start_date_str, end_date_str)
    df2_filter = filter_between_dates(df2, start_date_str, end_date_str)

    df = pd.concat([df1_filter, df2_filter], axis=1)

    corr_df = df.corr()

    return corr_df.iloc[0, 1]


def double_ended_slider(df, slider_title: str, key: str):
    try:
        format = 'MMM/YYYY'
        start_date = df.index[0].date()
        end_date = df.index[-1].date()
        start_date, end_date = st.sidebar.slider(slider_title, value=[start_date, end_date], format=format, key=key)
    except:
        start = df.index[0].date()
        end = df.index[-1].date()
        start_date, end_date = st.sidebar.date_input(slider_title, value=[start, end], key=key)

    return start_date, end_date


def get_best_correlation(df1, df2, start_date, end_date):
    list_correlations = []
    for i in range(0, 120):
        start_date_str = str(start_date)
        end_date_str = str(end_date)

        df1_filtered = filter_between_dates(df1, start_date_str, end_date_str)
        df2_filtered = filter_between_dates(df2, start_date_str, end_date_str)

        df2_shifted = df2_filtered.pct_change(12).shift(-i)
        df1_pct = df1_filtered.pct_change(12)

        df = pd.concat([df1_pct, df2_shifted], axis=1).dropna()

        df_corr = df.corr()

        list_correlations.append(df_corr.iloc[1, 0])

    return max(list_correlations), list_correlations.index(max(list_correlations)) + 1


def billion_nominal_metrics(df, start_date, end_date, currency_name ='$'):

    start_date_str = str(start_date)
    end_date_str = str(end_date)
    df_filtered = filter_between_dates(df, start_date_str, end_date_str)
    current_value = str(millify(df_filtered.iloc[-1]*1000000000, precision=3)) + currency_name
    delta_value = str(millify((df_filtered.iloc[-1]*1000000000) - df_filtered.iloc[-13]*1000000000 , precision=3)) + currency_name + ' regard anterior year'

    return current_value, delta_value


def nominal_metrics(df, start_date, end_date, currency_name ='$', precision=2):

    start_date_str = str(start_date)
    end_date_str = str(end_date)
    df_filtered = filter_between_dates(df, start_date_str, end_date_str)
    current_value = str(millify(df_filtered.iloc[-1], precision=3)) + currency_name
    delta_value = str(millify((df_filtered.iloc[-1]) - df_filtered.iloc[-13], precision=precision)) + currency_name + ' regard anterior year'

    return current_value, delta_value
