#! /usr/bin/python
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from pages import Pick, Movie, Stats, About, TopRated
from lib import Navbar
from services.DataManager import DataManager

"""
    The site generally works as a MVC, where a layout is returned based
    on the URL. There is a placeholder which is populated by these
    layouts, creating a dashboard which is divided into multiple sections.
"""
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    """
        Return a page layout depending on the url parameters.
    """
    if pathname == '/dashboard':
        return Dashboard.layout
    elif pathname.startswith('/movie'):
        params = pathname.split('/')
        # Split the url parameters to retreive the movie id.
        return Movie.getLayout(int(params[2]))
    elif pathname.startswith('/toprated'):
        params = pathname.split('/')
        # Split the url parameters to retreive the page ranking range.
        return TopRated.getLayout(int(params[2]))
    elif pathname.startswith('/stats'):
        return Stats.getLayout()
    elif pathname.startswith('/about'):
        return About.getLayout()
    else:
        return Pick.layout

if __name__ == '__main__':
    DataManager(init=True)
    app.run_server(debug=False)
