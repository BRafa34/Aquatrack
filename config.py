import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-aquatrack-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:SILVANITA16@localhost:5432/AquaTrack_BD'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuraciones de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False