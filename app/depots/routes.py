from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Depot
from .forms import DepotForm

depots_bp = Blueprint('depots', __name__, url_prefix='/depots')


@depots_bp.route('/')
@login_required
def list_depots():
    """Lista todos los almacenes"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    depots = Depot.query.order_by(Depot.id.desc()).all()
    return render_template('depots/list.html', depots=depots)


@depots_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_depot():
    """Crear un nuevo almacén"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = DepotForm()
    if form.validate_on_submit():
        depot = Depot(
            name=form.name.data,
            address=form.address.data,
            lat=form.lat.data,
            lon=form.lon.data,
            notes=form.notes.data
        )
        db.session.add(depot)
        db.session.commit()
        flash('Almacén creado exitosamente.', 'success')
        return redirect(url_for('depots.list_depots'))
    
    return render_template('depots/edit.html', form=form, is_edit=False)


@depots_bp.route('/<int:depot_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_depot(depot_id):
    """Editar un almacén existente"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    depot = Depot.query.get_or_404(depot_id)
    form = DepotForm(obj=depot)
    
    if form.validate_on_submit():
        depot.name = form.name.data
        depot.address = form.address.data
        depot.lat = form.lat.data
        depot.lon = form.lon.data
        depot.notes = form.notes.data
        
        db.session.commit()
        flash('Almacén actualizado exitosamente.', 'success')
        return redirect(url_for('depots.list_depots'))
    
    return render_template('depots/edit.html', form=form, is_edit=True, depot=depot)


@depots_bp.route('/<int:depot_id>/delete', methods=['POST'])
@login_required
def delete_depot(depot_id):
    """Eliminar un almacén"""
    if current_user.role != 'admin':
        flash('Acceso denegado. Solo para administradores.', 'error')
        return redirect(url_for('main.dashboard'))
    
    depot = Depot.query.get_or_404(depot_id)
    db.session.delete(depot)
    db.session.commit()
    flash('Almacén eliminado exitosamente.', 'success')
    return redirect(url_for('depots.list_depots'))

