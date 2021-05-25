# Author: Kane Rhee
# Shoutsout to Darren Willman

def display(*args):
    html_str=''
    for df in args:
        html_str+=df.to_html()
    display_html(html_str.replace('table','table style="display:inline"'),raw=True)

def show_all_games(dfm):

    def organize(x):
        a = x.split('-')
        a.sort()
        b = '-'.join(a)
        return b

    df = dfm.copy()
    df = df[['Week', 'GameId', 'GameDate', 'Offense', 'Defense']].dropna()
    df['Matchup'] = (df['Offense'] + '-' + df['Defense']).apply(lambda x: organize(x))
    df.drop(columns=['Offense', 'Defense'], inplace=True)
    df.sort_values(by=['GameDate'], inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def pull_master_df():

    url = 'http://nflsavant.com/pbp_data.php?year=2020'

    r = requests.post(url)
    if r.ok:
        data = r.content.decode('utf8')
        df = pd.read_csv(io.StringIO(data))
        df.GameDate = pd.to_datetime(df.GameDate).dt.normalize()

    game_id_list = list(set(df.GameId))
    game_dict = {}
    for game_id in game_id_list:
        df2 = df.copy()
        df2 = df2[df2['GameId'] == game_id]
        game_dict[game_id] = df2.copy()

    print('Done. Pulled ', len(game_dict.keys()), 'unique GameIDs')

    def make_week_dict(dfm):

        df = dfm.copy()
        game_id_list = set(list(df.GameId))
        game_date_list = list(set(df.GameDate))
        game_date_list.sort()
        w1 = game_date_list[0]

        blank = {1:w1}

        x=1
        while x < 18:
            blank[x+1] = blank[x]+timedelta(days=7)
            x += 1

        return blank

    global weekdict
    weekdict = make_week_dict(df)

    def return_week_index(date):

        indexlist = list(weekdict.keys())
        weeklist = list(weekdict.values())

        x = 1
        while x < len(indexlist):
            if (weekdict[x] <= date) & (date < weekdict[x+1]):
                return indexlist[x-1]
            x += 1

    df['WeekIndex'] = df['GameDate'].apply(lambda x: return_week_index(x))

    if 'Unnamed: 10' in df:
        df.drop(columns=['Unnamed: 10', 'Unnamed: 12', 'Unnamed: 16', 'Unnamed: 17', 'SeasonYear'], inplace=True)
        df.rename(columns={'OffenseTeam':'Offense',
                           'DefenseTeam':'Defense',
                          'IsTwoPointConversion':'Is2PT',
                          'IsTwoPointConversionSuccessful':'Is2PTGood',
                          'WeekIndex':'Week',
                          'SeriesFirstDown':'IsFirst'}, inplace=True)

    ####################################################################################

    def assign_all_players(x):
        def convert(lst):
            return ' '.join(lst)
        some_list = x.split(' ')
        players_in = []
        for some in some_list:
            if '-' in some:
                if '.' in some:
                    players_in.append(some)
        return convert(players_in)

    ####################################################################################

#     mi = df.copy()[['GameId', 'Week', 'GameDate', 'Quarter',
#                     'Minute', 'Second', 'Offense', 'Defense',
#                     'Description', 'Formation', 'PlayType', 'IsRush',
#                     'IsPass', 'RushDirection', 'Yards']]
    mi = df.copy()
    mi['Players'] = mi['Description'].apply(lambda x: assign_all_players(x))

    def assign_def(x):
        def convert(lst):
            return ' '.join(lst)
        some_list = x.split(' ')
        players_in = []
        for some in some_list:
            if '(' in some:
                if '.' in some:
                    players_in.append(some)
        return convert(players_in)

    def assign_off(x):
        def convert(lst):
            return ' '.join(lst)
        some_list = x.split(' ')
        players_in = []
        for some in some_list:
            if '(' not in some:
                if '.' in some:
                    players_in.append(some)
        return convert(players_in)


    mi['DPlayers'] = mi['Players'].apply(lambda x: assign_def(x))
    mi['Oplayers'] = mi['Players'].apply(lambda x: assign_off(x))

    #####################################################################################

    def assign_rusher(x):
        some_list = x.split(' ')
        return some_list[0]

    mi['rusher'] = 'n'
    mi0 = mi.copy()
    mi0 = mi0[mi0['IsRush'] == 0]
    mi0['rusher'] = 'n'
    mi1 = mi.copy()
    mi1 = mi1[mi1['IsRush'] == 1]
    mi1['rusher'] = mi['Oplayers'].apply(lambda x: assign_rusher(x))
    mi3 = pd.concat([mi0, mi1])

    wi = mi3.copy()

    def assign_passer(x):
        some_list = x.split(' ')
        return some_list[0]

    wi['passer'] = 'n'
    wi0 = wi.copy()
    wi0 = wi0[wi0['IsPass'] == 0]
    mi0['passer'] = 'n'
    wi1 = wi.copy()
    wi1 = wi1[wi1['IsPass'] == 1]
    wi1['passer'] = wi1['Oplayers'].apply(lambda x: assign_passer(x))
    wi3 = pd.concat([wi0, wi1])


    def sort_play_order(df):

        game_id_list = list(set(df.GameId))
        quarter_list = [1,2,3,4]
        blank = []

        for game_id in game_id_list:
            df2 = df.copy()[df.copy().GameId == game_id]
            df2 = df2.sort_values(by=['Quarter'])
            df_list = []

            for quarter in quarter_list:
                df3 = df2.copy()[df2.copy().Quarter == quarter]
                df3 = df3.sort_values(by=['Minute', 'Second'], ascending = False)
                df_list.append(df3)

#             df4 = pd.concat(df_list)
            blank.append(pd.concat(df_list))

        return pd.concat(blank)

    df = sort_play_order(wi3.copy())
    m = df.copy()

    gameID_lookup = show_all_games(df.copy())
    gmap = gameID_lookup.copy()[['GameId', 'Matchup']].to_dict()
    g = gameID_lookup.copy()[['GameId', 'Matchup']]

    game_ids = list(g.GameId)
    matchups = list(g.Matchup)
    res = {game_ids[i]: matchups[i] for i in range(len(matchups))}

    m['GAMEID'] = m['GameId']
    m.replace({'GAMEID': res}, inplace=True)
    m.rename(columns={'GAMEID':'Matchup'}, inplace=True)
    df = m.copy()

    df['RushingYards'] = df['IsRush']*df['Yards']
    df['PassingYards'] = df['IsPass']*df['Yards']

    return game_dict, gameID_lookup, df[['GameId', 'Matchup', 'Week', 'GameDate', 'Quarter', 'Minute', 'Second', 'Offense',
       'Defense', 'Down', 'ToGo', 'YardLine', 'Yards', 'IsFirst', 'NextScore',
       'Description', 'TeamWin', 'Formation', 'PlayType', 'IsRush',
       'IsPass', 'RushDirection', 'RushingYards', 'PassType', 'PassingYards',
       'IsIncomplete', 'IsTouchdown', 'IsSack', 'IsChallenge',
       'IsChallengeReversed', 'Challenger', 'IsMeasurement', 'IsInterception',
       'IsFumble', 'IsPenalty', 'Is2PT', 'Is2PTGood',
       'YardLineFixed', 'YardLineDirection', 'IsPenaltyAccepted',
       'PenaltyTeam', 'IsNoPlay', 'PenaltyType', 'PenaltyYards',
        'Players', 'DPlayers', 'Oplayers', 'rusher', 'passer', ]]

def get_team(df, teamstring):

    df2 = df.copy()
    df2 = df2[df2['Matchup'].str.contains(teamstring)]
    df2['GameDate2'] = df2['GameDate'].astype(str) + '-Q' + df2['Quarter'].astype(str)
    mid = df2['GameDate2']
    df2.drop(labels=['GameDate2'], axis=1, inplace = True)
    df2.insert(1, 'GameDate2', mid)

    df2['Focus'] = str(teamstring)
    mid = df2['Focus']
    df2.drop(labels=['Focus'], axis=1, inplace = True)
    df2.insert(1, 'Focus', mid)

    return df2

import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime, timedelta
import requests
import matplotlib
import io

# using matplotlib and seaborn
import matplotlib.pyplot as plt
import seaborn as sns

# The magic code for viewing plots using jupyter notebooks:
%matplotlib inline

# Display All (best used in notebooks)
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# pull all the data
game_dict, df_lookup, dfm = pull_master_df()

df = dfm.copy()
df.to_csv('nflpbpdata.csv')

# displayo(df.head(2), df_lookup)

print(df)

print('Done: Pulled ', len(df), ' rows.')
