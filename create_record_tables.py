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

df = pd.read_csv('all_ipl_data.csv')

data1 = df.copy()

# Group By Columns

runs_scored = data1.groupby(['striker', 'bowling_team'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = data1.groupby(['striker', 'bowling_team'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
wickets_taken = data1.groupby(['striker', 'bowling_team'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = data1.groupby(['striker', 'bowling_team'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})


dots = data1.groupby(['striker', 'bowling_team'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = data1.groupby(['striker', 'bowling_team'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = data1.groupby(['striker', 'bowling_team'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})



# 50s and 100s

runs_per_innings = pd.DataFrame(data1.groupby(['striker', 'match_id', 'bowling_team'])['runs_off_bat'].sum().reset_index())
runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

fifties = pd.DataFrame(runs_per_innings.groupby(['striker', 'bowling_team'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
hundreds = pd.DataFrame(runs_per_innings.groupby(['striker', 'bowling_team'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})


# Merging all Columns

bat_vs_team = pd.merge(innings, runs_scored, on=['striker', 'bowling_team']).merge(
    balls_faced, on=['striker', 'bowling_team']).merge(
        wickets_taken, on=['striker', 'bowling_team']).merge(
            dots, on=['striker', 'bowling_team']).merge(
                fours, on=['striker', 'bowling_team']).merge(
                    sixes, on=['striker', 'bowling_team']).merge(
                        fifties, on=['striker', 'bowling_team']).merge(
                            hundreds, on=['striker', 'bowling_team']
                        )


# Additional Columns
bat_vs_team['batting_AVG'] = bat_vs_team.apply(lambda x: x['runs_scored'] if x['wickets_taken'] == 0 else x['runs_scored']/x['wickets_taken'], axis=1)
bat_vs_team['batting_SR'] = 100 * bat_vs_team['runs_scored'] / bat_vs_team['balls_faced']
bat_vs_team['dot_percentage'] = 100 * bat_vs_team['dots'] / bat_vs_team['balls_faced']

# bat_vs_team.to_csv('bat_vs_team.csv', index=False)


##################
# Bat vs Venue   #
##################

data2 = df.copy()

# Group By Columns

dots = data2.groupby(['striker', 'stadium'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = data2.groupby(['striker', 'stadium'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = data2.groupby(['striker', 'stadium'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_scored = data2.groupby(['striker', 'stadium'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = data2.groupby(['striker', 'stadium'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
wickets_taken = data2.groupby(['striker', 'stadium'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = data2.groupby(['striker', 'stadium'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})


# 50s and 100s

runs_per_innings = pd.DataFrame(data2.groupby(['striker', 'match_id', 'stadium'])['runs_off_bat'].sum().reset_index())

runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

fifties = pd.DataFrame(runs_per_innings.groupby(['striker', 'stadium'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
hundreds = pd.DataFrame(runs_per_innings.groupby(['striker', 'stadium'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})


# Merging all Columns

bat_vs_venue = pd.merge(innings, runs_scored, on=['striker', 'stadium']).merge(
    balls_faced, on=['striker', 'stadium']).merge(
        wickets_taken, on=['striker', 'stadium']).merge(
            dots, on=['striker', 'stadium']).merge(
                fours, on=['striker', 'stadium']).merge(
                    sixes, on=['striker', 'stadium']).merge(
                        fifties, on=['striker', 'stadium']).merge(
                            hundreds, on=['striker', 'stadium']
                        )


# Additional Columns
bat_vs_venue['batting_AVG'] = bat_vs_venue.apply(lambda x: x['runs_scored'] if x['wickets_taken'] == 0 else x['runs_scored']/x['wickets_taken'], axis=1)
bat_vs_venue['batting_SR'] = 100 * bat_vs_venue['runs_scored'] / bat_vs_venue['balls_faced']
bat_vs_venue['dot_percentage'] = 100 * bat_vs_venue['dots'] / bat_vs_venue['balls_faced']

# final_data[final_data['striker'] == 'V Kohli'].head(10)

# bat_vs_venue.to_csv('bat_vs_venue.csv', index=False)


##################
# Bat vs Bowl    #
##################

data3 = df.copy()

# 50s and 100s

runs_per_innings = pd.DataFrame(data3.groupby(['striker', 'match_id'])['runs_off_bat'].sum().reset_index())

runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

fifties = pd.DataFrame(runs_per_innings.groupby(['striker'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
hundreds = pd.DataFrame(runs_per_innings.groupby(['striker'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})

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

dots = bat_vs_ball.groupby(['striker', 'bowler'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = bat_vs_ball.groupby(['striker', 'bowler'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = bat_vs_ball.groupby(['striker', 'bowler'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_scored = bat_vs_ball.groupby(['striker', 'bowler'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = bat_vs_ball.groupby(['striker', 'bowler'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
wickets_taken = bat_vs_ball.groupby(['striker', 'bowler'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = bat_vs_ball.groupby(['striker', 'bowler'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

matchup = pd.merge(innings, runs_scored, on=['striker', 'bowler']).merge(
    balls_faced, on=['striker', 'bowler']).merge(
        wickets_taken, on=['striker', 'bowler']).merge(
            dots, on=['striker', 'bowler']).merge(
                fours, on=['striker', 'bowler']).merge(
                    sixes, on=['striker', 'bowler'])

matchup['batting_SR'] = 100 * matchup['runs_scored'] / matchup['balls_faced']
matchup['dot_percentage'] = 100 * matchup['dots'] / matchup['balls_faced']
# matchup['inning_vs_dismissal'] = matchup['innings'] - matchup['wickets_taken']
matchup = matchup[['striker', 'bowler', 'innings', 'runs_scored', 'wickets_taken', 'batting_SR', 'dot_percentage']]
# matchup.to_csv('matchups.csv', index=False)

##################
# Batting Record #
##################


data4 = df.copy()

# 50s and 100s

runs_per_innings = pd.DataFrame(data4.groupby(['striker', 'match_id'])['runs_off_bat'].sum().reset_index())

runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

fifties = pd.DataFrame(runs_per_innings.groupby(['striker'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
hundreds = pd.DataFrame(runs_per_innings.groupby(['striker'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})

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

dots = batting_record.groupby(['striker'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = batting_record.groupby(['striker'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = batting_record.groupby(['striker'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_scored = batting_record.groupby(['striker'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = batting_record.groupby(['striker'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
wickets_taken = batting_record.groupby(['striker'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = batting_record.groupby(['striker'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

batting = pd.merge(innings, runs_scored, on=['striker']).merge(
    balls_faced, on=['striker']).merge(
        wickets_taken, on=['striker']).merge(
            dots, on=['striker']).merge(
                fours, on=['striker']).merge(
                    fifties, on=['striker']).merge(
                        hundreds, on=['striker']).merge(
                            sixes, on=['striker'])

batting['batting_SR'] = 100 * batting['runs_scored'] / batting['balls_faced']
batting['dot_percentage'] = 100 * batting['dots'] / batting['balls_faced']
batting['batting_AVG'] = batting['runs_scored'] / batting['wickets_taken']

# batting.to_csv('batting_record.csv', index=False)


#########################
# Batting Record by Year#
#########################

data8 = df.copy()

# 50s and 100s

runs_per_innings = pd.DataFrame(data8.groupby(['striker', 'match_id', 'year'])['runs_off_bat'].sum().reset_index())

runs_per_innings['is_50'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 50 and x < 100 else 0)
runs_per_innings['is_100'] = runs_per_innings['runs_off_bat'].apply(lambda x: 1 if x >= 100 else 0)

fifties = pd.DataFrame(runs_per_innings.groupby(['striker', 'year'])['is_50'].sum()).reset_index().rename(columns={'is_50': 'fifties'})
hundreds = pd.DataFrame(runs_per_innings.groupby(['striker', 'year'])['is_100'].sum()).reset_index().rename(columns={'is_100': 'hundreds'})

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

dots = batting_record_by_year.groupby(['striker', 'year'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = batting_record_by_year.groupby(['striker', 'year'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = batting_record_by_year.groupby(['striker', 'year'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_scored = batting_record_by_year.groupby(['striker', 'year'])['runs_off_bat'].sum().reset_index().rename(columns={'runs_off_bat': 'runs_scored'})
balls_faced = batting_record_by_year.groupby(['striker', 'year'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_faced'})
wickets_taken = batting_record_by_year.groupby(['striker', 'year'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = batting_record_by_year.groupby(['striker', 'year'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

batting_by_year = pd.merge(innings, runs_scored, on=['striker', 'year']).merge(
    balls_faced, on=['striker', 'year']).merge(
        wickets_taken, on=['striker', 'year']).merge(
            dots, on=['striker', 'year']).merge(
                fours, on=['striker', 'year']).merge(
                    fifties, on=['striker', 'year']).merge(
                        hundreds, on=['striker', 'year']).merge(
                            sixes, on=['striker', 'year'])

batting_by_year['batting_SR'] = 100 * batting_by_year['runs_scored'] / batting_by_year['balls_faced']
batting_by_year['dot_percentage'] = 100 * batting_by_year['dots'] / batting_by_year['balls_faced']
batting_by_year['batting_AVG'] = batting_by_year['runs_scored'] / batting_by_year['wickets_taken']



##################
# Bowling Record #
##################


data5 = df.copy()


data5['is_four'] = data5['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data5['is_six'] = data5['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

data5['total_runs'] = data5['runs_off_bat'] + data5['extras']

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

data5['bowlers_wicket'] = data5['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

bowling_record = data5

# Additional Columns

dots = bowling_record.groupby(['bowler'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = bowling_record.groupby(['bowler'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = bowling_record.groupby(['bowler'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_conceded = bowling_record.groupby(['bowler'])['total_runs'].sum().reset_index().rename(columns={'total_runs': 'runs_conceded'})
balls_bowled = bowling_record.groupby(['bowler'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_bowled'})
wickets_taken = bowling_record.groupby(['bowler'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = bowling_record.groupby(['bowler'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

bowling = pd.merge(innings, runs_conceded, on=['bowler']).merge(
    balls_bowled, on=['bowler']).merge(
        wickets_taken, on=['bowler']).merge(
            dots, on=['bowler']).merge(
                fours, on=['bowler']).merge(
                    sixes, on=['bowler'])

bowling['Economy'] = 6 * bowling['runs_conceded'] / bowling['balls_bowled']
bowling['bowling_AVG'] = bowling['runs_conceded'] / bowling['wickets_taken']


# bowling.to_csv('bowling_record.csv', index=False)


############################
# Bowling Record by Season #
############################


data7 = df.copy()


data7['is_four'] = data7['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
data7['is_six'] = data7['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

data7['total_runs'] = data7['runs_off_bat'] + data7['extras']

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

data7['bowlers_wicket'] = data7['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

bowling_record_by_year = data7

# Additional Columns

dots = bowling_record_by_year.groupby(['bowler', 'year'])['is_dot'].sum().reset_index().rename(columns = {'is_dot': 'dots'})
fours = bowling_record_by_year.groupby(['bowler', 'year'])['is_four'].sum().reset_index().rename(columns = {'is_four': 'fours'})
sixes = bowling_record_by_year.groupby(['bowler', 'year'])['is_six'].sum().reset_index().rename(columns = {'is_six': 'sixes'})

runs_conceded = bowling_record_by_year.groupby(['bowler', 'year'])['total_runs'].sum().reset_index().rename(columns={'total_runs': 'runs_conceded'})
balls_bowled = bowling_record_by_year.groupby(['bowler', 'year'])['runs_off_bat'].count().reset_index().rename(columns={'runs_off_bat': 'balls_bowled'})
wickets_taken = bowling_record_by_year.groupby(['bowler', 'year'])['bowlers_wicket'].sum().reset_index().rename(columns={'bowlers_wicket': 'wickets_taken'})
innings = bowling_record_by_year.groupby(['bowler', 'year'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns = {'match_id': 'innings'})

bowling_by_year = pd.merge(innings, runs_conceded, on=['bowler', 'year']).merge(
    balls_bowled, on=['bowler', 'year']).merge(
        wickets_taken, on=['bowler', 'year']).merge(
            dots, on=['bowler', 'year']).merge(
                fours, on=['bowler', 'year']).merge(
                    sixes, on=['bowler', 'year'])

bowling_by_year['Economy'] = 6 * bowling_by_year['runs_conceded'] / bowling_by_year['balls_bowled']
bowling_by_year['bowling_AVG'] = bowling_by_year['runs_conceded'] / bowling_by_year['wickets_taken']




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
dataframes = [bat_vs_venue, bat_vs_team, matchup, batting, bowling, batting_by_year, bowling_by_year]
table_names = ['batter_vs_venue', 'batter_vs_team', 'batter_vs_bowler', 'batting_record', 'bowling_record', 'batting_record_by_year', 'bowling_record_by_year']
table_columns = [
    ['striker', 'stadium', 'innings', 'runs_scored', 'balls_faced', 'wickets_taken', 'dots', 'fours', 'sixes',
     'fifties', 'hundreds', 'batting_AVG', 'batting_SR', 'dot_percentage'],  # Columns for batter_vs_venue
    ['striker', 'bowling_team', 'innings', 'runs_scored', 'balls_faced', 'wickets_taken', 'dots', 'fours', 'sixes',
     'fifties', 'hundreds', 'batting_AVG', 'batting_SR', 'dot_percentage'],  # Columns for batter_vs_team
    ['striker', 'bowler', 'innings', 'runs_scored', 'wickets_taken', 'batting_SR', 'dot_percentage'],  # Columns for batter_vs_bowler
    ['striker', 'innings', 'runs_scored', 'balls_faced', 'wickets_taken,dots',
     'fours', 'fifties', 'hundreds', 'sixes', 'batting_SR', 'dot_percentage', 'batting_AVG'], # Columns for batting_record
    ['bowler', 'innings', 'runs_conceded', 'balls_bowled', 'wickets_taken',
     'dots', 'fours', 'sixes', 'Economy', 'bowling_AVG'], # Columns for bowling_record
    ['striker', 'year', 'innings', 'runs_scored', 'balls_faced', 'wickets_taken,dots',
     'fours', 'fifties', 'hundreds', 'sixes', 'batting_SR', 'dot_percentage', 'batting_AVG'], # Columns for batting_record_by_year
    ['bowler', 'year', 'innings', 'runs_conceded', 'balls_bowled', 'wickets_taken',
     'dots', 'fours', 'sixes', 'Economy', 'bowling_AVG'] # Columns for bowling_record_by_year
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
