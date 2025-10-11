# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Configuración de la aplicación
    app.config['SECRET_KEY'] = 'aquatrack-super-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:SILVANITA16@localhost:5432/AquaTrack_BD'#AQUI PONGAN SUS DATOS DE US BASE DE DATOS
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configurar Flask-Login
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    # Configurar user_loader (IMPORTANTE para Flask-Login)
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints (rutas)
    from app.routes import main
    app.register_blueprint(main)
    
    return app