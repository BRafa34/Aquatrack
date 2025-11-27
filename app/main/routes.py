from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Client, Order, Vehicle, Zone, User
from datetime import datetime, date

# ✅ Blueprint para las rutas principales
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Redirigir conductores a su dashboard específico
    if current_user.role == 'driver':
        return redirect(url_for('drivers.driver_dashboard'))
    
    # Obtener estadísticas reales
    stats = {
        'active_clients': Client.query.filter_by(active=True).count(),
        'orders_today': Order.query.filter(
            Order.created_at >= datetime.combine(date.today(), datetime.min.time())
        ).count(),
        'total_vehicles': Vehicle.query.filter_by(active=True).count(),
        'total_zones': Zone.query.count(),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'assigned_orders': Order.query.filter_by(status='assigned').count(),
        'delivered_orders': Order.query.filter_by(status='delivered').count(),
        'total_drivers': User.query.filter_by(role='driver').count()
    }
    
    return render_template('dashboard.html', user=current_user, stats=stats)