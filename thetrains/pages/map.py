import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

from thetrains.app import app


def body():
    """
    Get map page body.

    Returns:
        html.Div: Dash layout
    """
    df = px.data.carshare()
    px.set_mapbox_access_token(app.server.config['MAPBOX_TOKEN'])
    fig = px.scatter_mapbox(df, lat="centroid_lat", lon="centroid_lon",
                            color="peak_hour", size="car_hours",
                            color_continuous_scale=px.colors.cyclical.IceFire,
                            size_max=15, zoom=10)
    body = html.Div([
        dcc.Graph(figure=fig)
    ])
    return body
