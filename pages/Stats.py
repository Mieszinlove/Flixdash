import json
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from numpy import array
from dash.dependencies import Input, Output
from services.DataManager import DataManager
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go

from app import app
from lib import Navbar

DM = DataManager()

def getLayout():
    data = DM.compute_boxplot()
    years = sorted(data.keys())[:-1]

    return html.Div([
        Navbar.getLayout('stats'),

        html.Div(json.dumps(data), id='boxplot-data', style={'display': 'none'}),
        html.Div([
            html.H1('Statistics'),
            html.Div([
                html.Div([
                    html.H2('17.8K'),
                    html.H3([html.I(className='fa fa-film'), ' Movies'])
                ], className='col-3'),
                html.Div([
                    html.H2('480.2K'),
                    html.H3([html.I(className='fa fa-users'), ' Users'])
                ], className='col-3'),
                html.Div([
                    html.H2('100M'),
                    html.H3([html.I(className='fa fa-thumbs-up'), ' Ratings'])
                ], className='col-3'),
                html.Div([
                    html.H2('2.17GB'),
                    html.H3([html.I(className='fa fa-file-archive'), ' Filesize'])
                ], className='col-3')
            ], className='stats row'),
            html.Hr(),
            html.Center([
                html.Br(),
                html.H2('All-time ratings per year', style={'margin-top': '1em', 'margin-bottom': '-2em'})
            ]),
            dcc.Graph(
                figure=go.Figure(
                    data=[
                        go.Scatter(
                            x=years,
                            y=[sum(data[year]) for year in years],
                            line = dict(
                                color = ('rgb(219, 32, 44)')
                            ),
                            text = [
                                str("{:,}".format(sum(data[year]))) + ' ratings' for year in years
                            ],
                            hoverinfo = 'text'
                        )
                    ],
                    layout=go.Layout(
                        xaxis={'tickmode': 'linear', 'title': 'Years'},
                        yaxis={'tickmode': 'array', 'title': 'Ratings per year', 'type': 'log'},
                        showlegend=False,
                        paper_bgcolor='rgb(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                    )
                ),
                config = {
                    'displayModeBar': False
                },
                id='alltime-ratings'
            ),
            html.Center([
                html.H2('Rating dispersion per year', style={'margin-top': '1em', 'margin-bottom': '-2em'})
            ]),
            html.Div(initialize(data), id='box'),
            dcc.RangeSlider(
                marks={i: '{}'.format(i) for i in range(1999, 2006)},
                min=1999,
                max=2005,
                value=[2002],
                id='range'
            )
        ], className='wrapper')
    ])

def initialize(paramData):
    """
        Create the boxplot with as default year 2001.
    """
    x = paramData

    trace = go.Box(
        name = 'Ratings for<br>??',
        x=x['2001']

    )

    layout = {
        'xaxis': {
            'type': 'log',
            'title': 'Ratings per movie'
        }
    }

    return dcc.Graph(figure={'data': [trace], 'layout': layout, 'animate': True}, id='box-plot')

@app.callback(
    Output('boxplot-data', 'children'),
    [Input('range', 'value')]
)
def update_boxplot_data(value):
    """
        Update the boxplot with statistics from the specified year.
    """
    year = str(value[0])
    return json.dumps({year: DM.compute_boxplot()[year]})

@app.callback(
    Output('box', 'children'),
    [Input('boxplot-data', 'children')]
)
def update_boxplot(value):
    """
        Generate a new boxplot with statistics from a specific year.
    """
    mem = json.loads(value)
    year = list(mem.keys())[0]

    x = list(mem.values())[0]

    trace = go.Box(
        name = 'Ratings for<br>' + year,
        x=x

    )

    layout = {
        'xaxis': {
            'type': 'log',
            'title': 'Ratings per movie'
        }
    }

    return dcc.Graph(figure={'data': [trace], 'layout': layout}, id='box-plot')
