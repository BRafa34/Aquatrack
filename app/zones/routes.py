from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Zone, Vehicle, Client
from .forms import ZoneForm

zones_bp = Blueprint('zones', __name__, url_prefix='/zones')


@zones_bp.route('/')
@login_required
def list_zones():
    """Lista todas las zonas"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    zones = Zone.query.order_by(Zone.name).all()
    # Obtener información adicional de cada zona
    zones_data = []
    for zone in zones:
        vehicles_count = Vehicle.query.filter_by(zone_id=zone.id).count()
        clients_count = Client.query.filter_by(zone_id=zone.id).count()
        zones_data.append({
            'zone': zone,
            'vehicles_count': vehicles_count,
            'clients_count': clients_count
        })
    
    return render_template('zones/list.html', zones_data=zones_data)


@zones_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_zone():
    """Crear una nueva zona"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = ZoneForm()
    if form.validate_on_submit():
        # Verificar si la zona ya existe
        existing = Zone.query.filter_by(name=form.name.data).first()
        if existing:
            flash('Ya existe una zona con ese nombre.', 'error')
            return render_template('zones/edit.html', form=form, is_edit=False)
        
        zone = Zone(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(zone)
        db.session.commit()
        flash('Zona creada exitosamente.', 'success')
        return redirect(url_for('zones.list_zones'))
    
    return render_template('zones/edit.html', form=form, is_edit=False)


@zones_bp.route('/<int:zone_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_zone(zone_id):
    """Editar una zona existente"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    zone = Zone.query.get_or_404(zone_id)
    form = ZoneForm(obj=zone)
    
    if form.validate_on_submit():
        # Verificar si el nombre ya existe en otra zona
        existing = Zone.query.filter(
            Zone.name == form.name.data,
            Zone.id != zone_id
        ).first()
        if existing:
            flash('Ya existe otra zona con ese nombre.', 'error')
            return render_template('zones/edit.html', form=form, is_edit=True, zone=zone)
        
        zone.name = form.name.data
        zone.description = form.description.data
        
        db.session.commit()
        flash('Zona actualizada exitosamente.', 'success')
        return redirect(url_for('zones.list_zones'))
    
    return render_template('zones/edit.html', form=form, is_edit=True, zone=zone)


@zones_bp.route('/<int:zone_id>/delete', methods=['POST'])
@login_required
def delete_zone(zone_id):
    """Eliminar una zona"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    zone = Zone.query.get_or_404(zone_id)
    
    # Verificar si hay vehículos o clientes asignados a esta zona
    vehicles_count = Vehicle.query.filter_by(zone_id=zone_id).count()
    clients_count = Client.query.filter_by(zone_id=zone_id).count()
    
    if vehicles_count > 0 or clients_count > 0:
        flash(f'No se puede eliminar la zona. Tiene {vehicles_count} vehículo(s) y {clients_count} cliente(s) asignado(s).', 'error')
        return redirect(url_for('zones.list_zones'))
    
    db.session.delete(zone)
    db.session.commit()
    flash('Zona eliminada exitosamente.', 'success')
    return redirect(url_for('zones.list_zones'))

