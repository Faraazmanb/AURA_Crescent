import datetime
import random
from flask import Flask
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from admin_dashboard_helper import network_load, user_names, new_users, users_month, users_year, active_users, study_time


def drawFigure_Users_Month():
    fig = users_month()
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=fig,
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ])

def drawFigure_Users_Year():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=users_year().update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ])



def drawFigure_Users_Active():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=active_users().update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ])



def drawFigure_Users_Study_Time():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=study_time().update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ])



def drawFigure_Users_New_Users():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=new_users().update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                        
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ]) 



def drawFigure_Users_Name():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=user_names().update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(2, 2, 2, 0.4)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ]) 

def drawFigure_Up_Time():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = 100, 
                    number = {'suffix': "%"},  # Add percentage symbol to the displayed value
                    title = {'text': "Todays Up TIme"},
                    gauge = {
                        'axis': {'range': [0, 100]}  # Set the range for the gauge
                    },
                    domain = {'x': [0, 1], 'y': [0, 1]}
                    )).update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(2, 2, 2, 0.4)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ]) 


def drawFigure_Network_load():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=network_load().update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(2, 2, 2, 0.4)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ]) 


# Text field
def drawText_Admin_Dashbaord():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("ADMIN Dashbaord"),
                ], style={'textAlign': 'center'})
            ])
        ),
    ])


# Data
df = px.data.iris()