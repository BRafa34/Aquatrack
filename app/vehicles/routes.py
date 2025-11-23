from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Vehicle, Zone, User
from .forms import VehicleForm

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')


@vehicles_bp.route('/')
@login_required
def list_vehicles():
    """Lista todos los vehículos"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    vehicles = Vehicle.query.order_by(Vehicle.id.desc()).all()
    # Obtener información adicional de cada vehículo
    vehicles_data = []
    for vehicle in vehicles:
        driver = User.query.filter_by(vehicle_id=vehicle.id).first()
        zone = Zone.query.get(vehicle.zone_id) if vehicle.zone_id else None
        vehicles_data.append({
            'vehicle': vehicle,
            'driver': driver,
            'zone': zone
        })
    
    return render_template('vehicles/list.html', vehicles_data=vehicles_data)


@vehicles_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_vehicle():
    """Crear un nuevo vehículo"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = VehicleForm()
    if form.validate_on_submit():
        # Verificar si la placa ya existe
        existing = Vehicle.query.filter_by(license_plate=form.license_plate.data).first()
        if existing:
            flash('Ya existe un vehículo con esa placa.', 'error')
            return render_template('vehicles/edit.html', form=form, is_edit=False)
        
        vehicle = Vehicle(
            name=form.name.data,
            license_plate=form.license_plate.data,
            zone_id=form.zone_id.data if form.zone_id.data != 0 else None,
            active=form.active.data,
            notes=form.notes.data
        )
        db.session.add(vehicle)
        db.session.commit()
        flash('Vehículo creado exitosamente.', 'success')
        return redirect(url_for('vehicles.list_vehicles'))
    
    return render_template('vehicles/edit.html', form=form, is_edit=False)


@vehicles_bp.route('/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    """Editar un vehículo existente"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = VehicleForm(obj=vehicle)
    
    if form.validate_on_submit():
        # Verificar si la placa ya existe en otro vehículo
        existing = Vehicle.query.filter(
            Vehicle.license_plate == form.license_plate.data,
            Vehicle.id != vehicle_id
        ).first()
        if existing:
            flash('Ya existe otro vehículo con esa placa.', 'error')
            return render_template('vehicles/edit.html', form=form, is_edit=True, vehicle=vehicle)
        
        vehicle.name = form.name.data
        vehicle.license_plate = form.license_plate.data
        vehicle.zone_id = form.zone_id.data if form.zone_id.data != 0 else None
        vehicle.active = form.active.data
        vehicle.notes = form.notes.data
        
        db.session.commit()
        flash('Vehículo actualizado exitosamente.', 'success')
        return redirect(url_for('vehicles.list_vehicles'))
    
    # Establecer el valor por defecto para zone_id
    form.zone_id.data = vehicle.zone_id if vehicle.zone_id else 0
    
    return render_template('vehicles/edit.html', form=form, is_edit=True, vehicle=vehicle)


@vehicles_bp.route('/<int:vehicle_id>/delete', methods=['POST'])
@login_required
def delete_vehicle(vehicle_id):
    """Eliminar un vehículo"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Verificar si hay conductores asignados a este vehículo
    drivers = User.query.filter_by(vehicle_id=vehicle_id).all()
    if drivers:
        flash(f'No se puede eliminar el vehículo. Tiene {len(drivers)} conductor(es) asignado(s).', 'error')
        return redirect(url_for('vehicles.list_vehicles'))
    
    db.session.delete(vehicle)
    db.session.commit()
    flash('Vehículo eliminado exitosamente.', 'success')
    return redirect(url_for('vehicles.list_vehicles'))

