from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from config import Config
import logging
from logging.handlers import RotatingFileHandler



db = SQLAlchemy()
toolbar = DebugToolbarExtension()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicialitzar base de dades
    db.init_app(app)

    # Inicialitzar Debug Toolbar
    if app.config["DEBUG_TB_ENABLED"]:
        toolbar.init_app(app)

        # --- Configuració de logging ---
    log_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=3)
    log_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    log_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(log_handler)

    # Aplicar nivell de registre des de config
    log_level = app.config.get('LOG_LEVEL')
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        raise ValueError('Nivell de registre no vàlid')
    app.logger.setLevel(getattr(logging, log_level))

    # Registrar blueprints
    from .routes_users import bp as users_bp
    from .routes_products import bp as products_bp
    from .routes_main import bp as main_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(main_bp)

    return app
