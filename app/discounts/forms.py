from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange

class DiscountRuleForm(FlaskForm):
    product_id = SelectField('Producto', coerce=int, validators=[DataRequired()])
    min_quantity = IntegerField('Cantidad mínima', validators=[DataRequired(), NumberRange(min=1)])
    discount_percent = FloatField('Porcentaje descuento (%)', validators=[DataRequired(), NumberRange(min=0.1, max=100)])
    active = BooleanField('Activo')
    submit = SubmitField('Guardar')
