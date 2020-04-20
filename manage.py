from flask_script import Manager
from thetrains.index import app, server

manager = Manager(server)


@manager.command
def run():
    "Run the app in debug mode"
    app.run_server(debug=True, port=8000)


@manager.command
def drop_ppm():
    "Clear the mongo db ppm data"
    app.mongo.drop("ppm")
    return "PPM data dropped"


@manager.command
def drop_td():
    "Clear the mongo db td data"
    app.mongo.drop("td")
    return "TD data dropped"


if __name__ == "__main__":
    manager.run()
