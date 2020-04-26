# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_bootstrap_components as dbc
# import plotly.express as px
import plotly.graph_objects as go

from thetrains.app import app


def body():
    """
    Get map page body.

    Returns:
        html.Div: Dash layout
    """
    pos_dict = app.network.get_positions()

    edge_trace = go.Scatter(
        x=pos_dict['edge_x'], y=pos_dict['edge_y'],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_trace = go.Scatter(
        x=pos_dict['node_x'], y=pos_dict['node_y'],
        mode='markers',
        hoverinfo='text'
    )

    node_text = []
    for node, adjacencies in enumerate(pos_dict['names']):
        node_text.append('Name: ' + str(adjacencies))

    node_trace.text = node_text

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )

    # df = px.data.carshare()
    # px.set_mapbox_access_token(app.server.config['MAPBOX_TOKEN'])
    # fig = px.scatter_mapbox(df, lat="centroid_lat", lon="centroid_lon",
    #                         color="peak_hour", size="car_hours",
    #                         color_continuous_scale=px.colors.cyclical.IceFire,
    #                         size_max=15, zoom=10)

    body = dbc.Container(
        dbc.Row(
            dbc.Col(
                dcc.Graph(figure=fig),
                width=12
            )
        )
    )
    return body
