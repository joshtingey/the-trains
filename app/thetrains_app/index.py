# -*- coding: utf-8 -*-

"""Module to initialise the multipage dash application."""

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from thetrains_app.app import app
import thetrains_app.pages.graph as graph_page
import thetrains_app.pages.ppm as ppm_page


server = app.server
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)


def add_navbar(body):
    """Add navbar to body.

    Args:
        body (dash.layout): dash layout
    Returns:
        dash.layout: body with navbar
    """
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Graph", href="/")),
            dbc.NavItem(dbc.NavLink("PPM", href="/ppm")),
        ],
        brand="thetrains",
        brand_href="/",
        sticky="top",
    )
    layout = html.Div([navbar, body])
    return layout


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    """Display the correct page for the URL.

    Args:
        pathname (str): URL pathname
    Returns:
        dash.layout: layout for page
    """
    if pathname == "/":
        return add_navbar(graph_page.body())
    elif pathname == "/ppm":
        return add_navbar(ppm_page.body())
    else:
        return "404"


if __name__ == "__main__":
    app.run_server(debug=True, port=8000)
