from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.security import get_empresa_id
from app.extensions import db
from app.models import Producto, Movimiento
from app.services.stock_service import registrar_movimiento
from app.utils.decorators import role_required
from app.utils.auditoria import log_auditoria

movimientos_bp = Blueprint('movimientos_bp', __name__)

@movimientos_bp.route('/movimientos')
@login_required
def movimientos_lista():
    page = request.args.get('page', 1, type=int)
    tipo_filtro = request.args.get('tipo', '').strip().upper()
    per_page = 30

    empresa_id = get_empresa_id()
    query = Movimiento.query.filter_by(empresa_id=empresa_id)

    if tipo_filtro in ['ENTRADA', 'SALIDA']:
        query = query.filter(Movimiento.tipo == tipo_filtro)

    movimientos = query.order_by(Movimiento.fecha.desc()).paginate(page=page, per_page=per_page)

    return render_template('movimientos.html', 
                           movimientos=movimientos,
                           tipo_filtro=tipo_filtro)

@movimientos_bp.route('/productos/<int:id>/entrada', methods=['POST'])
@login_required
@role_required('Administrador', 'Supervisor', 'Operador')
def stock_entrada(id):
    empresa_id = get_empresa_id()
    producto = Producto.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()
    cantidad = request.form.get('cantidad', type=int)
    motivo = request.form.get('motivo', 'Entrada de stock').strip()

    if not cantidad or cantidad <= 0:
        flash('La cantidad debe ser mayor a cero.', 'danger')
        return redirect(url_for('productos_bp.producto_detalle', id=id))

    try:
        registrar_movimiento(producto, 'ENTRADA', cantidad, motivo)
        log_auditoria('CREAR', 'movimientos', None, {'producto_id': producto.id, 'tipo': 'ENTRADA', 'cantidad': cantidad})
        flash(f'Entrada registrada: +{cantidad} unidades de {producto.codigo}.', 'success')
    except Exception as e:
        flash(f'Error al registrar entrada: {e}', 'danger')

    return redirect(url_for('productos_bp.producto_detalle', id=id))

@movimientos_bp.route('/productos/<int:id>/salida', methods=['POST'])
@login_required
@role_required('Administrador', 'Supervisor', 'Operador')
def stock_salida(id):
    empresa_id = get_empresa_id()
    producto = Producto.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()
    cantidad = request.form.get('cantidad', type=int)
    motivo = request.form.get('motivo', 'Salida de stock').strip()

    if not cantidad or cantidad <= 0:
        flash('La cantidad debe ser mayor a cero.', 'danger')
        return redirect(url_for('productos_bp.producto_detalle', id=id))

    if producto.stock < cantidad:
        flash('Stock insuficiente para realizar esta salida.', 'danger')
        return redirect(url_for('productos_bp.producto_detalle', id=id))

    try:
        registrar_movimiento(producto, 'SALIDA', cantidad, motivo)
        log_auditoria('CREAR', 'movimientos', None, {'producto_id': producto.id, 'tipo': 'SALIDA', 'cantidad': cantidad})
        flash(f'Salida registrada: -{cantidad} unidades de {producto.codigo}.', 'success')
        
        # Alert if stock is low after sale
        if producto.stock <= producto.stock_minimo:
            flash(f'ATENCIÓN: {producto.codigo} tiene stock bajo ({producto.stock} unidades).', 'warning')
            
    except Exception as e:
        flash(f'Error al registrar salida: {e}', 'danger')

    return redirect(url_for('productos_bp.producto_detalle', id=id))
