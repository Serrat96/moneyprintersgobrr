import streamlit as st
import pandas as pd

import sys, os

# Helpers
abspath = os.path.abspath
dirname = os.path.dirname
sep = os.sep

##################################################### FUNCTIONS #####################################################
#####
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