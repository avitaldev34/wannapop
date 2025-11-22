import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = "sqlite:///sqlite/database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_ENABLED = os.getenv("DEBUG_TB_ENABLED", "False") == "True"

    # Nivell de registre
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()