# -*- coding: utf-8 -*-

import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from flask_sqlalchemy import SQLAlchemy

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

server.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    surname = db.Column(db.String())


@server.route('/db_test')
def db_test():
    status = 'old'
    db.create_all()
    user = User.query.first()
    if not user:
        u = User(name='The', surname='Trains')
        db.session.add(u)
        db.session.commit()
        status = 'new'
    user = User.query.first()
    return "User '{} {}' in database ({}). ".format(
        user.name, user.surname, status)


@server.route('/db_drop')
def db_drop():
    db.drop_all()
    return "All tables dropped."


app.layout = html.Div(children=[
    html.H1(children='thetrains'),

    html.Div(children='''
        thetrains dash application
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2],
                    'type': 'bar', 'name': 'Train1'},
                {'x': [1, 2, 3], 'y': [2, 4, 5],
                    'type': 'bar', 'name': 'Train2'},
            ],
            'layout': {
                'title': 'thetrains example visualisation'
            }
        }
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
