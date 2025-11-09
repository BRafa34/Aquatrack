from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Client
from .forms import ClientForm

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')


@clients_bp.route('/')
@login_required
def list_clients():
    clients = Client.query.order_by(Client.id.desc()).all()
    return render_template('clients/list.html', clients=clients)


@clients_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_client():
    form = ClientForm()
    if form.validate_on_submit():
        client = Client(
            name=form.name.data,
            address=form.address.data,
            lat=form.lat.data,
            lon=form.lon.data,
            phone=form.phone.data,
            notes=form.notes.data
        )
        db.session.add(client)
        db.session.commit()
        flash('Cliente creado', 'success')
        return redirect(url_for('clients.list_clients'))
    return render_template('clients/edit.html', form=form, is_edit=False)


@clients_bp.route('/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    form = ClientForm(obj=client)
    if form.validate_on_submit():
        client.name = form.name.data
        client.address = form.address.data
        client.lat = form.lat.data
        client.lon = form.lon.data
        client.phone = form.phone.data
        client.notes = form.notes.data
        db.session.commit()
        flash('Cliente actualizado', 'success')
        return redirect(url_for('clients.list_clients'))
    return render_template('clients/edit.html', form=form, is_edit=True)


@clients_bp.route('/<int:client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash('Cliente eliminado', 'success')
    return redirect(url_for('clients.list_clients'))
