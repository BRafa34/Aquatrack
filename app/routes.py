from flask import Blueprint, render_template, redirect, url_for, flash, request #estos son imports necesarios para manejar rutas, renderizar plantillas HTML, redirigir usuarios, mostrar mensajes flash y manejar solicitudes HTTP en Flask.
from flask_login import login_user, logout_user, login_required, current_user# estos imports son necesarios para manejar la autenticación de usuarios y sesiones en Flask.
from app.forms import LoginForm, RegistrationForm# estos imports son necesarios para manejar los formularios de login y registro definidos en forms.py
from app.models import User# estos imports son necesarios para manejar el modelo de usuario definido en models.py
from app import db#este import es necesario para manejar la base de datos usando SQLAlchemy

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está logueado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Buscar usuario por email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Verificar si el usuario existe y la contraseña es correcta
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Email o contraseña incorrectos', 'Intente de nuevo')
    
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    # Si el usuario ya está logueado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('El email ya está registrado', 'error')
            return render_template('register.html', form=form)
        
        # Verificar si el username ya existe
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('El nombre de usuario ya está en uso', 'error')
            return render_template('register.html', form=form)
        
        # Crear nuevo usuario
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        new_user.set_password(form.password.data)
        
        # Guardar en la base de datos
        db.session.add(new_user)
        db.session.commit()
        
        flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('main.index'))