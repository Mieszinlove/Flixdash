import dash_core_components as dcc
import dash_html_components as html

from app import app

url = 'http://localhost:8050/'

def getLayout(index):
    return html.Nav([
        html.A(html.Img(src='https://www.123-bijles.nl/logo.png'), className='navbar-brand'),
        html.Div([
            html.Ul([
                html.Li(
                    html.A(
                        'Top Rated',
                        href=(url + 'toprated/1'),
                        className='nav-link ' + \
                        ('active' if index == 'top' else '')
                    ),
                className='nav-item'),
                html.Li(
                    html.A(
                        'Pick A Movie',
                        href=(url + 'pick'),
                        className='nav-link ' + \
                        ('active' if index == 'pick' else '')
                    ),
                className='nav-item'),
                html.Li(
                    html.A(
                        'Statistics',
                        href=(url + 'stats'),
                        className='nav-link ' + \
                        ('active' if index == 'stats' else '')
                    ),
                className='nav-item'),
                html.Li(
                    html.A(
                        'About',
                        href=(url + 'about'),
                        className='nav-link ' + \
                        ('active' if index == 'about' else '')
                    ),
                className='nav-item')
            ], className='navbar-nav')
        ], className='collapse navbar-collapse justify-content-md-center')
    ], className='navbar fixed-top navbar-expand-lg navbar-light bg-white rounded')
