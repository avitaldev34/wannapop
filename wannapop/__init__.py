from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

db = SQLAlchemy()
toolbar = DebugToolbarExtension()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")

    db.init_app(app)
    toolbar.init_app(app)

    from .routes_products import products
    from .routes_users import users

    app.register_blueprint(products)
    app.register_blueprint(users)

    return app
