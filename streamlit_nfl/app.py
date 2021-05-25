import offense
import defense
import headtohead
import singleteam
import singleplayer
import log
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime, timedelta, date
import altair as alt
import requests
import matplotlib
import io
import warnings

warnings.filterwarnings('ignore')


def logtouch(pathname, pagename):

    df = pd.read_csv(pathname)
    if 'Unnamed: 0' in df:
        df.drop(columns=['Unnamed: 0'], inplace=True)
    t = 'touch'
    today = date.today()
    d1 = today.strftime("%m/%d/%Y")
    now = datetime.now()
    d2 = now.strftime("%Y-%m-%d %H:%M")
    df2 = pd.DataFrame({'Date':[d1],
                       'Time':[d2],
                       'Touch':[t],
                       'Where':[pagename]})
    df = df.append(df2)
    df.to_csv(pathname)
    del df
    print(now)
    return


pathname1 = ('/Users/kanerhee/Desktop/streamlit2/data/touchlog.csv')
pathname2 = ('/home/ubuntu/streamlit-nfl/data/nflpbpdata.csv')

PAGES = {
    'Offenses' : offense,
    'Defenses' : defense,
    'Single Team' : singleteam,
    'Head to Head' : headtohead,
    'Single Player' : singleplayer,
    'Log' : log
}


st.sidebar.text('https://github.com/kanerhee')
st.sidebar.title('Navigation')

selection = st.sidebar.radio("Go to: ", list(PAGES.keys()))
page = PAGES[selection]
logtouch(pathname2, selection)
page.app()
