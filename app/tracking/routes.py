from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models import Order, Client, Depot

tracking_bp = Blueprint('tracking', __name__, url_prefix='/tracking')


@tracking_bp.route('/map')
@login_required
def map_view():
    """Vista del mapa con todos los pedidos, clientes y almacenes para administradores"""
    # Obtener todos los pedidos
    orders = Order.query.all()
    
    # Preparar datos para el mapa
    orders_data = []
    for order in orders:
        if order.client:
            orders_data.append({
                'id': order.id,
                'type': 'order',
                'client_name': order.client.name,
                'address': order.client.address or '',
                'lat': float(order.client.lat),
                'lon': float(order.client.lon),
                'status': order.status,
                'delivery_date': order.delivery_date.strftime('%Y-%m-%d') if order.delivery_date else '',
                'total_amount': str(order.total_amount) if order.total_amount else '0',
                'driver_name': order.driver.username if order.driver else 'Sin asignar'
            })
    
    # Obtener todos los clientes
    clients = Client.query.filter_by(active=True).all()
    clients_data = []
    for client in clients:
        clients_data.append({
            'id': client.id,
            'type': 'client',
            'name': client.name,
            'address': client.address or '',
            'lat': float(client.lat),
            'lon': float(client.lon),
            'phone': client.phone or ''
        })
    
    # Obtener todos los almacenes
    depots = Depot.query.all()
    depots_data = []
    for depot in depots:
        if depot.lat and depot.lon:
            depots_data.append({
                'id': depot.id,
                'type': 'depot',
                'name': depot.name,
                'address': depot.address or '',
                'lat': float(depot.lat),
                'lon': float(depot.lon)
            })
    
    # Si no hay almacenes, usar uno por defecto en Cochabamba
    if not depots_data:
        depots_data = [{
            'id': 0,
            'type': 'depot',
            'name': 'Almacén Principal',
            'address': 'Cochabamba',
            'lat': -17.3935,
            'lon': -66.1570
        }]
    
    return render_template('tracking/map.html', 
                         orders=orders_data, 
                         clients=clients_data, 
                         depots=depots_data)


@tracking_bp.route('/route', methods=['POST'])
@login_required
def get_route():
    """Obtener ruta optimizada desde almacén a pedidos"""
    data = request.get_json()
    depot_id = data.get('depot_id')
    order_ids = data.get('order_ids', [])
    
    # Obtener almacén
    depot = Depot.query.get(depot_id) if depot_id else None
    if not depot or not depot.lat or not depot.lon:
        # Usar almacén por defecto
        depot_lat, depot_lon = -17.3935, -66.1570
    else:
        depot_lat, depot_lon = float(depot.lat), float(depot.lon)
    
    # Obtener pedidos
    orders = Order.query.filter(Order.id.in_(order_ids)).all() if order_ids else []
    waypoints = []
    
    for order in orders:
        if order.client:
            waypoints.append({
                'lat': float(order.client.lat),
                'lon': float(order.client.lon),
                'name': order.client.name
            })
    
    return jsonify({
        'depot': {'lat': depot_lat, 'lon': depot_lon},
        'waypoints': waypoints
    })

