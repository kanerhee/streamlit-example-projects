# singleplayer.py

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


def gettargets():

    def return_player(Player):

        nlist = Player.split(' ')
        newname = nlist[0][0] + '.' + nlist[1].upper()

        return newname

    dft = pd.read_html('https://www.fantasypros.com/nfl/reports/targets/')[0]
    dft['player'] = dft['Player'].apply(lambda x: return_player(x))
    dft = dft[['Player', 'player', 'Pos', 'Team', '1', '2', '3', '4', '5', '6', '7', '8', '9',
       '10', '11', '12', '13', '14', '15', '16', '17', 'TTL', 'AVG']]

    return dft[['Player', 'player', 'Pos', 'Team']]

def get_player_list(df):

    df['Description'] = df['Description'].astype(str)
    descriptions = list(set(df.Description))
    returnlist = []
    for description in descriptions:
        newlist = description.split(' ')
        for word in newlist:
            if '-' in word:
                returnlist.append(word)
    returnlist2 = list(set(returnlist))

    list2 = [x for x in returnlist2 if x[-1] != '.'] # get rid of trailing . duplicates

    defplayers = [x for x in returnlist2 if ('(' in x) or (')' in x)]
    offplayers = [x for x in returnlist2 if '(' not in x and ')' not in x and '[' not in x]
    offplayers = [x for x in offplayers if 'CENTER' not in x and 'HOLDER' not in x and 'HOU' not in x and 'ATL-' not in x
                 and 'MIN-' not in x and 'CAR-' not in x and 'LA-' not in x and 'TB-' not in x and 'LV-' not in x
                 and 'BAL-' not in x and 'NYJ-' not in x and 'NYG-' not in x and 'JAX-' not in x and 'TEN-' not in x
                 and 'GB-' not in x and 'DAL-' not in x and 'NE-' not in x and 'CLE-' not in x and 'NO-' not in x
                 and 'CHI-' not in x and 'KC-' not in x and 'SEA-' not in x and 'BUF-' not in x and 'PIT-' not in x
                 and 'DET-' not in x and 'MIA-' not in x and 'ARI-' not in x and 'LAC-' not in x and 'SF-' not in x
                 and 'IND-' not in x and 'PHI-' not in x and 'CIN-' not in x and 'DEN-' not in x and 'WAS-' not in x]
    offplayers = [x for x in offplayers if x[-1] != '.']
    offplayers = [x for x in offplayers if len(x) >=8]


    return offplayers

def makePlayerGroupby1(df1, dfprefiltered, playerChosen):

    dftwo = df1.copy().groupby(['Week', 'GameDate', 'Matchup']).agg({'Description':'count'}).reset_index()
    dftwo.drop(columns=['Description'], inplace=True)

    spine = pd.DataFrame({'Week':list(set(dfprefiltered.Week))})
    spine = pd.merge(spine, dftwo, on='Week', how='left')
    spine2 = spine.copy()
    spine['Type'] = 'PASS'
    spine2['Type'] = 'RUSH'

    newcoldict = {
        'IsIncomplete':'Incompletions',
        'IsFirst':'1sts',
        'Description': 'Attempts',
        'PlayType' : 'Attempts',
        'IsTouchdown': 'TDs',
        'Is2PTGood': '2PTs',
    }

    pt_list = ['PASS', 'RUSH'] #, 'SCRAMBLE', 'SACK', 'FUMBLES', 'KICK OFF', 'PUNT']
    tackle_name = '(' + playerChosen + ')'
    for pt in pt_list:

        df2 = df1.copy()
        df2 = df2[df2['PlayType'] == pt]
        df2 = df2[(df2['IsPenaltyAccepted'] == 0)]

        ncl = list(newcoldict.values())

        if pt == 'PASS':

            df2t = df2.copy().groupby(['Week', 'GameDate', 'PlayType']).agg({'IsIncomplete':'sum',
                                                                     'Description':'count',
                                                                     'Yards':'sum',
                                                                     'IsFirst':'sum',
                                                                     'IsTouchdown':'sum',
                                                                     'Is2PTGood':'sum'}).unstack().reset_index().fillna(0)
            df2t.rename(columns = newcoldict, inplace=True)
            mi = df2t.columns
            ind = pd.Index([e[0] for e in mi.tolist()])

            df2t.columns = ind
            for colm in ncl:
                if colm not in df2t:
                    df2t[colm] = 0

            df2t['Completions'] = df2t['Attempts'] - df2t['Incompletions']

            try:
                df2t['YPC'] = df2t['Yards'] / df2t['Completions']
                df2t['YPC'] = df2t['YPC'].round(2)
            except:
                df2t['Yards'] = '-'
                df2t['YPC'] = '-'

            df2t = df2t[['Week', 'Attempts', 'Completions', 'Yards', 'YPC', '1sts', 'TDs', '2PTs']]
            spine = pd.merge(spine, df2t, on='Week', how='left').fillna('-')

        if pt == 'RUSH':

            df2t = df2.copy().groupby(['Week', 'GameDate', 'PlayType']).agg({'IsFumble':'sum',
                                                                     'Description':'count',
                                                                     'Yards':'sum',
                                                                     'IsFirst':'sum',
                                                                     'IsTouchdown':'sum',
                                                                     'Is2PTGood':'sum'}).unstack().reset_index().fillna(0)
            df2t.rename(columns = newcoldict, inplace=True)
            mi = df2t.columns
            ind = pd.Index([e[0] for e in mi.tolist()])
            df2t.columns = ind

            for colm in ncl:
                if colm not in df2t:
                    df2t[colm] = 0

            df2t['Completions'] = 'n/a'
            try:
                df2t['YPC'] = df2t['Yards'] / df2t['Attempts']
                df2t['YPC'] = df2t['YPC'].round(2)
            except:
                df2t['Yards'] = '-'
                df2t['YPC'] = '-'

            df2t = df2t[['Week', 'Attempts', 'Completions', 'Yards', 'YPC', '1sts', 'TDs', '2PTs']]
            spine2 = pd.merge(spine2, df2t, on='Week', how='left').fillna('-')

    h = pd.concat([spine, spine2])
    h = h.groupby(['Type', 'Week', 'GameDate', 'Matchup']).agg({'Completions':'sum',
                                                        'Attempts':'sum',
                                                        'Yards':'sum',
                                                        'YPC':'max',
                                                        '1sts':'sum',
                                                        'TDs':'sum'})
    return h

def app():

    st.title('Single Player')
    st.write('by kanerhee')

    ####################################################################

    df = pd.read_csv('/home/ubuntu/streamlit-nfl/data/nflpbpdata.csv', low_memory='False')
    # df = pd.read_csv('/Users/kanerhee/Desktop/streamlit2/data/nflpbpdata.csv', low_memory='False')

    inilist = list(gettargets().player)
    AllPlayers = [x for x in get_player_list(df.copy()) if str(x) != 'nan']
    # AllFlexes = [x for x in AllPlayers if x in inilist]

    AllWeeks = [x for x in list(set(df.Week)) if str(x) != 'nan']

    PlayerChosen = st.selectbox("Choose Player", AllPlayers)
    if not PlayerChosen:
        st.error("Please select a player")

    # Filter - Weeks
    weeksChosen = st.multiselect("Choose Weeks", AllWeeks, AllWeeks)
    if not weeksChosen:
        st.error("Please select at least one week")

    df1 = df.copy()
    df1['Description'] = df1['Description'].astype(str)
    df1 = df1[df1['Description'].str.contains(PlayerChosen)]
    df1 = df1[df1.Week.isin(weeksChosen)]


    # get_player_list(df.copy())
    ####################################################################

    st.text('2020 Game Log:')
    st.write(makePlayerGroupby1(df1.copy(), df.copy(), PlayerChosen))

    st.text('Raw Data:')
    st.write(df1)
