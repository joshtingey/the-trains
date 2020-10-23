# -*- coding: utf-8 -*-

"""Graph page layout module."""

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

from app import app


def get_berths():
    """Get the nodes and edges of the graph as dataframes.

    Returns:
        pd.DataFrame: nodes dataframe
        pd.DataFrame: edges dataframe
    """

    def apply_text(node):
        """Generate the hover text to display for each node.

        Returns:
            str: hover text for node
        """
        text = "Berth name: " + node["NAME"]

        if node["FIXED"]:
            text = text + ", Exact location: True"
        else:
            text = text + ", Exact location: False"

        if node["LATEST_TRAIN"] != "0000":
            text = text + ", Current train:" + node["LATEST_TRAIN"]
        return text

    def apply_colour(node):
        """Generate colour of each node.

        Returns:
            str: color for node
        """
        if node["LATEST_TRAIN"] == "0000":
            return "#AFD275"
        else:
            return "#E7717D"

    if app.mongo is None:
        return None, None

    berths = app.mongo.get("BERTHS")
    if berths is None:
        return None, None

    selected = {}
    for b in berths:
        if "SELECTED" in list(b.keys()):
            if b["SELECTED"]:
                selected[b["NAME"]] = b

    # Generate nodes dataframe
    try:
        nodes = pd.DataFrame.from_dict(selected, orient="index")
        nodes["FIXED"].fillna(False, inplace=True)
        nodes["TEXT"] = nodes.apply(apply_text, axis=1)
        nodes["COLOUR"] = nodes.apply(apply_colour, axis=1)

        # Generate edges dataframe
        lat, lon = [], []
        for name, data in selected.items():
            if "EDGES" in list(data.keys()):
                for edge in data["EDGES"][0]:
                    if edge in selected:
                        lat.append(data["LATITUDE"])
                        lat.append(selected[edge]["LATITUDE"])
                        lat.append(None)
                        lon.append(data["LONGITUDE"])
                        lon.append(selected[edge]["LONGITUDE"])
                        lon.append(None)
        edges = pd.DataFrame({"LATITUDE": lat, "LONGITUDE": lon})
    except Exception as e:
        app.logger.warning("Could not generate berths from database data: {}".format(e))
        return None, None

    return nodes, edges


def get_graph_map():
    """Get the graph rail network mapbox map.

    Returns:
        go.Figure: Scattermapbox of rail network graph
    """
    # Get the nodes and edges and pandas dataframes from the database
    nodes, edges = get_berths()
    if nodes is None or edges is None:
        return None

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
            accesstoken=app.server.config["DASH_MAPBOX_TOKEN"],
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
    graph_map = get_graph_map()
    if graph_map is None:
        return html.Div(
            dbc.Alert("Cannot retrieve data! Try again later!", color="danger")
        )

    # Put everything in a dcc container and return
    body = dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        "This map displays the generated 'graph' of the UK rail network. \
                            Red markers indicate a current train location. \
                            It is updated every 30 seconds.",
                        body=True,
                    ),
                    width={"size": 6, "offset": 3},
                )
            ),
            dbc.Row(dbc.Col(dcc.Graph(id="graph-map", figure=graph_map))),
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
