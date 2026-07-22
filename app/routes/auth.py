from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from app.models import Usuario

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
                
            login_user(user)
            return redirect(url_for('dashboard_bp.dashboard'))
        else:
            flash('Email o contraseña incorrectos.', 'danger')
            
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))
