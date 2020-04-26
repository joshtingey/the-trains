# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


def body():
    """
    Get homepage body.

    Returns:
        dbc.Container: Dash layout
    """
    body = dbc.Container([
        dbc.Row([
            dbc.Col(
                [
                    html.H2("Pages"),
                    html.P("PPM, Map")
                ],
                width=4
            ),
            dbc.Col(
                [
                    html.H2("Graph"),
                    dcc.Graph(
                        figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
                    ),
                ],
                width=8
            ),
        ])
    ])
    return body
