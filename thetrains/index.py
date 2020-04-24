import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from thetrains.app import app
import thetrains.pages.home as home_page
import thetrains.pages.ppm as ppm_page
import thetrains.pages.map as map_page


server = app.server


def add_navbar(body):
    """
    Adds navbar to body

    Args:
        body (dash.layout): Dash layout
    Returns:
        dash.layout: Body with navbar
    """
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("PPM", href="/ppm")),
            dbc.NavItem(dbc.NavLink("Map", href="/map")),
        ],
        brand="thetrains",
        brand_href="/",
        sticky="top",
    )
    layout = html.Div([navbar, body])
    return layout


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    """
    Displays the correct page for the URL

    Args:
        pathname (str): URL pathname
    Returns:
        dash.layout: Layout for page
    """
    if pathname == '/':
        return add_navbar(home_page.body())
    elif pathname == '/ppm':
        return add_navbar(ppm_page.body())
    elif pathname == '/map':
        return add_navbar(map_page.body())
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
