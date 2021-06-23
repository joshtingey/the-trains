# -*- coding: utf-8 -*-

"""Graph page layout module."""

import datetime

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

from app import app


def get_sizes():
    """Get the sizes of the nodes given frequency of use.

    Returns:
        dict: dict of node sizes
    """
    trains = app.mongo.get("TRAINS")
    if trains is None:
        return None

    # Get the current time and delta
    time_now = datetime.datetime.now()
    time_delta = datetime.timedelta(hours=1)

    # Get counts of trains passing through berths in the past hour
    usage = {}
    for train in trains:
        for time, berth in zip(train["TIMES"], train["BERTHS"]):
            if berth not in usage:
                usage[berth] = 0
            if (time_now - time) < time_delta:
                usage[berth] += 1

    # Get the sizes by scaling and applying a minimum
    scale = 1
    min_size = 5
    sizes = {}
    for key, value in usage.items():
        sizes[key] = (value * scale) + min_size

    return usage, sizes


def get_berths():
    """Get the nodes and edges of the graph as dataframes.

    Returns:
        pd.DataFrame: nodes dataframe
        pd.DataFrame: edges dataframe
    """
    usage, sizes = get_sizes()
    if sizes is None:
        return None, None

    def apply_usage(node):
        """Get the count of how many trains have used berth in last hour.

        Returns:
            float: usage of the node
        """
        return usage[node["NAME"]]

    def apply_size(node):
        """Generate the size of the node from how frequently train use it.

        Returns:
            float: size for the node
        """
        return sizes[node["NAME"]]

    def apply_text(node):
        """Generate the hover text to display for each node.

        Returns:
            str: hover text for node
        """
        text = "TD area: " + str(node["NAME"])[:2] + "<br />"
        text = text + "Berth: " + str(node["NAME"])[2:] + "<br />"
        if str(node["DESCRIPTION"]) != "nan":
            text = text + "Description: " + str(node["DESCRIPTION"]) + "<br />"
        if node["FIXED"]:
            text = text + "Fixed: True" + "<br />"
        else:
            text = text + "Fixed: False" + "<br />"
        text = text + "Usage: " + str(node["USAGE"]) + " trains/hr<br />"
        text = text + "Updated: " + str(node["LATEST_TIME"]) + "<br />"

        if node["LATEST_TRAIN"] != "0000":
            text = text + "Train: " + str(node["LATEST_TRAIN"])
        return text

    def apply_colour(node):
        """Generate colour of each node.

        Returns:
            str: color for node
        """
        if node["LATEST_TRAIN"] == "0000":
            return "#263025"
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

    try:
        # Generate nodes dataframe
        nodes = pd.DataFrame.from_dict(selected, orient="index")
        nodes["FIXED"].fillna(False, inplace=True)
        nodes["COLOUR"] = nodes.apply(apply_colour, axis=1)
        nodes["SIZE"] = nodes.apply(apply_size, axis=1)
        nodes["USAGE"] = nodes.apply(apply_usage, axis=1)
        nodes["TEXT"] = nodes.apply(apply_text, axis=1)

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
                size=nodes["SIZE"].tolist(), color=nodes["COLOUR"].tolist(), opacity=0.7
            ),
            hovertext=nodes["TEXT"].tolist(),
            hoverinfo="text",
        )
    )

    # Update the mapbox layout
    graph_map.update_layout(
        autosize=True,
        height=1000,
        hovermode="closest",
        showlegend=False,
        mapbox=dict(
            accesstoken=app.server.config["DASH_MAPBOX_TOKEN"],
            style="light",
            pitch=0,
            zoom=9,
            center=go.layout.mapbox.Center(lat=53.3, lon=-2.5),  # 53.4771, -2.2297
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
                        dbc.CardBody(
                            [
                                html.P(
                                    "A graph of the UK rail network generated from \
                                individual train movements captured from the Network Rail feeds and a subset of known fixed locations. \
                                Each node represents a train describer 'berth' which usually, but not always, represents a signal.\
                                Red nodes indicate the live locations of trains on the network, \
                                whilst the node size indicates the frequency of usage. Hovering over each node provides additional information.\
                                The graph is updated every 5 seconds. \
                                Only the west coast mainline central signal area (around Manchester) is considered for now."
                                ),
                            ]
                        ),
                        color="secondary",
                    ),
                    width={"size": 10, "offset": 1},
                )
            ),
            dbc.Row(dbc.Col(dcc.Graph(id="graph-map", figure=graph_map))),
            dcc.Interval(
                id="graph-page-interval",
                interval=1 * 5000,
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
