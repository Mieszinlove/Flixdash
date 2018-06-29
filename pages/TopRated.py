import json
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
from services.DataManager import DataManager
from services.Stats import Stats
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go

from app import app
from lib import Navbar

DM = DataManager()

# Amount of results per page
_CONTENT_SIZE = 20

def getLayout(index):
    return html.Div([
        Navbar.getLayout('top'),

        html.Div(initialize(index), id='range-data', style={'display': 'none'}),
        html.Div([
            html.H1(id='display-range'),
            html.Hr(),
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th('Ranking'),
                        html.Th('Movie Title'),
                        html.Th('Avg. Rating', style={'min-width': '120px'}),
                        html.Th('')
                    ])
                ], className='', style={'background-color': '#db202c', 'color': '#fff'}),
                html.Tbody([

                ], id='table-content'),
            ], className='table'),
            html.Div(id='table-navigation', className='col-12'),
            html.Br(),
            html.Div(id='test')
        ], className='wrapper')
    ])

def initialize(value):
    return json.dumps(
        {
            'Index': (value - 1),
            'Start': (value - 1) * _CONTENT_SIZE,
            'End': (((value - 1) * _CONTENT_SIZE) + (_CONTENT_SIZE - 1))
        }
    )

@app.callback(
    Output('display-range', 'children'),
    [Input('range-data', 'children')]
)
def show_range(value):
    Data = json.loads(value)
    return ['Showing top rated movies ' + str(Data['Start'] + 1) + ' until ' + str(Data['End'] + 1)]

@app.callback(
    Output('table-content', 'children'),
    [Input('range-data', 'children')]
)
def populate_table(value):
    """
        Create the boxplot with as default year 2001.
    """
    Data = json.loads(value)
    TRMovies = DM.get_top_rated(index=Data['Start'], limit=_CONTENT_SIZE)
    Movies = [DM.get_movie_stats(x) for x in TRMovies]

    return [
        html.Tr([
            html.Th('#' + str(DM.get_ranking(Movies[i]['Meta']['Id']) + 1)),
            html.Th(Movies[i]['Meta']['Title']),
            html.Th(format(round(Stats.computeRatings(Movies[i]['Ratings'], perYear=False), 2), '.2f')),
            html.Th(
                html.Center(
                    html.A(
                        html.Button('More Info', className='btn btn-primary'),
                        href='../movie/' + str(Movies[i]['Meta']['Id'])
                    )
                )
            )
        ])
        for i in range(len(Movies))
    ]

@app.callback(
    Output('table-navigation', 'children'),
    [Input('range-data', 'children')]
)
def table_navigation(value):
    """
        Generate 'Previous' and 'Next' button.
    """
    Data = json.loads(value)
    return [
                html.A(
                    [html.Button('Previous', id='prev', className='btn btn-secondary', disabled=True)
                    if Data['Index'] == 0 else
                    html.Button('Previous', id='prev', className='btn btn-secondary')],
                    href='./' + str(Data['Index'])

                ),

                html.A(
                    [html.Button('Next', id='next', className='btn btn-secondary', disabled=True, style={'float': 'right'})
                    if Data['Index'] == len(DM.get_titles()) else
                    html.Button('Next', id='next', className='btn btn-secondary', style={'float': 'right'})],
                    href='./' + str(Data['Index'] + 2)
                )
            ]
