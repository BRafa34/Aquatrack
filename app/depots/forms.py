from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class DepotForm(FlaskForm):
    name = StringField('Nombre del Almacén', validators=[DataRequired(), Length(min=2, max=100)])
    address = TextAreaField('Dirección', validators=[Optional()])
    lat = FloatField('Latitud', validators=[DataRequired(), NumberRange(min=-90, max=90)])
    lon = FloatField('Longitud', validators=[DataRequired(), NumberRange(min=-180, max=180)])
    notes = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Guardar')

