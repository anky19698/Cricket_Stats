# All Imports

import pandas as pd
import requests
import zipfile
import io
import glob
import os
import numpy as np
import sqlite3

##################
# Bat vs Team    #
##################

ipl_df = pd.read_csv('all_ipl_data.csv')
t20i_df = pd.read_csv('all_t20i_data.csv')

df = pd.concat([ipl_df, t20i_df], ignore_index=True)

data1 = df.copy()

# Group By Columns

# Players Team
data1['played_for'] = data1['batting_team']

any_wicket = ['caught', 'bowled', 'run out', 'lbw', 'caught and bowled', 'stumped',
 'retired hurt', 'hit wicket', 'obstructing the field', 'retired out']

data1['player_out'] = data1['wicket_type'].apply(lambda x: 1 if x in any_wicket else 0)


runs_scored = data1.groupby(['striker', 'played_for', 'bowling_team', 'format'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = data1.groupby(['striker', 'played_for', 'bowling_team', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})

data1['player_got_out'] = data1['player_dismissed']
wickets_taken = data1.groupby(['player_got_out', 'played_for', 'bowling_team', 'format'])['player_dismissed'].count().reset_index()
wickets_taken['striker'] = wickets_taken['player_got_out']
wickets_taken.drop(columns=['player_got_out'], inplace=True)

innings = data1.groupby(['striker', 'played_for', 'bowling_team', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})


dots = data1.groupby(['striker', 'played_for', 'bowling_team', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = data1.groupby(['striker', 'played_for', 'bowling_team', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = data1.groupby(['striker', 'played_for', 'bowling_team', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})



# 50s and 100s

runs_per_innings = pd.DataFrame(data1.groupby(['striker', 'match_id', 'played_for', 'bowling_team', 'format'])['runs_off_bat'].sum().reset_index())
runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

fifties = pd.DataFrame(runs_per_innings.groupby(['striker', 'played_for', 'bowling_team', 'format'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
hundreds = pd.DataFrame(runs_per_innings.groupby(['striker', 'played_for', 'bowling_team', 'format'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})


# Merging all Columns

bat_vs_team = pd.merge(innings, runs_scored, on=['striker', 'played_for', 'bowling_team', 'format']).merge(
    balls_faced, on=['striker', 'played_for', 'bowling_team', 'format']).merge(
        wickets_taken, on=['striker', 'played_for', 'bowling_team', 'format']).merge(
            dots, on=['striker', 'played_for', 'bowling_team', 'format']).merge(
                fours, on=['striker', 'played_for', 'bowling_team', 'format']).merge(
                    sixes, on=['striker', 'played_for', 'bowling_team', 'format']).merge(
                        fifties, on=['striker', 'played_for', 'bowling_team', 'format']).merge(
                            hundreds, on=['striker', 'played_for', 'bowling_team', 'format']
                        )


# Additional Columns
bat_vs_team['batting_AVG'] = bat_vs_team.apply(lambda x: x['runs_scored'] if x['player_dismissed'] == 0 else x['runs_scored']/x['player_dismissed'], axis=1)
bat_vs_team['batting_SR'] = 100 * bat_vs_team['runs_scored'] / bat_vs_team['balls_faced']
bat_vs_team['dot_percentage'] = 100 * bat_vs_team['dots'] / bat_vs_team['balls_faced']

bat_vs_team = bat_vs_team[['striker', 'played_for', 'bowling_team', 'format', 'innings', 'runs_scored', 'balls_faced', 'dots', 'fours', 'sixes',
     'fifties', 'hundreds', 'batting_AVG', 'batting_SR', 'dot_percentage']]

# bat_vs_team.to_csv('bat_vs_team.csv', index=False)


##################
# Bat vs Venue   #
##################

data2 = df.copy()

data2['played_for'] = data2['batting_team']
# Group By Columns

dots = data2.groupby(['striker', 'played_for', 'stadium', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = data2.groupby(['striker', 'played_for', 'stadium', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = data2.groupby(['striker', 'played_for', 'stadium', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_scored = data2.groupby(['striker', 'played_for', 'stadium', 'format'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = data2.groupby(['striker', 'played_for', 'stadium', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
wickets_taken = data2.groupby(['striker', 'played_for', 'stadium', 'format'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = data2.groupby(['striker', 'played_for', 'stadium', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})


# 50s and 100s

runs_per_innings = pd.DataFrame(data2.groupby(['striker', 'match_id', 'played_for', 'stadium', 'format'])['runs_off_bat'].sum().reset_index())

runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

fifties = pd.DataFrame(runs_per_innings.groupby(['striker', 'played_for', 'stadium', 'format'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
hundreds = pd.DataFrame(runs_per_innings.groupby(['striker', 'played_for', 'stadium', 'format'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})


# Merging all Columns

bat_vs_venue = pd.merge(innings, runs_scored, on=['striker', 'played_for', 'stadium', 'format']).merge(
    balls_faced, on=['striker', 'played_for', 'stadium', 'format']).merge(
        wickets_taken, on=['striker', 'played_for', 'stadium', 'format']).merge(
            dots, on=['striker', 'played_for', 'stadium', 'format']).merge(
                fours, on=['striker', 'played_for', 'stadium', 'format']).merge(
                    sixes, on=['striker', 'played_for', 'stadium', 'format']).merge(
                        fifties, on=['striker', 'played_for', 'stadium', 'format']).merge(
                            hundreds, on=['striker', 'played_for', 'stadium', 'format']
                        )


# Additional Columns
bat_vs_venue['batting_AVG'] = bat_vs_venue.apply(lambda x: x['runs_scored'] if x['wickets_taken'] == 0 else x['runs_scored']/x['wickets_taken'], axis=1)
bat_vs_venue['batting_SR'] = 100 * bat_vs_venue['runs_scored'] / bat_vs_venue['balls_faced']
bat_vs_venue['dot_percentage'] = 100 * bat_vs_venue['dots'] / bat_vs_venue['balls_faced']

bat_vs_venue = bat_vs_venue[['striker', 'played_for', 'stadium', 'format', 'innings', 'runs_scored', 'balls_faced', 'dots', 'fours', 'sixes',
     'fifties', 'hundreds', 'batting_AVG', 'batting_SR', 'dot_percentage']]

# final_data[final_data['striker', 'played_for', 'format'] == 'V Kohli'].head(10)

# bat_vs_venue.to_csv('bat_vs_venue.csv', index=False)


##################
# Bat vs Bowl    #
##################

data3 = df.copy()

# 50s and 100s

runs_per_innings = pd.DataFrame(data3.groupby(['striker', 'match_id', 'format'])['runs_off_bat'].sum().reset_index())

runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

fifties = pd.DataFrame(runs_per_innings.groupby(['striker', 'format'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
hundreds = pd.DataFrame(runs_per_innings.groupby(['striker', 'format'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})

# Additional Columns

data3['is_dot'] = data3['runs_off_bat'].apply(lambda x: 1 if x == 0 else 0)
data3['is_one'] = data3['runs_off_bat'].apply(lambda x: 1 if x == 1 else 0)
data3['is_two'] = data3['runs_off_bat'].apply(lambda x: 1 if x == 2 else 0)
data3['is_three'] = data3['runs_off_bat'].apply(lambda x: 1 if x == 3 else 0)
data3['is_four'] = data3['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data3['is_six'] = data3['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

data3['bowlers_wicket'] = data3['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

bat_vs_ball = data3

# Additional Columns

dots = bat_vs_ball.groupby(['striker', 'bowler', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = bat_vs_ball.groupby(['striker', 'bowler', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = bat_vs_ball.groupby(['striker', 'bowler', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_scored = bat_vs_ball.groupby(['striker', 'bowler', 'format'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = bat_vs_ball.groupby(['striker', 'bowler', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
wickets_taken = bat_vs_ball.groupby(['striker', 'bowler', 'format'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = bat_vs_ball.groupby(['striker', 'bowler', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

matchup = pd.merge(innings, runs_scored, on=['striker', 'bowler', 'format']).merge(
    balls_faced, on=['striker', 'bowler', 'format']).merge(
        wickets_taken, on=['striker', 'bowler', 'format']).merge(
            dots, on=['striker', 'bowler', 'format']).merge(
                fours, on=['striker', 'bowler', 'format']).merge(
                    sixes, on=['striker', 'bowler', 'format'])

matchup['batting_SR'] = 100 * matchup['runs_scored'] / matchup['balls_faced']
matchup['dot_percentage'] = 100 * matchup['dots'] / matchup['balls_faced']
# matchup['inning_vs_dismissal'] = matchup['innings'] - matchup['wickets_taken']

# matchup.to_csv('matchups.csv', index=False)

##################
# Batting Record #
##################


data4 = df.copy()

data4['played_for'] = data4['batting_team']

# 50s and 100s

runs_per_innings = pd.DataFrame(data4.groupby(['striker', 'match_id', 'played_for', 'format'])['runs_off_bat'].sum().reset_index())

runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

fifties = pd.DataFrame(runs_per_innings.groupby(['striker', 'played_for', 'format'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
hundreds = pd.DataFrame(runs_per_innings.groupby(['striker', 'played_for', 'format'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})

# Additional Columns

data4['is_dot'] = data4['runs_off_bat'].apply(lambda x: 1 if x == 0 else 0)
data4['is_one'] = data4['runs_off_bat'].apply(lambda x: 1 if x == 1 else 0)
data4['is_two'] = data4['runs_off_bat'].apply(lambda x: 1 if x == 2 else 0)
data4['is_three'] = data4['runs_off_bat'].apply(lambda x: 1 if x == 3 else 0)
data4['is_four'] = data4['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data4['is_six'] = data4['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

data4['bowlers_wicket'] = data4['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

batting_record = data4

# Additional Columns

dots = batting_record.groupby(['striker', 'played_for', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = batting_record.groupby(['striker', 'played_for', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = batting_record.groupby(['striker', 'played_for', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_scored = batting_record.groupby(['striker', 'played_for', 'format'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = batting_record.groupby(['striker', 'played_for', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
wickets_taken = batting_record.groupby(['striker', 'played_for', 'format'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = batting_record.groupby(['striker', 'played_for', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

batting = pd.merge(innings, runs_scored, on=['striker', 'played_for', 'format']).merge(
    balls_faced, on=['striker', 'played_for', 'format']).merge(
        wickets_taken, on=['striker', 'played_for', 'format']).merge(
            dots, on=['striker', 'played_for', 'format']).merge(
                fours, on=['striker', 'played_for', 'format']).merge(
                    fifties, on=['striker', 'played_for', 'format']).merge(
                        hundreds, on=['striker', 'played_for', 'format']).merge(
                            sixes, on=['striker', 'played_for', 'format'])

batting['batting_SR'] = 100 * batting['runs_scored'] / batting['balls_faced']
batting['dot_percentage'] = 100 * batting['dots'] / batting['balls_faced']
batting['batting_AVG'] = batting['runs_scored'] / batting['wickets_taken']

batting = batting[['striker', 'played_for', 'format', 'innings', 'runs_scored', 'balls_faced', 'dots',
     'fours', 'fifties', 'hundreds', 'sixes', 'batting_SR', 'dot_percentage', 'batting_AVG']]

# batting.to_csv('batting_record.csv', index=False)


#########################
# Batting Record by Year#
#########################

data8 = df.copy()

data8['played_for'] = data8['batting_team']
# 50s and 100s

runs_per_innings = pd.DataFrame(data8.groupby(['striker', 'match_id', 'played_for', 'year', 'format'])['runs_off_bat'].sum().reset_index())

runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

fifties = pd.DataFrame(runs_per_innings.groupby(['striker', 'played_for', 'year', 'format'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
hundreds = pd.DataFrame(runs_per_innings.groupby(['striker', 'played_for', 'year', 'format'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})

# Additional Columns

data8['is_dot'] = data8['runs_off_bat'].apply(lambda x: 1 if x == 0 else 0)
data8['is_one'] = data8['runs_off_bat'].apply(lambda x: 1 if x == 1 else 0)
data8['is_two'] = data8['runs_off_bat'].apply(lambda x: 1 if x == 2 else 0)
data8['is_three'] = data8['runs_off_bat'].apply(lambda x: 1 if x == 3 else 0)
data8['is_four'] = data8['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data8['is_six'] = data8['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

data8['bowlers_wicket'] = data8['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

batting_record_by_year = data8

# Additional Columns

dots = batting_record_by_year.groupby(['striker', 'played_for', 'year', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = batting_record_by_year.groupby(['striker', 'played_for', 'year', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = batting_record_by_year.groupby(['striker', 'played_for', 'year', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_scored = batting_record_by_year.groupby(['striker', 'played_for', 'year', 'format'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = batting_record_by_year.groupby(['striker', 'played_for', 'year', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
wickets_taken = batting_record_by_year.groupby(['striker', 'played_for', 'year', 'format'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = batting_record_by_year.groupby(['striker', 'played_for', 'year', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

batting_by_year = pd.merge(innings, runs_scored, on=['striker', 'played_for', 'year', 'format']).merge(
    balls_faced, on=['striker', 'played_for', 'year', 'format']).merge(
        wickets_taken, on=['striker', 'played_for', 'year', 'format']).merge(
            dots, on=['striker', 'played_for', 'year', 'format']).merge(
                fours, on=['striker', 'played_for', 'year', 'format']).merge(
                    fifties, on=['striker', 'played_for', 'year', 'format']).merge(
                        hundreds, on=['striker', 'played_for', 'year', 'format']).merge(
                            sixes, on=['striker', 'played_for', 'year', 'format'])

batting_by_year['batting_SR'] = 100 * batting_by_year['runs_scored'] / batting_by_year['balls_faced']
batting_by_year['dot_percentage'] = 100 * batting_by_year['dots'] / batting_by_year['balls_faced']
batting_by_year['batting_AVG'] = batting_by_year['runs_scored'] / batting_by_year['wickets_taken']

batting_by_year = batting_by_year[['striker', 'played_for', 'year', 'format', 'innings', 'runs_scored', 'balls_faced', 'dots',
     'fours', 'fifties', 'hundreds', 'sixes', 'batting_SR', 'dot_percentage', 'batting_AVG']]

#########################
# Batting Record by Innings #
#########################

data10 = df.copy()

data10['played_for'] = data10['batting_team']

# Additional Columns

data10['is_dot'] = data10['runs_off_bat'].apply(lambda x: 1 if x == 0 else 0)
data10['is_one'] = data10['runs_off_bat'].apply(lambda x: 1 if x == 1 else 0)
data10['is_two'] = data10['runs_off_bat'].apply(lambda x: 1 if x == 2 else 0)
data10['is_three'] = data10['runs_off_bat'].apply(lambda x: 1 if x == 3 else 0)
data10['is_four'] = data10['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data10['is_six'] = data10['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

any_wicket = ['caught', 'bowled', 'run out', 'lbw', 'caught and bowled', 'stumped',
 'retired hurt', 'hit wicket', 'obstructing the field', 'retired out']

data10['player_out'] = data10['wicket_type'].apply(lambda x: 1 if x in any_wicket else 0)

batting_record_by_innings = data10
# Additional Columns

dots = batting_record_by_innings.groupby(['striker', 'played_for', 'bowling_team', 'start_date', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = batting_record_by_innings.groupby(['striker', 'played_for', 'bowling_team', 'start_date', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = batting_record_by_innings.groupby(['striker', 'played_for', 'bowling_team', 'start_date', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_scored = batting_record_by_innings.groupby(['striker', 'played_for', 'bowling_team', 'start_date', 'format'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = batting_record_by_innings.groupby(['striker', 'played_for', 'bowling_team', 'start_date', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
player_out = batting_record_by_innings.groupby(['striker', 'played_for', 'bowling_team', 'start_date', 'format'])['player_out'].sum().reset_index()
innings = batting_record_by_innings.groupby(['striker', 'played_for', 'bowling_team', 'start_date', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})


batting_by_innings = pd.merge(innings, runs_scored, on=['striker', 'played_for', 'bowling_team', 'start_date', 'format']).merge(
    balls_faced, on=['striker', 'played_for', 'bowling_team', 'start_date', 'format']).merge(
        player_out, on=['striker', 'played_for', 'bowling_team', 'start_date', 'format']).merge(
            dots, on=['striker', 'played_for', 'bowling_team', 'start_date', 'format']).merge(
                fours, on=['striker', 'played_for', 'bowling_team', 'start_date', 'format']).merge(
                    sixes, on=['striker', 'played_for', 'bowling_team', 'start_date', 'format'])

batting_by_innings['batting_SR'] = 100 * batting_by_innings['runs_scored'] / batting_by_innings['balls_faced']
batting_by_innings['dot_percentage'] = 100 * batting_by_innings['dots'] / batting_by_innings['balls_faced']

batting_by_innings = batting_by_innings.sort_values(by='start_date', ascending=False)

batting_by_innings['player_dismissed'] = batting_by_innings['player_out'].apply(lambda x: 'Yes' if x == 1 else 'No')

batting_by_innings = batting_by_innings[['striker', 'played_for', 'bowling_team', 'start_date', 'runs_scored',
       'balls_faced', 'player_dismissed', 'dots', 'fours', 'sixes', 'batting_SR',
       'dot_percentage']]

# print(batting_by_innings.columns)





##################
# Bowling Record #
##################


data5 = df.copy()

data5['played_for'] = data5['bowling_team']

data5['is_four'] = data5['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data5['is_six'] = data5['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

data5['total_runs'] = data5['runs_off_bat'] + data5['extras']

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

data5['bowlers_wicket'] = data5['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

bowling_record = data5

# Additional Columns

dots = bowling_record.groupby(['bowler', 'played_for', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = bowling_record.groupby(['bowler', 'played_for', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = bowling_record.groupby(['bowler', 'played_for', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_conceded = bowling_record.groupby(['bowler', 'played_for', 'format'])['total_runs'].sum().reset_index().rename(columns={'total_runs': 'runs_conceded'})
balls_bowled = bowling_record.groupby(['bowler', 'played_for', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_bowled'})
wickets_taken = bowling_record.groupby(['bowler', 'played_for', 'format'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = bowling_record.groupby(['bowler', 'played_for', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

bowling = pd.merge(innings, runs_conceded, on=['bowler', 'played_for', 'format']).merge(
    balls_bowled, on=['bowler', 'played_for', 'format']).merge(
        wickets_taken, on=['bowler', 'played_for', 'format']).merge(
            dots, on=['bowler', 'played_for', 'format']).merge(
                fours, on=['bowler', 'played_for', 'format']).merge(
                    sixes, on=['bowler', 'played_for', 'format'])

bowling['Economy'] = 6 * bowling['runs_conceded'] / bowling['balls_bowled']
bowling['bowling_AVG'] = bowling['runs_conceded'] / bowling['wickets_taken']


# bowling.to_csv('bowling_record.csv', index=False)


############################
# Bowling Record by Season #
############################


data7 = df.copy()

data7['played_for'] = data7['bowling_team']

data7['is_four'] = data7['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data7['is_six'] = data7['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

data7['total_runs'] = data7['runs_off_bat'] + data7['extras']

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

data7['bowlers_wicket'] = data7['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

bowling_record_by_year = data7

# Additional Columns

dots = bowling_record_by_year.groupby(['bowler', 'played_for', 'year', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = bowling_record_by_year.groupby(['bowler', 'played_for', 'year', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = bowling_record_by_year.groupby(['bowler', 'played_for', 'year', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_conceded = bowling_record_by_year.groupby(['bowler', 'played_for', 'year', 'format'])['total_runs'].sum().reset_index().rename(columns={'total_runs': 'runs_conceded'})
balls_bowled = bowling_record_by_year.groupby(['bowler', 'played_for', 'year', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_bowled'})
wickets_taken = bowling_record_by_year.groupby(['bowler', 'played_for', 'year', 'format'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = bowling_record_by_year.groupby(['bowler', 'played_for', 'year', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

bowling_by_year = pd.merge(innings, runs_conceded, on=['bowler', 'played_for', 'year', 'format']).merge(
    balls_bowled, on=['bowler', 'played_for', 'year', 'format']).merge(
        wickets_taken, on=['bowler', 'played_for', 'year', 'format']).merge(
            dots, on=['bowler', 'played_for', 'year', 'format']).merge(
                fours, on=['bowler', 'played_for', 'year', 'format']).merge(
                    sixes, on=['bowler', 'played_for', 'year', 'format'])

bowling_by_year['Economy'] = 6 * bowling_by_year['runs_conceded'] / bowling_by_year['balls_bowled']
bowling_by_year['bowling_AVG'] = bowling_by_year['runs_conceded'] / bowling_by_year['wickets_taken']



############################
# Bowling Record by Innings#
############################
# df = pd.read_csv('all_ipl_data.csv')

data9 = df.copy()

data9['played_for'] = data9['bowling_team']

data9['is_four'] = data9['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data9['is_six'] = data9['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

data9['total_runs'] = data9['runs_off_bat'] + data9['extras']

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

data9['bowlers_wicket'] = data9['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

bowling_record_by_innings = data9

# Additional Columns

dots = bowling_record_by_innings.groupby(['bowler', 'played_for', 'batting_team', 'start_date', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = bowling_record_by_innings.groupby(['bowler', 'played_for', 'batting_team', 'start_date', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = bowling_record_by_innings.groupby(['bowler', 'played_for', 'batting_team', 'start_date', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_conceded = bowling_record_by_innings.groupby(['bowler', 'played_for', 'batting_team', 'start_date', 'format'])['total_runs'].sum().reset_index().rename(columns={'total_runs': 'runs_conceded'})
balls_bowled = bowling_record_by_innings.groupby(['bowler', 'played_for', 'batting_team', 'start_date', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_bowled'})
wickets_taken = bowling_record_by_innings.groupby(['bowler', 'played_for', 'batting_team', 'start_date', 'format'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = bowling_record_by_innings.groupby(['bowler', 'played_for', 'batting_team', 'start_date', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index()

bowling_by_innings = pd.merge(innings, runs_conceded, on=['bowler', 'played_for', 'batting_team', 'start_date', 'format']).merge(
    balls_bowled, on=['bowler', 'played_for', 'batting_team', 'start_date', 'format']).merge(
        wickets_taken, on=['bowler', 'played_for', 'batting_team', 'start_date', 'format']).merge(
            dots, on=['bowler', 'played_for', 'batting_team', 'start_date', 'format']).merge(
                fours, on=['bowler', 'played_for', 'batting_team', 'start_date', 'format']).merge(
                    sixes, on=['bowler', 'played_for', 'batting_team', 'start_date', 'format'])

bowling_by_innings['Economy'] = 6 * bowling_by_innings['runs_conceded'] / bowling_by_innings['balls_bowled']
bowling_by_innings['bowling_AVG'] = bowling_by_innings['runs_conceded'] / bowling_by_innings['wickets_taken']

bowling_by_innings = bowling_by_innings.sort_values(by='start_date', ascending=False)

bowling_by_innings = bowling_by_innings[['bowler', 'played_for', 'batting_team', 'start_date', 'format', 'runs_conceded',
       'balls_bowled', 'wickets_taken', 'dots', 'Economy']]



############################
# Bowler vs Team           #
############################
# df = pd.read_csv('all_ipl_data.csv')

data11 = df.copy()

data11['played_for'] = data11['bowling_team']

data11['is_four'] = data11['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data11['is_six'] = data11['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

data11['total_runs'] = data11['runs_off_bat'] + data11['extras']

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

data11['bowlers_wicket'] = data11['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

bowl_vs_team = data11

# Additional Columns

dots = bowl_vs_team.groupby(['bowler', 'played_for', 'batting_team', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = bowl_vs_team.groupby(['bowler', 'played_for', 'batting_team', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = bowl_vs_team.groupby(['bowler', 'played_for', 'batting_team', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_conceded = bowl_vs_team.groupby(['bowler', 'played_for', 'batting_team', 'format'])['total_runs'].sum().reset_index().rename(columns={'total_runs': 'runs_conceded'})
balls_bowled = bowl_vs_team.groupby(['bowler', 'played_for', 'batting_team', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_bowled'})
wickets_taken = bowl_vs_team.groupby(['bowler', 'played_for', 'batting_team', 'format'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = bowl_vs_team.groupby(['bowler', 'played_for', 'batting_team', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index()

bowler_vs_team = pd.merge(innings, runs_conceded, on=['bowler', 'played_for', 'batting_team', 'format']).merge(
    balls_bowled, on=['bowler', 'played_for', 'batting_team', 'format']).merge(
        wickets_taken, on=['bowler', 'played_for', 'batting_team', 'format']).merge(
            dots, on=['bowler', 'played_for', 'batting_team', 'format']).merge(
                fours, on=['bowler', 'played_for', 'batting_team', 'format']).merge(
                    sixes, on=['bowler', 'played_for', 'batting_team', 'format'])

bowler_vs_team['Economy'] = 6 * bowler_vs_team['runs_conceded'] / bowler_vs_team['balls_bowled']
bowler_vs_team['bowling_AVG'] = bowler_vs_team['runs_conceded'] / bowler_vs_team['wickets_taken']


bowler_vs_team = bowler_vs_team[['bowler', 'played_for', 'batting_team', 'format', 'runs_conceded',
       'balls_bowled', 'wickets_taken', 'dots', 'Economy']]




############################
# Bowler vs Venue          #
############################
# df = pd.read_csv('all_ipl_data.csv')

data12 = df.copy()

data12['played_for'] = data12['bowling_team']

data12['is_four'] = data12['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data12['is_six'] = data12['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

data12['total_runs'] = data12['runs_off_bat'] + data12['extras']

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

data12['bowlers_wicket'] = data12['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

bowl_vs_venue = data12

# Additional Columns

dots = bowl_vs_venue.groupby(['bowler', 'played_for', 'stadium', 'format'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = bowl_vs_venue.groupby(['bowler', 'played_for', 'stadium', 'format'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = bowl_vs_venue.groupby(['bowler', 'played_for', 'stadium', 'format'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_conceded = bowl_vs_venue.groupby(['bowler', 'played_for', 'stadium', 'format'])['total_runs'].sum().reset_index().rename(columns={'total_runs': 'runs_conceded'})
balls_bowled = bowl_vs_venue.groupby(['bowler', 'played_for', 'stadium', 'format'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_bowled'})
wickets_taken = bowl_vs_venue.groupby(['bowler', 'played_for', 'stadium', 'format'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = bowl_vs_venue.groupby(['bowler', 'played_for', 'stadium', 'format'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index()

bowler_vs_venue = pd.merge(innings, runs_conceded, on=['bowler', 'played_for', 'stadium', 'format']).merge(
    balls_bowled, on=['bowler', 'played_for', 'stadium', 'format']).merge(
        wickets_taken, on=['bowler', 'played_for', 'stadium', 'format']).merge(
            dots, on=['bowler', 'played_for', 'stadium', 'format']).merge(
                fours, on=['bowler', 'played_for', 'stadium', 'format']).merge(
                    sixes, on=['bowler', 'played_for', 'stadium', 'format'])

bowler_vs_venue['Economy'] = 6 * bowler_vs_venue['runs_conceded'] / bowler_vs_venue['balls_bowled']
bowler_vs_venue['bowling_AVG'] = bowler_vs_venue['runs_conceded'] / bowler_vs_venue['wickets_taken']

bowler_vs_venue = bowler_vs_venue[['bowler', 'played_for', 'stadium', 'format', 'runs_conceded',
       'balls_bowled', 'wickets_taken', 'dots', 'Economy']]



######################
# Adding to Database #
######################


# Connect to SQLite Database
def connect_to_database(database_name):
    return sqlite3.connect(database_name)


# Create Table
def create_table(conn, table_name, columns):
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")


# Insert Data into Database
def insert_data(conn, table_name, data):
    data.to_sql(table_name, conn, if_exists='append', index=False)


# Query Database
def query_database(conn, query):
    return pd.read_sql_query(query, conn)


# csv_files = ['bat_vs_venue.csv', 'bat_vs_team.csv', 'matchups.csv', 'batting_record.csv', 'bowling_record.csv']
dataframes = [bat_vs_venue, bat_vs_team, matchup, batting, bowling, batting_by_year, bowling_by_year, batting_by_innings, bowling_by_innings, bowler_vs_team, bowler_vs_venue]
table_names = ['batter_vs_venue', 'batter_vs_team', 'batter_vs_bowler', 'batting_record', 'bowling_record', 'batting_record_by_year', 'bowling_record_by_year', 'batting_record_by_innings', 'bowling_record_by_innings', 'bowler_vs_team', 'bowler_vs_venue']
table_columns = [
    ['striker', 'played_for', 'stadium', 'format', 'innings', 'runs_scored', 'balls_faced', 'dots', 'fours', 'sixes',
     'fifties', 'hundreds', 'batting_AVG', 'batting_SR', 'dot_percentage'],  # Columns for batter_vs_venue
    ['striker', 'played_for', 'bowling_team', 'format', 'innings', 'runs_scored', 'balls_faced', 'dots', 'fours', 'sixes',
     'fifties', 'hundreds', 'batting_AVG', 'batting_SR', 'dot_percentage'],  # Columns for batter_vs_team
    ['striker', 'bowler', 'format', 'innings', 'runs_scored', 'balls_faced', 'wickets_taken', 'dots', 'fours', 'sixes',
     'batting_SR', 'dot_percentage', 'inning_vs_dismissal'],  # Columns for batter_vs_bowler
    ['striker', 'played_for', 'format', 'innings', 'runs_scored', 'balls_faced', 'dots',
     'fours', 'fifties', 'hundreds', 'sixes', 'batting_SR', 'dot_percentage', 'batting_AVG'], # Columns for batting_record
    ['bowler', 'played_for', 'format', 'innings', 'runs_conceded', 'balls_bowled', 'wickets_taken',
     'dots', 'fours', 'sixes', 'Economy', 'bowling_AVG'], # Columns for bowling_record
    ['striker', 'played_for', 'year', 'format', 'innings', 'runs_scored', 'balls_faced', 'dots',
     'fours', 'fifties', 'hundreds', 'sixes', 'batting_SR', 'dot_percentage', 'batting_AVG'], # Columns for batting_record_by_year
    ['bowler', 'played_for', 'year', 'format', 'innings', 'runs_conceded', 'balls_bowled', 'wickets_taken',
     'dots', 'fours', 'sixes', 'Economy', 'bowling_AVG'],  # Columns for bowling_record_by_year
    ['striker', 'played_for', 'bowling_team', 'start_date', 'format', 'runs_scored',
     'balls_faced', 'player_dismissed', 'dots', 'fours', 'sixes', 'batting_SR',
     'dot_percentage'], # Columns for batting_record_by_innings
    ['bowler', 'played_for', 'batting_team', 'start_date', 'format', 'runs_conceded',
    'balls_bowled', 'wickets_taken', 'dots', 'Economy'], # Columns for bowling_record_by_innings
    ['bowler', 'played_for', 'batting_team', 'format', 'runs_conceded',
       'balls_bowled', 'wickets_taken', 'dots', 'Economy'], # Columns for bowler vs team
    ['bowler', 'played_for', 'stadium', 'format', 'runs_conceded',
       'balls_bowled', 'wickets_taken', 'dots', 'Economy'] # Columns for bowler vs venue

]

# Connect to SQLite Database
conn = connect_to_database('cricket_database.db')

# Iterate over CSV files
for dataframe, table_name, columns in zip(dataframes, table_names, table_columns):
    # Read CSV data
    csv_data = dataframe.copy()

    # Create table
    create_table(conn, table_name, columns)

    # Insert data into table
    insert_data(conn, table_name, csv_data)



# Close database connection
conn.close()
