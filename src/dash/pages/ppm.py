# -*- coding: utf-8 -*-

"""PPM page layout module."""

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app


def body():
    """
    Get ppm page body.

    Returns:
        html.Div: Dash layout
    """
    df = app.mongo.get_ppm_df()
    if df is None:
        return html.Div(dbc.Alert("This is a danger alert. Scary!", color="danger"))

    body = dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id="number-graph",
                        figure={
                            "data": [
                                {
                                    "x": df["date"],
                                    "y": df["total"],
                                    "type": "scatter",
                                    "name": "Total",
                                },
                                {
                                    "x": df["date"],
                                    "y": df["on_time"],
                                    "type": "scatter",
                                    "name": "On Time",
                                },
                                {
                                    "x": df["date"],
                                    "y": df["late"],
                                    "type": "scatter",
                                    "name": "Late",
                                },
                            ],
                            "layout": {"title": "Current Train Totals"},
                        },
                    ),
                    width=12,
                )
            ),
            dbc.Row(
                dbc.Col(
                    dcc.Graph(
                        id="ppm-graph",
                        figure={
                            "data": [
                                {
                                    "x": df["date"],
                                    "y": df["ppm"],
                                    "type": "scatter",
                                    "name": "PPM",
                                },
                                {
                                    "x": df["date"],
                                    "y": df["rolling_ppm"],
                                    "type": "scatter",
                                    "name": "Rolling PPM",
                                },
                            ],
                            "layout": {"title": "Public Performance Measure (PPM)"},
                        },
                    ),
                    width=12,
                )
            ),
        ],
        fluid=True,
    )
    return body
