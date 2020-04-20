import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from thetrains.app import app


def body():
    df = app.mongo.get_ppm_df()
    body = html.Div([
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
        )
    ])
    return body


@app.callback(
    [Output('number-graph', 'figure'),
     Output('ppm-graph', 'figure')],
    [Input('update-button', 'n_clicks')])
def update_graph(n_clicks):
    df = app.mongo.get_ppm_df()
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
