#! /usr/bin/python

__author__ = "Michelle Dijkstra and Miguel Pieters"
__copyright__ = "Copyright 2018"
__credits__ = ["Nanne van Noord", "Bär Halberkamp"]
__license__ = "GPL"
__version__ = "1.0"
__email__ = "miguelpieters@me.com"
__status__ = "Production"

import dash

app = dash.Dash()

app.css.append_css({'external_url': 'https://use.fontawesome.com/releases/v5.0.13/css/all.css'})
app.css.append_css({'external_url': 'https://123-bijles.nl/netvis.css'})
app.css.append_css({'external_url': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css'})

app.title = 'Flixdash'

server = app.server
app.config.suppress_callback_exceptions = True
