import datetime
import random
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def network_load():
    # Generate 1000 random time points and percentages for active users and network load
    sample_size = 500
    time = pd.date_range(start='2023-09-17 06:00', periods=sample_size, freq='h')
    active_users = np.random.randint(2, 100, size=sample_size)  # Random active users percentage
    network_load = np.random.randint(5, 100, size=sample_size)    # Random network load percentage

    # Create the DataFrame
    data = {
        'time': time,
        'active_users_%': active_users,
        'network_load_%': network_load
    }
    df = pd.DataFrame(data)

    # Apply rolling mean (smoothing)
    df['active_users_%'] = df['active_users_%'].rolling(window=20).mean()  # Rolling window for active users
    df['network_load_%'] = df['network_load_%'].rolling(window=20).mean()  # Rolling window for network load

    # Drop the NaN values created by the rolling operation
    df = df.dropna()

    # Create the line plot with 1000 rows of data (smoothed)
    fig = px.line(
        df, 
        x='time',
        y=[
            'active_users_%',
            'network_load_%'
        ],
        labels={'value': 'Percentage', 'variable': 'Metrics'}  # Labels for the legend
    )

    # Update the layout
    fig.update_layout(
        title='Network Load and Active Users Over Time (Smoothed)',  # Adding title
        xaxis_title='Time',  # Title for x-axis
        yaxis_title='Percentage',  # Title for y-axis
        xaxis=dict(           # Attributes for x-axis
            showline=True,
            showgrid=True,
            linecolor='black',
            tickfont=dict(
                family='Calibri'
            )
        ),
        yaxis=dict(           # Attributes for y-axis
            showline=True,
            showgrid=True,
            linecolor='black',
            tickfont=dict(
                family='Times New Roman'
            )
        ),
        plot_bgcolor='white'  # Background color for the graph
    )

    return fig


def user_names():
    names = ["David",  "Alice", "Bob", "Charlie", "Eva", "Frank", "Grace", "Hannah", "Ivy", "Jack", 'Jill']

    # Determine grid dimensions (for example, 3x4 grid)
    rows = 6
    cols = 2

    # Create subplots with adjusted subplot size
    fig = make_subplots(rows=rows, cols=cols, 
                        vertical_spacing=0.02,  # Adjust vertical spacing
                        horizontal_spacing=0.02)  # Adjust horizontal spacing


    # Add names to each subplot
    for i, name in enumerate(names):
        row = i // cols + 1
        col = i % cols + 1
        fig.add_trace(
            go.Scatter(
                x=[0],
                y=[0],
                text=name,
                mode='text',
                textfont=dict(size=24),
                showlegend=False
            ),
            row=row, col=col
        )

    # Update layout to define grid layout and remove gridlines and axes
    fig.update_layout(
        title_text="Employees",
        height=450,
        width=700,
        showlegend=False,
    )

    # Update axes properties for each subplot
    for i in range(1, rows + 1):
        for j in range(1, cols + 1):
            fig.update_xaxes(
                visible=False,
                row=i,
                col=j
            )
            fig.update_yaxes(
                visible=False,
                row=i,
                col=j
            ) 

    return fig

def new_users():
    linear_values = np.linspace(1, 100, num=12)
    random_noise = np.random.uniform(0, 10, size=12)
    noisy_values = linear_values + random_noise

    data = {
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nove", "Dec"],
        "New Users": noisy_values  # Example values
    }
    new_users_df = pd.DataFrame(data)
    fig = px.bar(
        new_users_df, x="Month", y="New Users", title="New Users"
        )
    return fig

def users_month():
    users = pd.DataFrame(
        [["example",  datetime.date(random.randint(2021, 2024), random.randint(1, 12), random.randint(1, 28))] for i in range(2000)],
        columns=['Name', 'Join']
    )
    users['Join'] = pd.to_datetime(users['Join'])
    user_count_by_month = users.groupby(pd.Grouper(key='Join', freq='ME')).size().reset_index(name='Number of Users')
    fig=px.bar(user_count_by_month, x='Join', y='Number of Users', title='Number of Users Joined Over Time (Monthly Aggregation)')
    return fig

def users_year():
    users = pd.DataFrame(
        [["example",  datetime.date(random.randint(2021, 2024), random.randint(1, 12), random.randint(1, 28))] for i in range(1000)],
        columns=['Name', 'Join']
    )
    users['Join'] = pd.to_datetime(users['Join'])
    user_count_by_year = users.groupby(pd.Grouper(key='Join', freq='Y')).size().reset_index(name='Number of Users')
    fig = px.bar(user_count_by_year, x='Join', y='Number of Users', title='Number of Users Joined Over Time (Monthly Aggregation)')
    return fig

def active_users():
    active_users = pd.DataFrame(
        [["example", random.choice(["active", "not active", "long time inactive"])] for i in range(100)],
        columns=['Name', 'Active']
    )
    user_count_by_active = active_users.groupby("Active").size().reset_index(name='Count')
    colors = {
        "active": "green",
        "not active": "orange",
        "long time inactive": "red"
    }

    fig=px.pie(
            user_count_by_active, 
            names='Active', 
            values='Count',
            title='Distribution of User Activity Status',
            color='Active',
            color_discrete_map=colors,
            hole=0.6 
            )
    return fig

def study_time():
    data = [["Example", random.randint(2,13), round(random.uniform(1,4),1), random.choice(['Free User', "Limited Plan", "Premium Plan"])]for i in range(100)]
    Study_time_df = pd.DataFrame(data, columns=["Name", "Study Time", "Idle Time", "Plan"])
    fig = px.bar(Study_time_df, x="Study Time", y="Idle Time", color="Plan",title="User Study Time")
    return fig
