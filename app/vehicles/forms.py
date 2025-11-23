from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from app.models import Zone


class VehicleForm(FlaskForm):
    name = StringField('Nombre del Vehículo', validators=[DataRequired(), Length(min=2, max=100)])
    license_plate = StringField('Placa', validators=[DataRequired(), Length(min=2, max=20)])
    zone_id = SelectField('Zona', coerce=int, validators=[Optional()])
    active = BooleanField('Activo', default=True)
    notes = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Guardar')
    
    def __init__(self, *args, **kwargs):
        super(VehicleForm, self).__init__(*args, **kwargs)
        # Cargar zonas para el select
        self.zone_id.choices = [(0, 'Sin zona')] + [(z.id, z.name) for z in Zone.query.order_by(Zone.name).all()]

