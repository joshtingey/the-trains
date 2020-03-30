# -*- coding: utf-8 -*-

import os
from datetime import datetime
import time

import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'thetrains'
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


def get_df():
    ppm = PPM.query.all()
    ppm_dict = {'date': [], 'timestamp': [], 'total': [], 'on_time': [],
                'late': [], 'ppm': [], 'rolling_ppm': []}

    for entry in ppm:
        timestamp = datetime.fromtimestamp(entry.date)
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ppm_dict['date'].append(entry.date)
        ppm_dict['timestamp'].append(timestamp)
        ppm_dict['total'].append(entry.total)
        ppm_dict['on_time'].append(entry.on_time)
        ppm_dict['late'].append(entry.late)
        ppm_dict['ppm'].append(entry.ppm)
        ppm_dict['rolling_ppm'].append(entry.rolling_ppm)

    # Crete df and only return entries from last 24 hours
    df = pd.DataFrame.from_dict(ppm_dict)
    df = df[df.date >= (int(time.time()) - 86400)]
    return df


df = get_df()
db.create_all()


@server.route('/db_refresh')
def db_refresh():
    db.drop_all()
    db.create_all()
    return "Database refreshed."


app.layout = html.Div([
    html.Button('Update', id='update-button'),
    dcc.Graph(
        id='number-graph',
        figure={
            'data': [
                {'x': df['timestamp'], 'y': df['total'],
                 'type': 'scatter', 'name': 'Total'},
                {'x': df['timestamp'], 'y': df['on_time'],
                 'type': 'scatter', 'name': 'On Time'},
                {'x': df['timestamp'], 'y': df['late'],
                 'type': 'scatter', 'name': 'Late'}
            ],
            'layout': {
                'title': 'Current Train Totals'
            }
        }
    ),
    dcc.Graph(
        id='ppm-graph',
        figure={
            'data': [
                {'x': df['timestamp'], 'y': df['ppm'],
                 'type': 'scatter', 'name': 'PPM'},
                {'x': df['timestamp'], 'y': df['rolling_ppm'],
                 'type': 'scatter', 'name': 'Rolling PPM'},
            ],
            'layout': {
                'title': 'Public Performance Measure (PPM)'
            }
        }
    )
])


@app.callback(
    [dash.dependencies.Output('number-graph', 'figure'),
     dash.dependencies.Output('ppm-graph', 'figure')],
    [dash.dependencies.Input('update-button', 'n_clicks')])
def update_graph(n_clicks):
    df = get_df()
    return [
        {
            'data': [
                {'x': df['timestamp'], 'y': df['total'],
                 'type': 'scatter', 'name': 'Total'},
                {'x': df['timestamp'], 'y': df['on_time'],
                 'type': 'scatter', 'name': 'On Time'},
                {'x': df['timestamp'], 'y': df['late'],
                 'type': 'scatter', 'name': 'Late'}
            ],
            'layout': {
                'title': 'Current Train Totals'
            }
        },
        {
            'data': [
                {'x': df['timestamp'], 'y': df['ppm'],
                 'type': 'scatter', 'name': 'PPM'},
                {'x': df['timestamp'], 'y': df['rolling_ppm'],
                 'type': 'scatter', 'name': 'Rolling PPM'},
            ],
            'layout': {
                'title': 'Public Performance Measure (PPM)'
            }
        }
    ]


if __name__ == '__main__':
    app.run_server(debug=True)
