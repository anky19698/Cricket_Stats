# All Imports

import pandas as pd
import requests
import zipfile
import io
import glob
import os
import numpy as np


# Download Data From Cricsheet
url = 'https://cricsheet.org/downloads/ipl_male_csv2.zip'

response = requests.get(url)
destination_folder = 'Cricstat/iplData'

if response.status_code == 200:
    with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zip_files:
        zip_files.extractall(destination_folder)
        print('success')
else:
    print('failed')


# Extract Zip File and Create CSV of All IPL Data

files = glob.glob('Cricstat/iplData/[0-9]*.csv')
all_files = []
for file in files:
    filename = os.path.basename(file)
    if 'info' not in filename:
        all_files.append(file)

df = pd.concat((pd.read_csv(f, header=0) for f in all_files))

# Exporting final csv without super over data

df = df[df['innings'] < 3]

# Add Unique Stadium Names

# Dictionary to map the replacements
replacements = {
    'chepauk': 'MA Chidambaram Stadium, Chepauk, Chennai',
    'chidambaram': 'MA Chidambaram Stadium, Chepauk, Chennai',
    'wankhede': 'Wankhede Stadium, Mumbai',
    'chinnaswamy': 'M Chinnaswamy Stadium, Bengaluru',
    'punjab': 'Punjab Cricket Association IS Bindra Stadium, Mohali',
    'sawai mansingh': 'Sawai Mansingh Stadium, Jaipur',
    'rajiv gandhi international stadium': 'Rajiv Gandhi International Stadium',
    'arun jaitley': 'Arun Jaitley Stadium',
    'feroz shah': 'Arun Jaitley Stadium',
    'himachal pradesh cricket association stadium': 'Himachal Pradesh Cricket Association Stadium',
    'dr dy patil sports academy': 'Dr DY Patil Sports Academy',
    'dr dy patil sports academy, mumbai': 'Dr DY Patil Sports Academy, Mumbai',
    'eden gardens': 'Eden Gardens, Kolkata',
    'motera': 'Narendra Modi Stadium, Ahmedabad',
    'maharashtra': 'Maharashtra Cricket Association Stadium, Pune',
    'sahara': 'Maharashtra Cricket Association Stadium, Pune',
    'brabourne': 'Brabourne Stadium, Mumbai'
}

# Function to replace values
def replace_venue(name):
    for key, value in replacements.items():
        if key in name.lower():
            return value
    return name

# Apply the function to each venue in the DataFrame
df['stadium'] = df['venue'].apply(replace_venue)


# Additional Columns

df['is_dot'] = df['runs_off_bat'].apply(lambda x: 1 if x == 0 else 0)
df['is_one'] = df['runs_off_bat'].apply(lambda x: 1 if x == 1 else 0)
df['is_two'] = df['runs_off_bat'].apply(lambda x: 1 if x == 2 else 0)
df['is_three'] = df['runs_off_bat'].apply(lambda x: 1 if x == 3 else 0)
df['is_four'] = df['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
df['is_six'] = df['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

bowlers_wicket = ['bowled', 'caught', 'caught and bowled', 'lbw',
       'stumped', 'hit wicket']

df['bowlers_wicket'] = df['wicket_type'].apply(lambda x: 1 if x in bowlers_wicket else 0)

df['start_date'] = pd.to_datetime(df['start_date'])

df['year'] = df['start_date'].dt.year.astype(int)

df.to_csv('all_ipl_data.csv', index=False)
