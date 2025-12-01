# -*- coding: utf-8 -*-
from app import db #maneja la info de la base de datos
from datetime import datetime #maneja fechas y horas
from werkzeug.security import generate_password_hash, check_password_hash #maneja la seguridad de las contraseñas
from flask_login import UserMixin #proporciona funcionalidades de usuario para la autenticación y gestión de sesiones en aplicaciones Flask.

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='admin')  # 'admin' or 'driver'
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relación con vehículos (opcional para conductores)
    vehicle = db.relationship('Vehicle', backref='driver', foreign_keys=[vehicle_id])

#esta clase define la estructura de la tabla de usuarios en la base de datos usando SQLAlchemy
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
#esta función genera un hash seguro de la contraseña y lo almacena en la base de datos
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
#esta función verifica si la contraseña proporcionada coincide con el hash almacenado en la base de datos
    
    def __repr__(self):
        return f'<User {self.username}>'
#esta función define cómo se representa un objeto User cuando se imprime o se muestra, útil para depuración y registros.

# Modelos adicionales que necesitarás eventualmente, no tomar importancia de momento, es para mas adelante. Lo necesario para el login y registro ya está arriba.
class Zone(db.Model):
    __tablename__ = 'zones'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    license_plate = db.Column(db.String(20), unique=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'))
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'))
    phone = db.Column(db.String(20))
    active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Depot(db.Model):
    __tablename__ = 'depots'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.Text)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    notes = db.Column(db.Text)


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(80), unique=True)
    price = db.Column(db.Numeric, nullable=True)
    active = db.Column(db.Boolean, default=True)
    stock = db.Column(db.Integer, default=0)
    sales_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_time = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.Date)
    delivered_at = db.Column(db.DateTime, nullable=True)
    items = db.Column(db.JSON)
    total_amount = db.Column(db.Numeric)
    status = db.Column(db.String(20), default='pending')  # pending|assigned|delivered|cancelled
    driver_notes = db.Column(db.Text, nullable=True)  # Notas del conductor sobre errores o problemas

    client = db.relationship('Client', backref='orders')
    driver = db.relationship('User', backref='assigned_orders', foreign_keys=[driver_id])
    zone = db.relationship('Zone', backref='orders')