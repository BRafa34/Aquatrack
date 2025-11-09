from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class UserForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[Optional(), Email()])
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6)])
    role = SelectField('Rol', choices=[('admin', 'Admin'), ('driver', 'Driver')], validators=[DataRequired()])
    submit = SubmitField('Guardar')

