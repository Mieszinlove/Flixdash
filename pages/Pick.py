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

layout = html.Div([
    Navbar.getLayout('pick'),

    html.Div(id='movie-data', style={'display': 'none'}),
    html.Div([
        html.H1('Pick a Movie'),
        dcc.Dropdown(
            id='dropdown',
            options=[
                {'label': DM.get_movie_title(x)['Title'], 'value': x} for x in list(DM.get_titles().keys())[:10]
            ],
            placeholder='Type title of a movie...'
        ),
        html.Hr(),
        html.Button([html.I(className='fas fa-blender'), ' Random Movies'], className='btn btn-search', id='search'),
        html.Br()
    ], className='wrapper'),
    html.Ul([], id='categories', className='clr')
])

@app.callback(
    Output('categories', 'children'),
    [Input('search', 'n_clicks')])
def clicks(n_clicks):
    """
        Fetch newly generated movies.
    """
    return [html.Li(className='pusher')] + \
        [html.Li([
            html.Div([
                html.H1(x['Meta']['Title']),
                html.P(html.A('See More', href='./movie/' + str(x['Meta']['Id'])))
            ], style={'background-image': 'url(' + x['Meta']['Poster'] + ')'})
        ]) for x in DM.pick_random_movies(8)]

@app.callback(
    Output('url', 'pathname'),
    [Input('dropdown', 'value')]
)
def redirect(value):
    """
        Redirect the user to the movie page if a movie is selected from the dropdown menu.
    """
    return '/movie/' + str(value)
