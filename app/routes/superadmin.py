from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Empresa, Usuario, Producto, Movimiento
from app.utils.decorators import superadmin_required

superadmin_bp = Blueprint('superadmin_bp', __name__)

@superadmin_bp.route('/sysadmin/empresas')
@login_required
@superadmin_required
def empresas_lista():
    empresas = Empresa.query.order_by(Empresa.fecha_alta.desc()).all()
    
    # Calcular métricas para cada empresa
    metricas = {}
    for emp in empresas:
        usuarios_count = emp.usuarios.count()
        productos_count = emp.productos.count()
        
        # Último acceso (del último login de algún usuario de la empresa)
        ultimo_usuario = emp.usuarios.order_by(Usuario.ultimo_login.desc()).first()
        ultimo_acceso = ultimo_usuario.ultimo_login if ultimo_usuario and ultimo_usuario.ultimo_login else None
        
        # Espacio utilizado aproximado (suma de productos y movimientos)
        espacio = productos_count + emp.movimientos.count()
        
        metricas[emp.id] = {
            'usuarios': usuarios_count,
            'productos': productos_count,
            'ultimo_acceso': ultimo_acceso,
            'espacio': espacio
        }

    return render_template('superadmin/empresas.html', empresas=empresas, metricas=metricas)

@superadmin_bp.route('/sysadmin/empresas/<int:id>/estado', methods=['POST'])
@login_required
@superadmin_required
def empresa_estado(id):
    empresa = Empresa.query.get_or_404(id)
    nuevo_estado = request.form.get('estado')
    if nuevo_estado in ['Activa', 'Suspendida']:
        empresa.estado = nuevo_estado
        db.session.commit()
        flash(f'Estado de la empresa {empresa.nombre} cambiado a {nuevo_estado}.', 'success')
    return redirect(url_for('superadmin_bp.empresas_lista'))

@superadmin_bp.route('/sysadmin/empresas/<int:id>/plan', methods=['POST'])
@login_required
@superadmin_required
def empresa_plan(id):
    empresa = Empresa.query.get_or_404(id)
    nuevo_plan = request.form.get('plan')
    if nuevo_plan in ['Starter', 'Pro', 'Enterprise']:
        empresa.plan = nuevo_plan
        db.session.commit()
        flash(f'Plan de la empresa {empresa.nombre} cambiado a {nuevo_plan}.', 'success')
    return redirect(url_for('superadmin_bp.empresas_lista'))

@superadmin_bp.route('/sysadmin/empresas/<int:id>/eliminar', methods=['POST'])
@login_required
@superadmin_required
def empresa_eliminar(id):
    empresa = Empresa.query.get_or_404(id)
    nombre = empresa.nombre
    # SQLAlchemy cascada eliminará usuarios, productos, etc.
    db.session.delete(empresa)
    db.session.commit()
    flash(f'Empresa {nombre} eliminada por completo del sistema.', 'success')
    return redirect(url_for('superadmin_bp.empresas_lista'))
