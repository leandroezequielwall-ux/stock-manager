from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.es_admin:
            flash('No tenés permisos suficientes para realizar esta acción.', 'danger')
            return redirect(url_for('dashboard_bp.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
