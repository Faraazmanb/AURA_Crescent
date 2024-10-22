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

from report_dashbaord_helper import *

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


def drawText_Report_Dashbaord():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("REPORT"),
                ], style={'textAlign': 'center'})
            ])
        ),
    ])

def drawFigure_Correct_incorrect(data):
    fig = report_correct_incorrect(data)
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return return_html(fig)


def drawFigure_Average_score_Report(data):
    fig = report_avg_score(data)
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return return_html(fig)


def drawFigure_Leaderbaord_Report(mongo_client):
    fig = report_leaderboard(mongo_client)
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return return_html(fig)


def drawFigure_Time_Taken(data):
    fig = time_taken_bar(data)
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return return_html(fig)

