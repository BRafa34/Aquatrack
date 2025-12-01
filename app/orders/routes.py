from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Order, Client, Zone, Product
from .forms import OrderForm
import json


def get_products_json():
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    return [
        {
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'price': float(p.price) if p.price is not None else None,
            'stock': int(p.stock) if p.stock is not None else 0
        }
        for p in products
    ]

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
    form.zone_id.choices = [(z.id, z.name) for z in Zone.query.order_by(Zone.name).all()]
    if form.validate_on_submit():
        items_json = None
        if form.items.data:
            try:
                items_json = json.loads(form.items.data)
            except Exception:
                flash('Items deben ser JSON válido', 'error')
                return render_template('orders/detail.html', form=form, is_edit=False, products=get_products_json())

        # Validar stock disponible
        adjustments = []  # (product, delta) where delta = new_qty - old_qty (for create old=0)
        if items_json:
            for it in items_json:
                pid = it.get('product_id')
                qty = int(it.get('qty', 0))
                if not pid or qty <= 0:
                    flash('Producto inválido o cantidad no válida', 'error')
                    return render_template('orders/detail.html', form=form, is_edit=False, products=get_products_json())
                prod = Product.query.get(pid)
                if not prod:
                    flash(f'Producto con id {pid} no encontrado', 'error')
                    return render_template('orders/detail.html', form=form, is_edit=False, products=get_products_json())
                if (prod.stock or 0) < qty:
                    flash(f'No hay stock suficiente para {prod.name} (disponible: {prod.stock})', 'error')
                    return render_template('orders/detail.html', form=form, is_edit=False, products=get_products_json())
                adjustments.append((prod, qty))

        order = Order(
            client_id=form.client_id.data,
            zone_id=form.zone_id.data,
            delivery_date=form.delivery_date.data,
            items=items_json,
            total_amount=form.total_amount.data,
            status=form.status.data
        )
        db.session.add(order)
        try:
            for prod, delta in adjustments:
                prod.stock = (prod.stock or 0) - delta
                prod.sales_count = (prod.sales_count or 0) + delta
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Ocurrió un error aplicando los ajustes de stock', 'error')
            return render_template('orders/detail.html', form=form, is_edit=False, products=get_products_json())
        flash('Pedido creado', 'success')
        return redirect(url_for('orders.list_orders'))
    products = get_products_json()
    return render_template('orders/detail.html', form=form, is_edit=False, products=products)


@orders_bp.route('/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderForm(obj=order)
    form.client_id.choices = [(c.id, c.name) for c in Client.query.order_by(Client.name).all()]
    form.zone_id.choices = [(z.id, z.name) for z in Zone.query.order_by(Zone.name).all()]
    if form.validate_on_submit():
        order.client_id = form.client_id.data
        order.zone_id = form.zone_id.data
        order.delivery_date = form.delivery_date.data
        order.total_amount = form.total_amount.data
        order.status = form.status.data
        old_items = order.items or []
        new_items = None
        if form.items.data:
            try:
                new_items = json.loads(form.items.data)
            except Exception:
                flash('Items deben ser JSON válido', 'error')
                return render_template('orders/detail.html', form=form, is_edit=True, products=get_products_json())
        order.items = new_items
        # Calcular deltas para ajuste de stock
        adjustments = []
        try:
            old_map = {}
            new_map = {}
            for it in old_items:
                pid = it.get('product_id')
                old_map[pid] = old_map.get(pid, 0) + int(it.get('qty', 0))
            if new_items:
                for it in new_items:
                    pid = it.get('product_id')
                    new_map[pid] = new_map.get(pid, 0) + int(it.get('qty', 0))
            pids = set(list(old_map.keys()) + list(new_map.keys()))
            for pid in pids:
                old_q = old_map.get(pid, 0)
                new_q = new_map.get(pid, 0)
                delta = new_q - old_q
                if delta == 0:
                    continue
                prod = Product.query.get(pid)
                if not prod:
                    flash(f'Producto con id {pid} no encontrado', 'error')
                    return render_template('orders/detail.html', form=form, is_edit=True, products=get_products_json())
                if delta > 0 and (prod.stock or 0) < delta:
                    flash(f'No hay stock suficiente para {prod.name} (disponible: {prod.stock})', 'error')
                    return render_template('orders/detail.html', form=form, is_edit=True, products=Product.query.filter_by(active=True).order_by(Product.name).all())
                adjustments.append((prod, delta))
        except Exception:
            adjustments = []
        # no commit yet; we'll apply adjustments and commit atomically
        # aplicar ajustes en stock
        try:
            for prod, delta in adjustments:
                prod.stock = (prod.stock or 0) - delta
                prod.sales_count = (prod.sales_count or 0) + delta
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Ocurrió un error al actualizar stock en la edición', 'error')
            return render_template('orders/detail.html', form=form, is_edit=True, products=get_products_json())
        flash('Pedido actualizado', 'success')
        return redirect(url_for('orders.list_orders'))
    form.items.data = json.dumps(order.items, ensure_ascii=False) if order.items else ''
    products = get_products_json()
    return render_template('orders/detail.html', form=form, is_edit=True, products=products)


@orders_bp.route('/<int:order_id>/delete', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Pedido eliminado', 'success')
    return redirect(url_for('orders.list_orders'))

