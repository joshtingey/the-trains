# -*- coding: utf-8 -*-

"""PPM page layout module."""

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd

from app import app


def get_ppm_df():
    """Get a pandas dataframe containing all PPM data.

    Returns:
        pd.DataFrame: PPM Pandas dataframe
    """
    if app.mongo is None:
        return None

    docs = app.mongo.get("ppm")
    if docs is None:
        return None

    ppm_dict = {
        "date": [],
        "total": [],
        "on_time": [],
        "late": [],
        "ppm": [],
        "rolling_ppm": [],
    }

    for doc in app.mongo.get("ppm"):
        ppm_dict["date"].append(doc["date"])
        ppm_dict["total"].append(doc["total"])
        ppm_dict["on_time"].append(doc["on_time"])
        ppm_dict["late"].append(doc["late"])
        ppm_dict["ppm"].append(doc["ppm"])
        ppm_dict["rolling_ppm"].append(doc["rolling_ppm"])

    df = pd.DataFrame.from_dict(ppm_dict)
    return df


def body():
    """
    Get ppm page body.

    Returns:
        html.Div: Dash layout
    """
    df = get_ppm_df()
    if df is None:
        return html.Div(
            dbc.Alert("Cannot retrieve data! Try again later!", color="danger")
        )

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
