# -*- coding: utf-8 -*-

"""Graph page layout module."""

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from thetrains_app.app import app


def get_graph_map():
    """Get the graph rail network mapbox map.

    Returns:
        go.Figure: Scattermapbox of rail network graph
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
            line=dict(width=1.0, color="#888"),
            hoverinfo="none",
        )
    )

    # Plot the nodes with markers depending on if a train is present
    graph_map.add_trace(
        go.Scattermapbox(
            mode="markers",
            lat=nodes["LATITUDE"].tolist(),
            lon=nodes["LONGITUDE"].tolist(),
            marker=go.scattermapbox.Marker(
                size=12, color=nodes["COLOUR"].tolist(), opacity=0.7
            ),
            hovertext=nodes["TEXT"].tolist(),
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

    graph_map["layout"]["uirevision"] = "constant"
    return graph_map


def body():
    """Get map page body.

    Returns:
        html.Div: dash layout
    """
    # Put everything in a dcc container and return
    body = dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        "This map displays the generated 'graph' of the UK rail network. \
                            Red markers indicate a current train location.",
                        body=True,
                    ),
                    width={"size": 6, "offset": 3},
                )
            ),
            dbc.Row(dbc.Col(dcc.Graph(id="graph-map", figure=get_graph_map()))),
            dcc.Interval(
                id="graph-page-interval",
                interval=1 * 30000,
                n_intervals=0,  # in milliseconds
            ),
        ],
        fluid=True,
    )
    return body


@app.callback(
    Output("graph-map", "figure"), [Input("graph-page-interval", "n_intervals")]
)
def update_graph_map(n):
    """Update the graph rail network mapbox map.

    Returns:
        go.Figure: Scattermapbox of rail network graph
    """
    return get_graph_map()
