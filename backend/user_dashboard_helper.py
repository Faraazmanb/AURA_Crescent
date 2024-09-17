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
