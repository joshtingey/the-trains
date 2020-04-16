# -*- coding: utf-8 -*-

import os
import datetime
import time
import logging
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import plotly.express as px


log = logging.getLogger(__name__)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
px.set_mapbox_access_token(os.getenv('MAPBOX_TOKEN'))

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'thetrains'
server = app.server

db_url = 'postgresql://{}:{}@postgres:5432/{}'.format(
    os.getenv('DB_USER'), os.getenv('DB_PASS'), os.getenv('DB_NAME'))

server.config['SQLALCHEMY_DATABASE_URI'] = db_url
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
        timestamp = datetime.datetime.fromtimestamp(entry.date)
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


map_df = px.data.carshare()
map_fig = px.scatter_mapbox(map_df, lat="centroid_lat", lon="centroid_lon",
                            color="peak_hour", size="car_hours",
                            color_continuous_scale=px.colors.cyclical.IceFire,
                            size_max=15, zoom=10)


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
    ),
    dcc.Graph(figure=map_fig)
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


def setup_logging():
    """Setup logging and stdout printing"""
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)


def main():
    """Main function called when app starts."""
    setup_logging()
    app.run_server(debug=True)


if __name__ == '__main__':
    main()
