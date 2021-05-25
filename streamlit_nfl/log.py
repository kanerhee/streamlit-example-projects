# log.py

import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime, timedelta
import altair as alt
import requests
import matplotlib
import io

def app():

    st.title('Change Log: ')
    st.write('by kanerhee')

    ####################################################################

    st.write('Changes: ')
    st.text('2020-10-30')
    st.text('Stacked Charts in O/D pages')
    st.text('Bug Fixes')
    st.text('Added event logger')
    st.text('2020-10-29')
    st.text('added log and singleplayer')
    st.text('2020-10-28')
    st.text('added headtohead and singleteam')

    ####################################################################

    st.write('Bugs: ')
    st.text('Average Column calculations drop by weeks')
    st.text('Single Team - aggregate row names')

    ####################################################################

    st.write('To Be Added: ')
    st.text('Average Column calculations drop by weeks')
    st.text('Single Team - aggregate row names')
