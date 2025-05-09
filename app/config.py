import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ysecret-key")
    API_TOKEN = os.getenv("API_TOKEN", "secret-token-123")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://root:12345678@localhost/flask_api")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=10)  
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)    