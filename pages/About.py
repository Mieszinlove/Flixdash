import json
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from services.DataManager import DataManager
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go

from app import app
from lib import Navbar

DM = DataManager()

def getLayout():

    return html.Div([
        Navbar.getLayout('about'),

        html.Div([
            html.Div([
                html.H1('Beheren van Big Data'),
                html.H3(html.I('"The smarter you get, the less you speak"', style={'color': '#5d5d5d'})),
                html.H4('Data Abstractie'),
                html.Ul([
                    html.Li(html.H6('Samenvatten')),
                    html.Li(html.H6('Archiveren')),
                    html.Li(html.H6('Hergebruiken'))
                ]),
                html.H4('Server Caches'),
                html.H5('Film cache'),
                html.Pre('{ \
                          \n\t"Correlated": [\
                          \n\t\t#1,\
                          \n\t\t#2,\
                          \n\t\t#3,\
                          \n\t\t#4,\
                          \n\t\t#5\
                          \n\t],\
                          \n\t"Meta": {\
                          \n\t\t"Id": Integer,\
                          \n\t\t"Plot": Text,\
                          \n\t\t"Poster": Img-url,\
                          \n\t\t"Release-Year": Integer,\
                          \n\t\t"Title": Text,\
                          \n\t},\
                          \n\t"Time": Milliseconds\
                          \n}'),
                html.H5('Boxplot'),
                html.Pre('{ \
                          \n\t"Year": [\
                          \n\t\tInteger,\
                          \n\t\tInteger,\
                          \n\t\t...\
                          \n\t],\
                          \n\t"Time": Milliseconds\
                          \n}'),
                html.H5('Top Rated'),
                html.Pre('{ \
                          \n\t"Rankings": [\
                          \n\t\tInteger,\
                          \n\t\tInteger,\
                          \n\t\t...\
                          \n\t],\
                          \n\t"Time": Milliseconds\
                          \n}')
            ], className='col-12 facts'),
        ], className='wrapper')
    ])
