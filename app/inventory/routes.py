from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.models import Product
from app import db

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')


@inventory_bp.route('/')
@login_required
def dashboard():
    # Resumen del inventario: total productos, productos en bajo stock, top vendidos
    products = Product.query.order_by(Product.name).all()
    top_products = Product.query.order_by(Product.sales_count.desc()).limit(5).all()
    low_stock = Product.query.filter(Product.stock <= 5).order_by(Product.stock.asc()).all()
    total_stock_value = 0
    for p in products:
        try:
            total_stock_value += (p.stock or 0) * (float(p.price) if p.price else 0)
        except Exception:
            pass

    return render_template('inventory/dashboard.html', products=products, top_products=top_products, low_stock=low_stock, total_stock_value=total_stock_value)


@inventory_bp.route('/adjust', methods=['POST'])
@login_required
def adjust_stock():
    data = request.form
    product_id = data.get('product_id')
    delta = int(data.get('delta', 0))
    if not product_id:
        flash('Producto inválido', 'error')
        return redirect(url_for('inventory.dashboard'))
    p = Product.query.get(product_id)
    if not p:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('inventory.dashboard'))

    p.stock = (p.stock or 0) + delta
    if p.stock < 0:
        p.stock = 0
    db.session.commit()
    flash('Stock actualizado', 'success')
    return redirect(url_for('inventory.dashboard'))
