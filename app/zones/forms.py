from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class ZoneForm(FlaskForm):
    name = StringField('Nombre de la Zona', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Descripción', validators=[Optional()])
    submit = SubmitField('Guardar')

