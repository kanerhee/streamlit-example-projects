# defense.py

import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime, timedelta
import altair as alt
import requests
import matplotlib
import io
import warnings

warnings.filterwarnings('ignore')

def make_alt_barchart(df, offordef):

    df2 = df.copy()
    # df2 = df2[df2['Defense'] == teamsChosen]
    df2 = df2[df2['PlayType'].isin(['RUSH', 'PASS', 'SACK', 'SCRAMBLE'])]
    df2 = df2.groupby(['Week', offordef, 'PlayType']).agg({'Yards':'sum'}).reset_index()

    source = df2.copy()

    a = alt.Chart(source).mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        x='Week:O',
        y='Yards:Q',
        color='PlayType:N'
    ).properties(
        width=700,
        height=300
    )

    return a

def defenseYards(df, PLAYTYPE):

    df2 = df.copy()

    if PLAYTYPE:
        df2 = df2[df2['PlayType'] == PLAYTYPE]

    df2.rename(columns={'Yards':'week'}, inplace=True)
    df2 = df2.groupby(['Defense', 'Week']).agg({'week':'sum'}).unstack().fillna(0.0)

    x = 0
    df2['Total'] = 0
    while x < (df2.shape[1]-1):
        df2['Total'] = df2['Total'] + df2.iloc[:,x]
        x += 1
    df2['Average'] = (df2['Total'] / (df2.shape[1]-1)).astype(int)

    df2 = df2.sort_values(by='Average', ascending=False).reset_index()

    return df2


def DefensePlaysOf(df, threshold):

    df2 = df.copy()
    df2 = df2[df2['Yards'] >= threshold]
    df2.rename(columns={'Yards':'week'}, inplace=True)
    df2 = df2.groupby(['Defense', 'Week']).agg({'week':'count'}).unstack().fillna(0)

    x = 0
    df2['Total'] = 0
    while x < (df2.shape[1]-1):
        df2['Total'] = df2['Total'] + df2.iloc[:,x]
        x += 1
    df2['Average'] = (df2['Total'] / (df2.shape[1]-1)).astype(int)

    df2 = df2.sort_values(by='Average', ascending=False).reset_index()

    return df2


def app():

    st.title('Defense')
    st.write('by kanerhee')

    ####################################################################

    df = pd.read_csv('/home/ubuntu/streamlit-nfl/data/nflpbpdata.csv', low_memory='False')
    # df = pd.read_csv('/Users/kanerhee/Desktop/streamlit2/data/nflpbpdata.csv', low_memory='False')

    AllTeams = [x for x in list(set(df.Defense)) if str(x) != 'nan']
    AllWeeks = [x for x in list(set(df.Week)) if str(x) != 'nan']

    # Filter 1 - Teams
    teamsChosen = st.multiselect("Choose Teams", AllTeams, AllTeams)
    if not teamsChosen:
        st.error("Please select at least one team")

    # Filter 2 - Weeks
    weeksChosen = st.multiselect("Choose Weeks", AllWeeks, AllWeeks)
    if not weeksChosen:
        st.error("Please select at least one week")

    df = df[df.Offense.isin(teamsChosen) | df.Defense.isin(teamsChosen)]
    df = df[df.Week.isin(weeksChosen)]

    ###################################################################

    st.write('Defensive Yards per Week - Bar')
    st.write(make_alt_barchart(df.copy(), 'Defense'))

    st.write('Defense Yards Allowed per Week - Crosstab')
    st.write(defenseYards(df.copy(), False))
