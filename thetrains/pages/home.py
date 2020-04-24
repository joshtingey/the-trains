import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


def body():
    """
    Get homepage body.

    Returns:
        dbc.Container: Dash layout
    """
    body = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Heading"),
                html.P("hello hello hello")
            ], md=4,),
            dbc.Col([
                html.H2("Graph"),
                dcc.Graph(
                    figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
                ),
            ]),
        ])
    ], className="mt-4")
    return body
