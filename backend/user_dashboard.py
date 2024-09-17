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

from user_dashboard_helper import questions_attempt

def drawText_User_Dashbaord():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("USER Dashbaord"),
                ], style={'textAlign': 'center'})
            ])
        ),
    ])

def drawFigure_Users_Month():
    fig = questions_attempt()
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


