# -*- coding: utf-8 -*-

import os
from datetime import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_sqlalchemy import SQLAlchemy

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

server.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)


class PPM(db.Model):
    __tablename__ = 'ppm'

    date = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Integer)
    on_time = db.Column(db.Integer)
    late = db.Column(db.Integer)
    ppm = db.Column(db.Float)
    rolling_ppm = db.Column(db.Float)


@server.route('/db_test')
def db_test():
    db.create_all()
    ppm = PPM.query.first()
    if not ppm:
        return "No entries in PPM table!"
    else:
        date = datetime.fromtimestamp(ppm.date)
        date = date.strftime('%Y-%m-%d %H:%M:%S')

        return ('{}: ({},{},{}), ({},{})'.format(
            date, ppm.total, ppm.on_time, ppm.late, ppm.ppm, ppm.rolling_ppm
        ))


@server.route('/db_drop')
def db_drop():
    db.drop_all()
    return "All tables dropped."


app.layout = html.Div(children=[
    html.H1(children='thetrains'),

    html.Div(children='''
        thetrains dash application
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
                'title': 'thetrains example visualisation'
            }
        }
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
