# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm # FlaskForm es una clase base que proporciona el paquete Flask-WTF para crear y manejar formularios web de manera segura y eficiente en aplicaciones Flask.
from wtforms import StringField, PasswordField, SubmitField, SelectField # importa los campos de formulario que se usan junto con FlaskForm. Campo de texto para entrada de una línea. Se renderiza como <input type="text"> Ideal para: nombres, emails, títulos, etc.
from wtforms.validators import DataRequired, Email, Length, EqualTo # importa validadores que aseguran que los datos del formulario sean correctos: DataRequired verifica que el campo no esté vacío, Email valida que el texto tenga formato de correo electrónico válido, Length controla que el texto tenga una longitud mínima y/o máxima específica, e EqualTo verifica que el valor de un campo sea igual al de otro campo.

class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')
    # esta clase crea los campos para el login usando los imports anteriores

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de Usuario', 
                          validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Correo Electrónico', 
                       validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', 
                            validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', 
                                   validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Rol', 
                  choices=[('admin', 'Administrador'), ('driver', 'Conductor')],
                  validators=[DataRequired()])
    submit = SubmitField('Registrarse')
    # esta clase crea los campos para el registro usando los imports anteriores