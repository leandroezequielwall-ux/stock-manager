from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from werkzeug.security import check_password_hash
from datetime import datetime
from app.extensions import db
from app.models import Usuario, Empresa, Categoria
from app.utils.auditoria import log_auditoria

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.activo:
                flash('Esta cuenta ha sido desactivada.', 'danger')
                return redirect(url_for('auth_bp.login'))
                
            user.ultimo_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user)
            log_auditoria('LOGIN', 'usuarios', user.id, 'Inicio de sesión exitoso')
            return redirect(url_for('dashboard_bp.dashboard'))
        else:
            flash('Email o contraseña incorrectos.', 'danger')
            
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        log_auditoria('LOGOUT', 'usuarios', current_user.id, 'Cierre de sesión')
    logout_user()
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre_empresa = request.form.get('nombre_empresa', '').strip()
        cuit = request.form.get('cuit', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        plan = request.form.get('plan', 'Starter')

        if not nombre_empresa or not email or not password:
            flash('Por favor completa todos los campos requeridos.', 'warning')
            return redirect(url_for('auth_bp.registro'))

        # Check if email exists in any company (emails should be globally unique for login)
        if Usuario.query.filter_by(email=email).first():
            flash('Ese email ya está registrado en el sistema.', 'danger')
            return redirect(url_for('auth_bp.registro'))

        try:
            # 1. Crear Empresa
            empresa = Empresa(
                nombre=nombre_empresa,
                razon_social=nombre_empresa,
                cuit=cuit or None,
                plan=plan
            )
            db.session.add(empresa)
            db.session.flush() # Para obtener el ID de la empresa

            # 2. Crear Usuario Administrador
            admin = Usuario(
                nombre="Administrador",
                email=email,
                rol='Administrador',
                empresa_id=empresa.id
            )
            admin.set_password(password)
            db.session.add(admin)

            # 3. Crear configuración inicial (Categoría "General")
            cat_general = Categoria(
                nombre="General",
                descripcion="Categoría creada por defecto",
                empresa_id=empresa.id
            )
            db.session.add(cat_general)

            db.session.commit()

            # Auto-login
            admin.ultimo_login = datetime.utcnow()
            db.session.commit()
            
            login_user(admin)
            log_auditoria('CREAR', 'empresas', empresa.id, f'Empresa registrada: {empresa.nombre}')
            log_auditoria('LOGIN', 'usuarios', admin.id, 'Inicio de sesión (Registro)')
            
            flash('¡Registro exitoso! Bienvenido a Stock Manager.', 'success')
            return redirect(url_for('dashboard_bp.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error durante el registro: {str(e)}', 'danger')
            return redirect(url_for('auth_bp.registro'))

    return render_template('registro.html')

