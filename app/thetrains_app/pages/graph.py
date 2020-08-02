# -*- coding: utf-8 -*-

"""Graph page layout module."""

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go

from thetrains_app.app import app


def set_colour(x):
    """Map a bool to a color.

    Returns:
        bool: color dependent on input
    """
    if x == "0000":
        return "#AFD275"
    else:
        return "#E7717D"


def body():
    """Get map page body.

    Returns:
        html.Div: dash layout
    """
    # Get the nodes and edges and pandas dataframes from the database
    nodes, edges = app.mongo.get_berths()
    if nodes is None or edges is None:
        return html.Div(dbc.Alert("This is a danger alert. Scary!", color="danger"))

    # Plot the edges as lines between the nodes
    graph_map = go.Figure(
        go.Scattermapbox(
            mode="lines",
            lat=edges["LATITUDE"].tolist(),
            lon=edges["LONGITUDE"].tolist(),
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
        )
    )

    # Plot the nodes with markers depending on if a train is present
    graph_map.add_trace(
        go.Scattermapbox(
            mode="markers",
            lat=nodes["LATITUDE"].tolist(),
            lon=nodes["LONGITUDE"].tolist(),
            marker=dict(
                size=9, color=list(map(set_colour, nodes["LATEST_DESCR"].tolist()))
            ),
            # hovertext=nodes.index.values.tolist(),
            hovertext=nodes["LATEST_DESCR"].tolist(),
            hoverinfo="text",
        )
    )

    # Update the mapbox layout
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

    # Put everything in a dcc container and return
    body = dbc.Container(
        [
            dbc.Row(dbc.Col(dcc.Graph(figure=graph_map))),
            dcc.Interval(
                id="graph-interval",
                interval=1 * 10000,
                n_intervals=0,  # in milliseconds
            ),
        ],
        fluid=True,
    )
    return body
