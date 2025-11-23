from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Product
from .forms import ProductForm

products_bp = Blueprint('products', __name__, url_prefix='/products')


@products_bp.route('/')
@login_required
def list_products():
    products = Product.query.order_by(Product.name).all()
    return render_template('products/list.html', products=products)


@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        p = Product(name=form.name.data, sku=form.sku.data or None, price=form.price.data or None, active=form.active.data)
        db.session.add(p)
        db.session.commit()
        flash('Producto creado', 'success')
        return redirect(url_for('products.list_products'))
    return render_template('products/detail.html', form=form, is_edit=False)


@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.sku = form.sku.data or None
        product.price = form.price.data or None
        product.active = form.active.data
        db.session.commit()
        flash('Producto actualizado', 'success')
        return redirect(url_for('products.list_products'))
    return render_template('products/detail.html', form=form, is_edit=True, product=product)


@products_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Producto eliminado', 'success')
    return redirect(url_for('products.list_products'))
