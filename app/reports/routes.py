from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from app.models import Order, Product
from sqlalchemy import func
from datetime import date, datetime, timedelta
from flask import request
from calendar import monthrange

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
def dashboard():
    # Totales generales
    total_sales = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar() or 0
    total_orders = db.session.query(func.count(Order.id)).scalar() or 0

    # Pedidos por día últimos 14 días
    start_dt = datetime.combine(date.today() - timedelta(days=13), datetime.min.time())
    orders_per_day_q = db.session.query(
        func.date(Order.created_at).label('day'),
        func.count(Order.id).label('count')
    ).filter(Order.created_at >= start_dt).group_by(func.date(Order.created_at)).order_by(func.date(Order.created_at)).all()
    orders_per_day = [{'day': r.day.strftime('%Y-%m-%d'), 'count': r.count} for r in orders_per_day_q]

    # Top productos por ventas (sales_count)
    top_products = Product.query.order_by(Product.sales_count.desc()).limit(10).all()

    return render_template('reports/dashboard.html',
                           total_sales=float(total_sales),
                           total_orders=total_orders,
                           orders_per_day=orders_per_day,
                           top_products=top_products,
                           now_year=date.today().year,
                           now_month=date.today().month)


@reports_bp.route('/monthly')
@login_required
def monthly_report():
    # Parámetros month/year opcionales
    try:
        year = int(request.args.get('year', date.today().year))
        month = int(request.args.get('month', date.today().month))
    except Exception:
        year = date.today().year
        month = date.today().month

    # rango inicio/fin
    start_date = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    # Pedidos en el mes (por created_at)
    orders = Order.query.filter(func.date(Order.created_at) >= start_date, func.date(Order.created_at) <= end_date).order_by(Order.created_at).all()

    total_sales = sum([float(o.total_amount or 0) for o in orders])
    total_orders = len(orders)

    # Agregar resumen por producto leyendo items JSON
    prod_map = {}
    for o in orders:
        items = o.items or []
        for it in items:
            try:
                pid = it.get('product_id')
                qty = int(it.get('qty', 0))
                price = float(it.get('price') or 0)
            except Exception:
                continue
            if not pid:
                continue
            if pid not in prod_map:
                prod_map[pid] = {'qty': 0, 'revenue': 0.0}
            prod_map[pid]['qty'] += qty
            prod_map[pid]['revenue'] += qty * price

    # Cargar nombres/sku de productos
    product_summary = []
    if prod_map:
        pids = list(prod_map.keys())
        prods = Product.query.filter(Product.id.in_(pids)).all()
        prod_by_id = {p.id: p for p in prods}
        for pid, data in prod_map.items():
            p = prod_by_id.get(pid)
            product_summary.append({
                'id': pid,
                'name': p.name if p else f'ID {pid}',
                'sku': p.sku if p else '',
                'qty': data['qty'],
                'revenue': data['revenue']
            })

    product_summary.sort(key=lambda x: x['qty'], reverse=True)

    return render_template('reports/monthly.html', year=year, month=month, total_sales=total_sales,
                           total_orders=total_orders, orders=orders, product_summary=product_summary,
                           current_time=datetime.now().strftime('%Y-%m-%d %H:%M'))
