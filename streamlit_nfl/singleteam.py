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
        width=700,
        height=300
    )

    return a


def gb1(df, offordef, tc):

    df2 = df.copy()

    if offordef == 'Offense':
        df2 = df2[df2['Offense'].isin(tc)]
    if offordef == 'Defense':
        df2 = df2[df2['Defense'].isin(tc)]

    return df2


def gb2(df, offordef, tc):

    df2 = df.copy()

    if offordef == 'Offense':
        df2 = df2[df2['Offense'].isin(tc)]
    if offordef == 'Defense':
        df2 = df2[df2['Defense'].isin(tc)]

    # df2.rename(columns={'Yards':'week'}, inplace=True)
    df2 = df2.groupby(['Offense', 'Week']).agg({'Yards':'sum'}).unstack().fillna(0.0)

    x = 0
    df2['Total'] = 0
    while x < (df2.shape[1]-1):
        df2['Total'] = df2['Total'] + df2.iloc[:,x]
        x += 1
    df2['Average'] = (df2['Total'] / (df2.shape[1]-1)).astype(int)

    return df2


def rushtypes(df, offordef, tc):

    df2 = df.copy()

    if offordef == 'Offense':
        df2 = df2[df2['Offense'].isin(tc)]
    if offordef == 'Defense':
        df2 = df2[df2['Defense'].isin(tc)]

    df2 = df2[df2['IsRush'] == 1]
    # df2.rename(columns={'Yards':'week'}, inplace=True)
    df2 = df2.groupby(['Offense', 'RushDirection', 'Week']).agg({'Yards':'sum'}).unstack().fillna(0.0)

    x = 0
    df2['Total'] = 0
    while x < (df2.shape[1]-1):
        df2['Total'] = df2['Total'] + df2.iloc[:,x]
        x += 1
    print(df2.shape[1]-1)
    df2['Average'] = ( df2['Total'] / ((df2.shape[1]-1)) ).astype(int)

    df2 = df2.append(df2.sum().rename('Total')).assign(Total=lambda d: d.sum(1))

    return df2


def passtypes(df, offordef, tc):

    df2 = df.copy()

    if offordef == 'Offense':
        df2 = df2[df2['Offense'].isin(tc)]
    if offordef == 'Defense':
        df2 = df2[df2['Defense'].isin(tc)]

    df2 = df2[df2['IsPass'] == 1]
    # df2.rename(columns={'Yards':'week'}, inplace=True)
    df2 = df2.groupby(['Offense', 'PassType', 'Week']).agg({'Yards':'sum'}).unstack().fillna(0.0)

    x = 0
    df2['Total'] = 0
    while x < (df2.shape[1]-1):
        df2['Total'] = df2['Total'] + df2.iloc[:,x]
        x += 1
    df2['Average'] = (df2['Total'] / (df2.shape[1]-1)).astype(int)

    df2 = df2.append(df2.sum().rename('Total')).assign(Total=lambda d: d.sum(1))

    return df2

def app():

    st.text('Note: this has bugs')
    st.title('Offense')
    st.write('by kanerhee')

    ####################################################################

    df = pd.read_csv('/home/ubuntu/streamlit-nfl/data/nflpbpdata.csv', low_memory='False')
    # df = pd.read_csv('/Users/kanerhee/Desktop/streamlit2/data/nflpbpdata.csv', low_memory='False')

    AllTeams = [x for x in list(set(df.Offense)) if str(x) != 'nan']
    AllWeeks = [x for x in list(set(df.Week)) if str(x) != 'nan']

    # Filter 1 - Teams
    teamChosen = st.multiselect("Choose Team", AllTeams)
    if len(teamChosen) > 1:
        st.error("Max team limit: 1")

    # Filter 2 - Weeks
    weeksChosen = st.multiselect("Choose Weeks", AllWeeks, AllWeeks)
    if not weeksChosen:
        st.error("Please select at least one week")

    df = df[df.Offense.isin(teamChosen) | df.Defense.isin(teamChosen)]
    df = df[df.Week.isin(weeksChosen)]

    df.drop(columns=['Unnamed: 0'], inplace=True)

    ####################################################################

    st.title('Offense:')
    st.subheader('Total Yards')
    st.write(make_alt_barchart(df.copy(), 'Offense', teamChosen))

    st.title('Defense:')
    st.subheader('Total Yards Allowed')
    st.write(make_alt_barchart(df.copy(), 'Defense', teamChosen))


    st.title('Crosstabs: ')
    st.subheader('Rush Types: ')
    st.write(passtypes(df.copy(), 'Offense', teamChosen))
    st.subheader('Pass Types: ')
    st.write(rushtypes(df.copy(), 'Offense', teamChosen))

    st.title('Raw Data:')
    st.header('Offense')
    st.write(gb1(df.copy(), 'Offense', teamChosen))
    st.header('Defense')
    st.write(gb1(df.copy(), 'Defense', teamChosen))
