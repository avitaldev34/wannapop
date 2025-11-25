import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Clau secreta per sessions i Flask-Login
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

    # Base de dades SQLite (assegura que la carpeta existeix)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "sqlite", "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mostrar SQL generat (configurable per entorn)
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False") == "True"

    # Debug Toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_ENABLED = os.getenv("DEBUG_TB_ENABLED", "False") == "True"

    # Carpeta per pujar fitxers (avatars, fotos de productes)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

    # Nivell de logs
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
