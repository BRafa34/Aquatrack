from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class ClientForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    address = TextAreaField('Dirección', validators=[Optional()])
    lat = FloatField('Latitud', validators=[DataRequired(), NumberRange(min=-90, max=90)])
    lon = FloatField('Longitud', validators=[DataRequired(), NumberRange(min=-180, max=180)])
    phone = StringField('Teléfono', validators=[Optional()])
    notes = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Guardar')
