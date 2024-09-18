import datetime
import random
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go



def questions_attempt():
    # Generate sample data
    users = pd.DataFrame(
        [["example", random.randint(1, 10), datetime.date(random.randint(2023, 2024), random.randint(1, 12), random.randint(1, 28))]
         for _ in range(20)],
        columns=['Name', 'Questions Attempted', 'Date']
    )
    users['Date'] = pd.to_datetime(users['Date'])
    user_count_by_month = users.groupby(pd.Grouper(key='Date', freq='M')).agg({'Questions Attempted': 'sum'}).reset_index()
    fig = px.bar(
        user_count_by_month, 
        x='Date', 
        y='Questions Attempted', 
        title='Questions Attempted Over Time (Monthly Aggregation)'
    )
    
    return fig

def correct_incorrect():
    correct_incorrect = pd.DataFrame(
        [["example", random.choice(["Correct", "Incorrect", "Skipped"])] for i in range(100)],
        columns=['Name', 'Correct or Incorrect']
    )

    # Count the number of occurrences for each status
    user_count_by_correct = correct_incorrect.groupby("Correct or Incorrect").size().reset_index(name='Count')

    # Define colors for each activity status
    colors = {
        "Correct": "green",
        "Incorrect": "orange",
        "Skipped": "red"
    }

    # Create the donut chart
    fig = px.pie(
        user_count_by_correct,  # Use the grouped data with counts
        names='Correct or Incorrect', 
        values='Count',  # Reference the 'Count' column for the values
        title='Distribution of User Activity Status',
        color='Correct or Incorrect',
        color_discrete_map=colors,
        hole=0.6  # Set the size of the hole in the center of the donut
    )
    return fig

def avg_score():
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = 200,
        title="Average Score since last Month",
        domain = {'x': [0, 1], 'y': [0, 1]},
        delta = {'reference': 40, 'relative': True, 'position' : "bottom"}))
    return fig

def user_activity():
    def generate_random_time():
        hour = random.choice(list(range(0, 8)) + list(range(12, 24)))
        minute = random.randint(0, 59)
        return datetime.time(hour=hour, minute=minute)
    user_activity = pd.DataFrame(
        [["example", generate_random_time()] for _ in range(100)],
        columns=['Name', 'Active Time']
    )
    user_activity['Active Time'] = pd.to_datetime(user_activity['Active Time'], format='%H:%M:%S').dt.time
    user_activity['Hour'] = pd.to_datetime(user_activity['Active Time'].astype(str)).dt.hour
    activity_by_hour = user_activity.groupby('Hour').size().reset_index(name='User Activity Count')
    figure = px.line(
        activity_by_hour, 
        x='Hour', 
        y='User Activity Count', 
        title='User Activity Throughout the Day',
        markers=True
    )
    return figure

def leaderbaord():
    leader = pd.DataFrame([
        ["Rahoul", 560],
        ["Ronak", 234],
        ["Joe", 154],
        ["Tony", 123],
        ["Shane", 112],
        ["Gillis", 83],
        ["Kam", 83],
        ["Patterson", 81],
    ], columns=["Name", "Points"])
    fig = px.bar(leader, x='Name', y='Points')
    return fig

# def users_year():
#     users = pd.DataFrame(
#         [["example",  datetime.date(random.randint(2021, 2024), random.randint(1, 12), random.randint(1, 28))] for i in range(1000)],
#         columns=['Name', 'Join']
#     )
#     users['Join'] = pd.to_datetime(users['Join'])
#     user_count_by_year = users.groupby(pd.Grouper(key='Join', freq='Y')).size().reset_index(name='Number of Users')
#     fig = px.bar(user_count_by_year, x='Join', y='Number of Users', title='Number of Users Joined Over Time (Monthly Aggregation)')
#     return fig

# def active_users():
#     active_users = pd.DataFrame(
#         [["example", random.choice(["active", "not active", "long time inactive"])] for i in range(100)],
#         columns=['Name', 'Active']
#     )
#     user_count_by_active = active_users.groupby("Active").size().reset_index(name='Count')
#     colors = {
#         "active": "green",
#         "not active": "orange",
#         "long time inactive": "red"
#     }

#     fig=px.pie(
#             user_count_by_active, 
#             names='Active', 
#             values='Count',
#             title='Distribution of User Activity Status',
#             color='Active',
#             color_discrete_map=colors,
#             hole=0.6 
#             )
#     return fig
