from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Order, Client
from .forms import OrderForm
import json

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


@orders_bp.route('/')
@login_required
def list_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('orders/list.html', orders=orders)


@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    form = OrderForm()
    form.client_id.choices = [(c.id, c.name) for c in Client.query.order_by(Client.name).all()]
    if form.validate_on_submit():
        items_json = None
        if form.items.data:
            try:
                items_json = json.loads(form.items.data)
            except Exception:
                flash('Items deben ser JSON válido', 'error')
                return render_template('orders/detail.html', form=form, is_edit=False)
        order = Order(
            client_id=form.client_id.data,
            delivery_date=form.delivery_date.data,
            items=items_json,
            total_amount=form.total_amount.data,
            status=form.status.data
        )
        db.session.add(order)
        db.session.commit()
        flash('Pedido creado', 'success')
        return redirect(url_for('orders.list_orders'))
    return render_template('orders/detail.html', form=form, is_edit=False)


@orders_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderForm(obj=order)
    form.client_id.choices = [(c.id, c.name) for c in Client.query.order_by(Client.name).all()]
    if form.validate_on_submit():
        order.client_id = form.client_id.data
        order.delivery_date = form.delivery_date.data
        order.total_amount = form.total_amount.data
        order.status = form.status.data
        order.items = None
        if form.items.data:
            try:
                order.items = json.loads(form.items.data)
            except Exception:
                flash('Items deben ser JSON válido', 'error')
                return render_template('orders/detail.html', form=form, is_edit=True)
        db.session.commit()
        flash('Pedido actualizado', 'success')
        return redirect(url_for('orders.list_orders'))
    form.items.data = json.dumps(order.items, ensure_ascii=False) if order.items else ''
    return render_template('orders/detail.html', form=form, is_edit=True)


@orders_bp.route('/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Pedido eliminado', 'success')
    return redirect(url_for('orders.list_orders'))

