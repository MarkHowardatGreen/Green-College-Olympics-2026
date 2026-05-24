import streamlit as st
import pandas as pd
import math
import requests
import json
from pathlib import Path
import plotly.express as px

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Olympics Dashboard',
    page_icon=':tennis:', # This is an emoji shortcode. Could be a URL too.
)

#grab Olympics point submissions
api_key = 'sk_prod_jdzrsSN1iDS7X1nPqDKdIPqhUM1baZWa17uT7pMq4g9erNbHrkNNtyoWmByQxDLwVYUwDeBPqlb4BLpqizr78qXMYh0flpof3h3_27197'
form_id = 'ksBq8tvCYQus'

# Construct the API endpoint URL
url = f'https://api.fillout.com/v1/api/forms/{form_id}/submissions'

# Set up the headers with your API key
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
all_responses = []
offset = 0
limit = 150  # max allowed

while True:
    params = {'offset': offset, 'limit': limit}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()
    responses = data.get('responses', [])
    all_responses.extend(responses)

    print(f"Fetched {len(responses)} responses at offset {offset}")

    # if fewer than limit were returned, we've reached the end
    if len(responses) < limit:
        break
    offset += limit

print(f"✅ All responses fetched — total records: {len(all_responses)}")

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :tennis: Olympics Dashboard

'''
team_membership = {
    'Ani':'Myla KcCallum',
    'Riku':'Myla KcCallum',
    'César':'Myla KcCallum',
    'Eduardo' :'Myla KcCallum',
    'Evan':'Myla KcCallum',
    'Joachim':'Myla KcCallum',
    'Keegan':'Myla KcCallum',
    'Layla':'Myla KcCallum',
    'Liam':'Myla KcCallum',
    'Linds':'Myla KcCallum',
    'Abbey': 'Gym Possible',
    'Andrew': 'Gym Possible',
    'Erin': 'Gym Possible',
    'Gabriela': 'Gym Possible',
    'Mitchi': 'Gym Possible',
    'Pedro': 'Gym Possible',
    'Sab': 'Gym Possible',
    'Sofie': 'Gym Possible',
    'Zachary': 'Gym Possible',
    'Linnea': 'Hrishi and the Machine',
    'Dhanya': 'Hrishi and the Machine',
    'Grace': 'Hrishi and the Machine',
    'Hrishikesh': 'Hrishi and the Machine',
    'Karyna': 'Hrishi and the Machine',
    'Mackenzie': 'Hrishi and the Machine',
    'Mark': 'Hrishi and the Machine',
    'Rebecca': 'Hrishi and the Machine',
    'Thomas': 'Hrishi and the Machine',
    'Nico': 'Hrishi and the Machine'
}

activity_multipliers = {
    "Aerobic Dance": (8, 11),
    "Backpacking": (6, 9),
    "Badminton": (7, 10),
    "Ballroom dancing": (8, 14),
    "Basketball": (6, 9),
    "Bicycling": (8, 11),
    "Billiard/pool": (16, 23),
    "Bowling": (16, 23),
    "Calisthenics": (8, 11),
    "Canoeing/rowing": (8, 11),
    "Croquet": (15, 17),
    "Stationary cycling": (7, 10),
    "Fencing": (5, 7),
    "Fishing": (12, 14),
    "Frisbee": (10, 14),
    "Football (Touch)": (8, 11),
    "Gardening (Active)": (20, 30),
    "Golfing": (15, 19),
    "Hiking": (7, 11),
    "Hockey (field & ice)": (5, 7),
    "Kayaking": (8, 11),
    "Martial Arts": (4, 6),
    "Mountain Climbing": (6, 9),
    "Pilates": (10, 13),
    "Racquetball/handball": (8, 11),
    "Rope Skipping": (5, 8),
    "Sailing": (11, 15),
    "SCUBA Diving": (8, 11),
    "Skating": (8, 11),
    "Skiing (Cross country)": (6, 9),
    "Skiing (downhill)": (9, 12),
    "Snowboarding": (7, 9),
    "Snowshoeing": (6, 8),
    "Soccer": (8, 11),
    "Spikeball": (16, 23),
    "Stair/bench stepping": (9, 12),
    "Swimming": (8, 11),
    "Swimming/Surfing": (8, 11),
    "Table Tennis": (16, 23),
    "Tennis": (8, 11),
    "Volleyball": (10, 15),
    "Water-skiing": (8, 11),
    "Weight Training Circuit": (8, 11),
    "Yoga": (11, 15),
    "Running": (6, 9),
    "Walking": (12, 16),
    "Baseball/softball": (11, 15),
    "Spikeball": (16, 23),
    "Sailing": (11, 15),
    "Surfing": (8,11)  
    }

rows = []
for submission in all_responses:
    row = {
        "submissionId": submission.get("submissionId"),
        "submissionTime": submission.get("submissionTime")
    }
    for q in submission.get("questions", []):
        # If it's a file upload, handle differently
        val = q["value"]
        if isinstance(val, list):
            # e.g. take first filename or URL
            val = val[0].get("filename") if val else None
        row[q["name"]] = val
    rows.append(row)

df = pd.DataFrame(rows)
df = df.drop(columns=df.columns[-1])
df = df.drop(df.index[:8])
df['Team']=df['Name'].map(team_membership)

st.write(f"Total number of records: {len(all_responses)}")

df['Date of activity completion'] = pd.to_datetime(df['Date of activity completion'])
df['completedDate'] = df['Date of activity completion'].dt.date
df['submissionTime'] = pd.to_datetime(df['submissionTime'])
df['submissionDate'] = df['submissionTime'].dt.date
df['submissionDate'] = pd.to_datetime(df['submissionDate'])
df['completedDate'] = pd.to_datetime(df['completedDate'])

def compute_points(row):
    submission_date = row['submissionDate']
    completed_date = row['completedDate']

    # If submission is more than 7 days after completion, return 0 points
    if (submission_date - completed_date).days > 7:
        return 0
    
    activity = row['Activity']
    intensity = row['Level of intensity']
    minutes = row['Number of minutes']
    social = row['Did you complete this activity with at least one other Resident Member?']
    games = row['How many games did you win?']
    
    if activity not in activity_multipliers:
        return 0  # or fallback value

    vigorous_div, moderate_div = activity_multipliers[activity]
    divisor = vigorous_div if intensity == "Vigorous" else moderate_div
    base_points = (1300 / divisor) * minutes

    if social == "Yes":
        base_points *= 2

    if pd.isna(games) or games == 0:
        multiplier = 1
    elif (minutes / games) > 30:
        multiplier = games + 1
    else:
        multiplier = (minutes / 30) + 1

    return base_points * multiplier

df['points'] = df.apply(compute_points, axis=1)


# st.dataframe(df)


teamPoints = df.groupby('Team')['points'].sum().reset_index()
teamPoints = teamPoints.rename(columns={'points': 'Total Points'})
teamPoints = teamPoints.sort_values(by='Total Points', ascending=False)

participantPoints = df.groupby('Name').agg(
    Team=('Team', 'first'),
    Points=('points', 'sum')
).reset_index()

# Sort by total_points descending
participantPoints = participantPoints.sort_values(by='Points', ascending=False)
participantPoints['Name'] = participantPoints['Name'].replace('Riku', 'Anonymous Rhino')
participantPoints['Name'] = participantPoints['Name'].replace('Linnea', 'Anonymous Lion')

st.header("Points by Team")
st.dataframe(teamPoints)
st.header("Points by Participant")
st.dataframe(participantPoints)

# Add some spacing
''
''


