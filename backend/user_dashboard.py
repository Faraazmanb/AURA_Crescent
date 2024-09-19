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

from user_dashboard_helper import *

def return_html(figure):
    return html.Div([
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(
                        figure=figure,
                        config={
                            'displayModeBar': False
                        }
                    )
                ])
            ),
        ])


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
    return return_html(fig)

def drawFigure_Correct_Incorrect():
    fig = correct_incorrect()
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return return_html(fig)

def drawFigure_Average():
    fig = avg_score()
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return return_html(fig)

def drawFigure_User_activity():
    fig = user_activity()
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return return_html(fig)



def drawFigure_Leaderbaord():
    fig = leaderbaord()
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return return_html(fig)


def drawFigure_Test_Insight():
    fig = test_insight()
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return return_html(fig)

