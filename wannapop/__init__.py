from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from .extensions import db
from .models import db as users_bp
from .models import db as products_bp
import logging
from logging.handlers import RotatingFileHandler
from config import Config
from .routes_auth import bp as auth_bp

toolbar = DebugToolbarExtension()

from .routes_users import bp as users_bp
from .routes_products import bp as products_bp
from .routes_main import bp as main_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    if app.config.get("DEBUG_TB_ENABLED", False):
        toolbar.init_app(app)

    log_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=3)
    log_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    log_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(log_handler)

    log_level = app.config.get('LOG_LEVEL', 'DEBUG')
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        raise ValueError('Nivell de registre no vàlid')
    app.logger.setLevel(getattr(logging, log_level))

    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp) 
    return app
