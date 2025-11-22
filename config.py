import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "sqlite", "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_ENABLED = os.getenv("DEBUG_TB_ENABLED", "False") == "True"
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
