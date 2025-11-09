from flask import Blueprint, render_template
from flask_login import login_required

tracking_bp = Blueprint('tracking', __name__, url_prefix='/tracking')


@tracking_bp.route('/map')
@login_required
def map_view():
    # Vista simple con una imagen estática de mapa
    return render_template('tracking/map.html')

