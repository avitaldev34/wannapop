from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler

from config import Config
from .extensions import db, login_manager

# Importem els blueprints correctament
from .routes_users import bp_users
from .routes_products import bp_products
from .routes_main import bp as main_bp
from .routes_auth import bp as auth_bp
from .routes_block_products import bp_block_products

toolbar = DebugToolbarExtension()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Clau secreta per sessions
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = "supersecretkey"

    # Inicialitzar extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Configuració de Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Debug Toolbar
    if app.config.get("DEBUG_TB_ENABLED", False):
        toolbar.init_app(app)

    # Configuració de logs
    log_handler = RotatingFileHandler("app.log", maxBytes=10240, backupCount=3)
    log_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    ))
    log_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(log_handler)
    app.logger.propagate = False  

    log_level = app.config.get("LOG_LEVEL", "DEBUG")
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError("Nivell de registre no vàlid")
    app.logger.setLevel(getattr(logging, log_level))

    # Registrar blueprints
    app.register_blueprint(bp_users)
    app.register_blueprint(bp_products)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(bp_block_products)

    return app
