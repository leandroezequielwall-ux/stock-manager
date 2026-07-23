from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """
    Decorador genérico que restringe el acceso a uno o más roles.
    Ejemplo: @role_required('Administrador', 'Supervisor')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth_bp.login'))
            if current_user.rol not in roles and current_user.rol != 'Administrador':
                # Nota: 'Administrador' siempre tiene acceso si usamos este bypass,
                # pero para ser estrictos con *roles, lo incluiremos en las llamadas.
                # Para evitar confusión, si 'Administrador' debe tener acceso global,
                # lo permitimos explícitamente.
                if current_user.rol != 'Administrador':
                    flash('No tenés permisos suficientes para realizar esta acción.', 'danger')
                    return redirect(url_for('dashboard_bp.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Mantiene compatibilidad hacia atrás, equivalente a @role_required('Administrador').
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'Administrador':
            flash('No tenés permisos suficientes para realizar esta acción. Requerido: Administrador.', 'danger')
            return redirect(url_for('dashboard_bp.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    """
    Decorador para el panel global. Solo permite acceso al dueño del sistema.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'SuperAdmin':
            flash('Acceso denegado. Se requieren privilegios de SuperAdmin.', 'danger')
            return redirect(url_for('dashboard_bp.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def plan_feature_required(feature_name):
    """
    Verifica si la empresa del usuario tiene acceso a una característica específica según su plan.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth_bp.login'))
            
            if current_user.rol == 'SuperAdmin':
                return f(*args, **kwargs)
                
            from app.models import Empresa
            from app.utils.planes import PLANES_LIMITES
            from app.utils.security import get_empresa_id
            
            empresa_id = get_empresa_id()
            empresa = Empresa.query.get(empresa_id)
            if not empresa:
                flash('Empresa no encontrada.', 'danger')
                return redirect(url_for('dashboard_bp.dashboard'))
                
            plan_actual = empresa.plan
            limites = PLANES_LIMITES.get(plan_actual, PLANES_LIMITES['Starter'])
            
            if not limites.get(feature_name, False):
                flash(f'Tu plan {plan_actual} no incluye acceso a esta funcionalidad ({feature_name}).', 'warning')
                return redirect(url_for('dashboard_bp.dashboard'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
