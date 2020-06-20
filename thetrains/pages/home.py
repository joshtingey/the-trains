# -*- coding: utf-8 -*-

"""Home page layout module."""

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from thetrains.app import app


def body():
    """Get map page body.

    Returns:
        html.Div: dash layout
    """
    edges = app.graph.edges
    graph_map = go.Figure(
        go.Scattermapbox(
            mode="lines",
            lat=edges["lat"].tolist(),
            lon=edges["lon"].tolist(),
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
        )
    )

    nodes = app.graph.nodes
    graph_map.add_trace(
        go.Scattermapbox(
            mode="markers",
            lat=nodes["lat"].tolist(),
            lon=nodes["lon"].tolist(),
            marker=go.scattermapbox.Marker(size=9),
            hovertext=nodes["name"].tolist(),
            hoverinfo="text",
        )
    )

    graph_map.update_layout(
        autosize=True,
        height=800,
        hovermode="closest",
        showlegend=False,
        mapbox=dict(
            accesstoken=app.server.config["MAPBOX_TOKEN"],
            style="streets",
            pitch=0,
            zoom=10,
            center=go.layout.mapbox.Center(lat=53.4771, lon=-2.2297),
        ),
    )

    body = dbc.Container(
        [
            dbc.Row(dbc.Col(dcc.Graph(figure=graph_map))),
            dcc.Interval(
                id="home-interval", interval=1 * 10000, n_intervals=0  # in milliseconds
            ),
        ],
        fluid=True,
    )
    return body
