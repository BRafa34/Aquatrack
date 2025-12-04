from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import DiscountRule, Product
from .forms import DiscountRuleForm

discounts_bp = Blueprint('discounts', __name__, url_prefix='/discounts')


@discounts_bp.route('/')
@login_required
def list_discounts():
    rules = DiscountRule.query.order_by(DiscountRule.product_id).all()
    return render_template('discounts/list.html', rules=rules)


@discounts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_discount():
    form = DiscountRuleForm()
    form.product_id.choices = [(p.id, p.name) for p in Product.query.filter_by(active=True).order_by(Product.name).all()]
    
    if form.validate_on_submit():
        rule = DiscountRule(
            product_id=form.product_id.data,
            min_quantity=form.min_quantity.data,
            discount_percent=form.discount_percent.data,
            active=form.active.data if form.active.data is not None else True
        )
        db.session.add(rule)
        db.session.commit()
        flash('Regla de descuento creada', 'success')
        return redirect(url_for('discounts.list_discounts'))
    
    form.active.data = True
    return render_template('discounts/form.html', form=form, is_edit=False)


@discounts_bp.route('/<int:rule_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_discount(rule_id):
    rule = DiscountRule.query.get_or_404(rule_id)
    form = DiscountRuleForm()
    form.product_id.choices = [(p.id, p.name) for p in Product.query.filter_by(active=True).order_by(Product.name).all()]
    
    if form.validate_on_submit():
        rule.product_id = form.product_id.data
        rule.min_quantity = form.min_quantity.data
        rule.discount_percent = form.discount_percent.data
        rule.active = form.active.data if form.active.data is not None else True
        db.session.commit()
        flash('Regla de descuento actualizada', 'success')
        return redirect(url_for('discounts.list_discounts'))
    
    form.product_id.data = rule.product_id
    form.min_quantity.data = rule.min_quantity
    form.discount_percent.data = rule.discount_percent
    form.active.data = rule.active
    
    return render_template('discounts/form.html', form=form, is_edit=True, rule=rule)


@discounts_bp.route('/<int:rule_id>/delete', methods=['POST'])
@login_required
def delete_discount(rule_id):
    rule = DiscountRule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()
    flash('Regla de descuento eliminada', 'success')
    return redirect(url_for('discounts.list_discounts'))
