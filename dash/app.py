# -*- coding: utf-8 -*-

import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_sqlalchemy import SQLAlchemy

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

#server.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
#server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(server)

app.layout = html.Div(children=[
    html.H1(children='thetrains.co.uk'),

    html.Div(children='''
        thetrains.co.uk dash application
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2],
                    'type': 'bar', 'name': 'Train1'},
                {'x': [1, 2, 3], 'y': [2, 4, 5],
                    'type': 'bar', 'name': 'Train2'},
            ],
            'layout': {
                'title': 'thetrains.co.uk example visualisation'
            }
        }
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
