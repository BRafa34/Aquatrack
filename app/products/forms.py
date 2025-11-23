from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class ProductForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=150)])
    sku = StringField('SKU', validators=[Optional(), Length(max=80)])
    price = DecimalField('Precio', validators=[Optional()])
    active = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar')
