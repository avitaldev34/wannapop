from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler

from config import Config
from .extensions import db, login_manager
from flask_principal import Principal, identity_loaded, RoleNeed, UserNeed, AnonymousIdentity, Identity
from flask_login import current_user

# Importem els blueprints 
from .routes_users import bp_users
from .routes_products import bp_products
from .routes_main import bp as main_bp
from .routes_auth import bp as auth_bp
from .routes_block_products import bp_block_products   # blueprint de moderació de productes
from .routes_block_users import bp_block_users         # blueprint de moderació d’usuaris

toolbar = DebugToolbarExtension()
migrate = Migrate()
principals = Principal()


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
    
    # Flask-Principal
    principals.init_app(app)

    # 🔑 Carregar identitat en cada request
    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        if current_user.is_authenticated:
            identity.user = current_user
            # Afegim el rol actual del usuari
            if getattr(current_user, "role", None):
                identity.provides.add(RoleNeed(current_user.role.name))
            # Afegim també el seu UserNeed
            identity.provides.add(UserNeed(current_user.id))

    # Debug Toolbar (només si està activada a config)
    if app.config.get("DEBUG_TB_ENABLED", False):
        toolbar.init_app(app)

    # Configuració de logs amb rotació
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
    app.register_blueprint(bp_block_products)   # rutes de moderació de productes
    app.register_blueprint(bp_block_users)      # rutes de moderació d’usuaris

    return app
