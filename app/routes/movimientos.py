from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Producto, Movimiento
from app.services.stock_service import registrar_movimiento

movimientos_bp = Blueprint('movimientos_bp', __name__)

@movimientos_bp.route('/movimientos')
@login_required
def movimientos_lista():
    page = request.args.get('page', 1, type=int)
    tipo_filtro = request.args.get('tipo', '').strip().upper()
    per_page = 30

    query = Movimiento.query

    if tipo_filtro in ['ENTRADA', 'SALIDA']:
        query = query.filter(Movimiento.tipo == tipo_filtro)

    movimientos = query.order_by(Movimiento.fecha.desc()).paginate(page=page, per_page=per_page)

    return render_template('movimientos.html', 
                           movimientos=movimientos,
                           tipo_filtro=tipo_filtro)

@movimientos_bp.route('/productos/<int:id>/entrada', methods=['POST'])
@login_required
def stock_entrada(id):
    producto = Producto.query.get_or_404(id)
    cantidad = request.form.get('cantidad', type=int)
    motivo = request.form.get('motivo', 'Entrada de stock').strip()

    if not cantidad or cantidad <= 0:
        flash('La cantidad debe ser mayor a cero.', 'danger')
        return redirect(url_for('productos_bp.producto_detalle', id=id))

    try:
        registrar_movimiento(producto, 'ENTRADA', cantidad, motivo)
        flash(f'Entrada registrada: +{cantidad} unidades de {producto.codigo}.', 'success')
    except Exception as e:
        flash(f'Error al registrar entrada: {e}', 'danger')

    return redirect(url_for('productos_bp.producto_detalle', id=id))

@movimientos_bp.route('/productos/<int:id>/salida', methods=['POST'])
@login_required
def stock_salida(id):
    producto = Producto.query.get_or_404(id)
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
        flash(f'Salida registrada: -{cantidad} unidades de {producto.codigo}.', 'success')
        
        # Alert if stock is low after sale
        if producto.stock <= producto.stock_minimo:
            flash(f'ATENCIÓN: {producto.codigo} tiene stock bajo ({producto.stock} unidades).', 'warning')
            
    except Exception as e:
        flash(f'Error al registrar salida: {e}', 'danger')

    return redirect(url_for('productos_bp.producto_detalle', id=id))
