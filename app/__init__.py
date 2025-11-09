from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

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
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(tracking_bp)
    app.register_blueprint(clients_bp)
    
    return app