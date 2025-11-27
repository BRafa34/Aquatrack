from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Order, Client
from app.models import Depot
from datetime import datetime
from sqlalchemy import or_

drivers_bp = Blueprint('drivers', __name__, url_prefix='/drivers')


@drivers_bp.route('/')
@login_required
def driver_dashboard():
    """Vista principal del conductor - lista de pedidos asignados"""
    if current_user.role != 'driver':
        flash('Acceso denegado. Solo para conductores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Obtener pedidos asignados al conductor o pendientes sin asignar
    orders = Order.query.filter(
        or_(
            Order.driver_id == current_user.id,
            db.and_(Order.driver_id.is_(None), Order.status.in_(['pending', 'assigned']))
        )
    ).order_by(Order.delivery_date.asc(), Order.created_at.desc()).all()
    
    return render_template('drivers/orders.html', orders=orders)


@drivers_bp.route('/map')
@login_required
def driver_map():
    """Vista del mapa con pedidos del conductor"""
    if current_user.role != 'driver':
        flash('Acceso denegado. Solo para conductores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Obtener pedidos asignados al conductor o pendientes
    orders = Order.query.filter(
        or_(
            Order.driver_id == current_user.id,
            db.and_(Order.driver_id.is_(None), Order.status.in_(['pending', 'assigned']))
        )
    ).all()
    
    # Preparar datos para el mapa
    orders_data = []
    for order in orders:
        if order.client:
            orders_data.append({
                'id': order.id,
                'client_name': order.client.name,
                'address': order.client.address or '',
                'lat': float(order.client.lat),
                'lon': float(order.client.lon),
                'status': order.status,
                'delivery_date': order.delivery_date.strftime('%Y-%m-%d') if order.delivery_date else '',
                'total_amount': str(order.total_amount) if order.total_amount else '0'
            })

    # Obtener almacenes para usar como punto de inicio de ruta
    depots = Depot.query.all()
    depots_data = []
    for depot in depots:
        if depot.lat and depot.lon:
            depots_data.append({
                'id': depot.id,
                'name': depot.name,
                'address': depot.address or '',
                'lat': float(depot.lat),
                'lon': float(depot.lon)
            })

    if not depots_data:
        depots_data = [{
            'id': 0,
            'name': 'Almacén Principal',
            'address': 'Cochabamba',
            'lat': -17.3935,
            'lon': -66.1570
        }]

    return render_template('drivers/map.html', orders=orders_data, depots=depots_data)


@drivers_bp.route('/order/<int:order_id>/deliver', methods=['POST'])
@login_required
def mark_delivered(order_id):
    """Marcar un pedido como entregado"""
    if current_user.role != 'driver':
        flash('Acceso denegado. Solo para conductores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    order = Order.query.get_or_404(order_id)
    
    # Verificar que el pedido esté asignado al conductor o esté pendiente
    if order.driver_id and order.driver_id != current_user.id:
        flash('No tienes permiso para modificar este pedido.', 'error')
        return redirect(url_for('drivers.driver_dashboard'))
    
    # Asignar el pedido al conductor si no está asignado
    if not order.driver_id:
        order.driver_id = current_user.id
    
    # Marcar como entregado
    order.status = 'delivered'
    order.delivered_at = datetime.utcnow()
    
    db.session.commit()
    flash('Pedido marcado como entregado exitosamente.', 'success')
    
    return redirect(url_for('drivers.driver_dashboard'))


@drivers_bp.route('/order/<int:order_id>/report-error', methods=['GET', 'POST'])
@login_required
def report_error(order_id):
    """Reportar un error en un pedido"""
    if current_user.role != 'driver':
        flash('Acceso denegado. Solo para conductores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    order = Order.query.get_or_404(order_id)
    
    # Verificar que el pedido esté asignado al conductor o esté pendiente
    if order.driver_id and order.driver_id != current_user.id:
        flash('No tienes permiso para modificar este pedido.', 'error')
        return redirect(url_for('drivers.driver_dashboard'))
    
    if request.method == 'POST':
        error_notes = request.form.get('error_notes', '').strip()
        
        if not error_notes:
            flash('Por favor, describe el error ocurrido.', 'error')
            return render_template('drivers/report_error.html', order=order)
        
        # Asignar el pedido al conductor si no está asignado
        if not order.driver_id:
            order.driver_id = current_user.id
        
        # Guardar las notas del error
        order.driver_notes = error_notes
        order.status = 'cancelled'  # Cambiar estado a cancelado por error
        
        db.session.commit()
        flash('Error reportado exitosamente.', 'success')
        
        return redirect(url_for('drivers.driver_dashboard'))
    
    return render_template('drivers/report_error.html', order=order)

