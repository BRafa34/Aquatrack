from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional


class OrderForm(FlaskForm):
    client_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    delivery_date = DateField('Fecha de entrega', validators=[Optional()])
    items = TextAreaField('Items (JSON)', validators=[Optional()])
    total_amount = DecimalField('Monto total', validators=[Optional()])
    status = SelectField('Estado', choices=[('pending','pending'),('assigned','assigned'),('delivered','delivered'),('cancelled','cancelled')], validators=[DataRequired()])
    submit = SubmitField('Guardar')

