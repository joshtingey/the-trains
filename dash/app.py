# -*- coding: utf-8 -*-

from decouple import config
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

from common.config import config_dict
from common.mongo import Mongo

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'thetrains'
server = app.server

conf = config_dict[config("ENV", cast=str, default="local")]
conf.init_logging(app.logger)
app.logger.removeHandler(app.logger.handlers[0])

mongo = Mongo(app.logger, conf)
px.set_mapbox_access_token(conf.MAPBOX_TOKEN)


def get_df():
    ppm_dict = {
        'date': [],
        'total': [],
        'on_time': [],
        'late': [],
        'ppm': [],
        'rolling_ppm': []
    }

    for doc in mongo.get("ppm"):
        ppm_dict['date'].append(doc['date'])
        ppm_dict['total'].append(doc['total'])
        ppm_dict['on_time'].append(doc['on_time'])
        ppm_dict['late'].append(doc['late'])
        ppm_dict['ppm'].append(doc['ppm'])
        ppm_dict['rolling_ppm'].append(doc['rolling_ppm'])

    df = pd.DataFrame.from_dict(ppm_dict)
    return df


df = get_df()


@server.route('/db_drop_all')
def db_refresh():
    mongo.drop_all()
    return "All collections dropped"


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
                {'x': df['date'], 'y': df['total'],
                 'type': 'scatter', 'name': 'Total'},
                {'x': df['date'], 'y': df['on_time'],
                 'type': 'scatter', 'name': 'On Time'},
                {'x': df['date'], 'y': df['late'],
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
                {'x': df['date'], 'y': df['ppm'],
                 'type': 'scatter', 'name': 'PPM'},
                {'x': df['date'], 'y': df['rolling_ppm'],
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
                {'x': df['date'], 'y': df['total'],
                 'type': 'scatter', 'name': 'Total'},
                {'x': df['date'], 'y': df['on_time'],
                 'type': 'scatter', 'name': 'On Time'},
                {'x': df['date'], 'y': df['late'],
                 'type': 'scatter', 'name': 'Late'}
            ],
            'layout': {
                'title': 'Current Train Totals'
            }
        },
        {
            'data': [
                {'x': df['date'], 'y': df['ppm'],
                 'type': 'scatter', 'name': 'PPM'},
                {'x': df['date'], 'y': df['rolling_ppm'],
                 'type': 'scatter', 'name': 'Rolling PPM'},
            ],
            'layout': {
                'title': 'Public Performance Measure (PPM)'
            }
        }
    ]


if __name__ == '__main__':
    app.run_server()
