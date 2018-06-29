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

def getLayout(movie_id):
    return html.Div([
        Navbar.getLayout('pick'),

        html.Div(initialize(movie_id), id='movie-data', style={'display': 'none'}),
        html.Div([
            html.H1(id='display-title'),
            html.Hr(),
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div([
                                html.H2(id='total-ratings'),
                                html.H3('Ratings')
                            ], className='col-6'),
                            html.Div([
                                html.H2(id='average-rating'),
                                html.H3('Average')
                            ], className='col-6'),
                            html.Div([
                                html.H2(id='release-year'),
                                html.H3('Release')
                            ], className='col-6'),
                            html.Div([
                                html.H2(id='movie-ranking'),
                                html.H3('Rank')
                            ], className='col-6')
                        ], className='row')
                    ], className='stats', style={'margin-left': '1em'}),
                    html.Div(id='plot-desc', style={'margin-right': '1em', 'margin-top': '1em'})
                ], className='col-6'),

                html.Div([
                    html.Img(id='poster', style={'float': 'right'})
                ], className='col-6'),
            ], className='row'),
            html.Hr(),
            html.Div([
                html.Div([
                    html.H3('Average ratings per year'),
                    html.Div(id='display-graph')
                ], className='col-6'),
                html.Div([
                    html.H3('Comparable average ratings'),
                    html.Div(id='barchart')
                ], className='col-6')
            ], className='row'),
            html.H3('Comparable Movies'),
        ], className='wrapper'),
        html.Ul([
        ], id='correlated', className='clr')
    ])

def initialize(value):
    Movie = DM.get_movie_stats(value)

    return json.dumps(
        {
            'Correlated': Movie['Correlated'],
            'Id': Movie['Meta']['Id'],
            'Ratings': Movie['Ratings'],
            'Title': Movie['Meta']['Title'],
            'Release-Year': Movie['Meta']['Release-Year'],
            'Poster': Movie['Meta']['Poster'],
            'Plot': Movie['Meta']['Plot']
        }
    )

@app.callback(
    Output('display-graph', 'children'),
    [Input('movie-data', 'children')]
)
def display_ratings(value):
    """
        Display the ratings per year in a line graph.
    """
    Data = json.loads(value)

    Keys = sorted([Year for Year in Data['Ratings']])
    Ratings = [Data['Ratings'][x][0] / Data['Ratings'][x][1] for x in Keys]

    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=Keys,
                    y=Ratings,
                    line = dict(
                        color = ('rgb(219, 32, 44)')
                    ),
                    text = [
                        '{} ratings <br> <b>{}</b> average'
                            .format(Data['Ratings'][x][1], round(float(Data['Ratings'][x][0] / Data['Ratings'][x][1]),2))
                        for x in Data['Ratings'].keys()
                    ],
                    hoverinfo = 'text',
                )
            ],
            layout=go.Layout(
                xaxis={'tickmode': 'linear', 'title': 'Years'},
                yaxis={'tickmode': 'array', 'title': 'Rating average'},
                showlegend=False,
                paper_bgcolor='rgb(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
        ),
        config = {
            'displayModeBar': False
        },
        id='linegraph'
    )

@app.callback(
    Output('barchart', 'children'),
    [Input('movie-data', 'children')]
)
def show_bar(value):
    """
        Display the average ratings of comparable movies in a bargraph.
    """
    Data = json.loads(value)

    Corr = [
        (Id, Stats.computeRatings(DM.get_movie_stats(Id)['Ratings'], perYear=False))
        for Id in Data['Correlated']
    ]

    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Bar(
                    x=[Data['Title']] + [DM.get_movie_title(x[0])['Title'] for x in Corr],
                    y=[Stats.computeRatings(Data['Ratings'], perYear=False)] + [x[1] for x in Corr],
                    marker=dict(
                        color=['#db202c'] + ['#5aacac' for _ in range(5)]
                    )
                )
            ],
            layout=go.Layout(
                yaxis={'title': 'Rating average'}
            )
        ),
        id='bar'
    )

@app.callback(
    Output('poster', 'src'),
    [Input('movie-data', 'children')]
)
def show_poster(value):
    """
        Serve the user with a poster of the movie (if available).
    """
    Data = json.loads(value)
    return (Data['Poster'])

@app.callback(
    Output('plot-desc', 'children'),
    [Input('movie-data', 'children')]
)
def show_desc(value):
    """
        Serve the user with a description of the movie (if available).
    """
    Data = json.loads(value)
    return [html.H4('Movie description'), html.P(Data['Plot'])]

@app.callback(
    Output('display-title', 'children'),
    [Input('movie-data', 'children')]
)
def display_title(value):
    """
        Serve the user with the movie title (if available).
    """
    Data = json.loads(value)
    Rating = 0
    Users = 0

    for Year in Data['Ratings']:
        Mem = Data['Ratings'][Year]
        Rating += Mem[0]
        Users += Mem[1]

    Stars = [html.I(className='fa fa-star') for i in range(int(Rating / Users))]
    Remainder = round(float(str((Rating / Users)-int((Rating / Users)))[1:]),2)
    if Remainder >= 0.75:
        Stars.append(html.I(className='fa fa-star'))
    elif Remainder >= 0.25:
        Stars.append(html.I(className='fa fa-star-half'))

    Stars = [html.Div(Stars, className='star-ratings')]
    return [Data['Title']] + Stars

@app.callback(
    Output('release-year', 'children'),
    [Input('movie-data', 'children')]
)
def display_release(value):
    """
        Display the release year of the movie.
    """
    Data = json.loads(value)
    return Data['Release-Year']

@app.callback(
    Output('total-ratings', 'children'),
    [Input('movie-data', 'children')]
)
def total_ratings(value):
    """
        Display the total ratings of the movie.
    """
    Data = json.loads(value)
    Ratings = 0

    for Year in Data['Ratings']:
        Ratings += Data['Ratings'][Year][1]

    return format(Ratings, ',d')

@app.callback(
    Output('movie-ranking', 'children'),
    [Input('movie-data', 'children')]
)
def movie_ranking(value):
    """
        Fetch the movie ranking of the movie.
    """
    Data = json.loads(value)
    return '#' + str(DM.get_ranking(Data['Id']) + 1)

@app.callback(
    Output('average-rating', 'children'),
    [Input('movie-data', 'children')]
)
def average_rating(value):
    """
        Compute the average rating of the movie.
    """
    Data = json.loads(value)
    Rating = 0
    Users = 0

    for Year in Data['Ratings']:
        Mem = Data['Ratings'][Year]
        Rating += Mem[0]
        Users += Mem[1]

    return round(Rating / Users, 2)

@app.callback(
    Output('correlated', 'children'),
    [Input('movie-data', 'children')]
)
def draw_network(value):
    """
        Generate hexagon network of the correlated movies.
    """
    Data = json.loads(value)
    Comparable = [DM.get_movie_stats(x) for x in Data['Correlated']]
    return [html.Li(className='pusher')] + \
        [html.Li([
            html.Div([
                html.H1(x['Meta']['Title']),
                html.P(html.A('See More', href='../movie/' + str(x['Meta']['Id'])))
            ], style={'background-image': 'url(' + x['Meta']['Poster'] + ')'})
        ]) for x in Comparable]
