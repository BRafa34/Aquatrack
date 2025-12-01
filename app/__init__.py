# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import inspect, text

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    
    # ✅ CONFIGURAR USER_LOADER (AGREGA ESTAS 4 LÍNEAS)
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Configurar Login Manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Registrar Blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.users.routes import users_bp
    from app.orders.routes import orders_bp
    from app.tracking.routes import tracking_bp
    from app.clients.routes import clients_bp
    from app.drivers.routes import drivers_bp
    from app.vehicles.routes import vehicles_bp
    from app.zones.routes import zones_bp
    from app.depots.routes import depots_bp
    from app.products.routes import products_bp
    from app.inventory.routes import inventory_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(drivers_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(zones_bp)
    app.register_blueprint(depots_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(inventory_bp)

    # --- Reparar esquema en caliente: añadir columna orders.zone_id si no existe ---
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            if 'orders' in inspector.get_table_names():
                cols = [c['name'] for c in inspector.get_columns('orders')]
                if 'zone_id' not in cols:
                    # Añadir columna nullable para no bloquear la app
                    with db.engine.begin() as conn:
                        conn.execute(text('ALTER TABLE orders ADD COLUMN zone_id INTEGER'))
                        # Si existe la tabla zones, intentar añadir constraint FK (silencioso si falla)
                        if 'zones' in inspector.get_table_names():
                            try:
                                conn.execute(text('ALTER TABLE orders ADD CONSTRAINT orders_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES zones (id)'))
                            except Exception:
                                pass
        except Exception as e:
            # No romper el arranque si algo falla; imprimir para debugging
            print('Warning: comprobación/esquema zone_id no completada:', e)
        # Crear tablas faltantes (products, zones, etc.) si no existen
        try:
            # Esto crea solo las tablas que faltan y no modifica tablas existentes
            db.create_all()
        except Exception as e:
            print('Warning: db.create_all() falló:', e)
        # Asegurar que columnas añadidas dinamicamente existen (para dev sin migraciones)
        try:
            inspector = inspect(db.engine)
            if 'products' in inspector.get_table_names():
                prod_cols = [c['name'] for c in inspector.get_columns('products')]
                with db.engine.begin() as conn:
                    if 'stock' not in prod_cols:
                        try:
                            conn.execute(text('ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT 0'))
                        except Exception as ex:
                            print('Warning: no se pudo añadir products.stock:', ex)
                    if 'sales_count' not in prod_cols:
                        try:
                            conn.execute(text('ALTER TABLE products ADD COLUMN sales_count INTEGER DEFAULT 0'))
                        except Exception as ex:
                            print('Warning: no se pudo añadir products.sales_count:', ex)
        except Exception as e:
            print('Warning: fallback chequeo columnas products falló:', e)
    
    return app