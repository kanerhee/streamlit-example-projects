# headtohead.py

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

def make_alt_barchart(df, offordef, teamChosen):

    df2 = df.copy()
    df2 = df2[df2[offordef].isin(teamChosen)]
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
        width=300,
        height=300
    )

    return a



def groupby1(df, tc):

    playtypelist = ['PASS', 'RUSH', 'SCRAMBLE', 'SACK']
    df2 = df.copy()

    df2 = df2[df2['Offense'].isin(tc)]
    df2 = df2[df2['PlayType'].isin(playtypelist)]

    df2.rename(columns={'Yards':'week'}, inplace=True)

    df2 = df2.groupby(['Offense', 'PlayType', 'Week']).agg({'week':'sum'}).unstack().fillna(0)

    x = 0
    df2['Total'] = 0
    while x < (df2.shape[1]-1):
        df2['Total'] = df2['Total'] + df2.iloc[:,x]
        x += 1
    df2['Average'] = (df2['Total'] / (df2.shape[1]-1)).astype(int)

    return df2

def groupby2(df, tc):

    playtypelist = ['PASS', 'RUSH', 'SCRAMBLE', 'SACK']
    df2 = df.copy()

    df2 = df2[df2['Defense'].isin(tc)]
    df2 = df2[df2['PlayType'].isin(playtypelist)]

    df2.rename(columns={'Yards':'week'}, inplace=True)

    df2 = df2.groupby(['Defense', 'PlayType', 'Week']).agg({'week':'sum'}).unstack().fillna(0)

    x = 0
    df2['Total'] = 0
    while x < (df2.shape[1]-1):
        df2['Total'] = df2['Total'] + df2.iloc[:,x]
        x += 1
    df2['Average'] = (df2['Total'] / (df2.shape[1]-1)).astype(int)

    return df2

def app():

    st.title('Head to Head')
    st.write('by kanerhee')

    ####################################################################

    df = pd.read_csv('/home/ubuntu/streamlit-nfl/data/nflpbpdata.csv', low_memory='False')
    # df = pd.read_csv('/Users/kanerhee/Desktop/streamlit2/data/nflpbpdata.csv', low_memory='False')

    AllTeams = [x for x in list(set(df.Offense)) if str(x) != 'nan']
    AllWeeks = [x for x in list(set(df.Week)) if str(x) != 'nan']

    # Filter - Weeks
    weeksChosen = st.multiselect("Choose Weeks", AllWeeks, AllWeeks)
    if not weeksChosen:
        st.error("Please select at least one week")

    df1 = df.copy()
    df2 = df.copy()

    df1 = df1[df1.Week.isin(weeksChosen)]
    df2 = df2[df2.Week.isin(weeksChosen)]

    ####################################################################

    col1, col2 = st.beta_columns(2)

    with col1:

        teamChosen1 = st.multiselect("Choose Team 1", AllTeams)
        if len(teamChosen1) > 1:
            st.error("Max team limit: 1")

        df1 = df[df.Offense.isin(teamChosen1) | df.Defense.isin(teamChosen1)]

        st.header("Team 1:")

        st.write("Offensive Summary:")
        st.write(make_alt_barchart(df1.copy(), 'Offense', teamChosen1))
        # st.write(groupby1(df1.copy(), teamChosen1))

        st.write("Defensive Summary:")
        st.write(make_alt_barchart(df1.copy(), 'Defense', teamChosen1))
        # st.write(groupby2(df1.copy(), teamChosen1))

    with col2:

        teamChosen2 = st.multiselect("Choose Team 2", AllTeams)
        if len(teamChosen2) > 1:
            st.error("Max team limit: 1")

        df2 = df[df.Offense.isin(teamChosen2) | df.Defense.isin(teamChosen2)]

        st.header("Team 2:")

        st.write("Defensive Summary:")
        st.write(make_alt_barchart(df2.copy(), 'Defense', teamChosen2))
        # st.write(groupby1(df2.copy(), teamChosen2))

        st.write("Offensive Summary:")
        st.write(make_alt_barchart(df2.copy(), 'Offense', teamChosen2))
        # st.write(groupby2(df2.copy(), teamChosen2))
