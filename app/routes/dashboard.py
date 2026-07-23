from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.utils.security import get_empresa_id
from sqlalchemy import func
from datetime import date
from app.models import Producto, Movimiento

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    # Basic statistics
    empresa_id = get_empresa_id()
    total_productos = Producto.query.filter_by(empresa_id=empresa_id).count()
    from app.extensions import db
    valor_inventario = db.session.query(func.sum(Producto.costo * Producto.stock)).filter(Producto.empresa_id == empresa_id).scalar() or 0
    
    productos_bajo_stock = Producto.query.filter(
        Producto.stock <= Producto.stock_minimo,
        Producto.empresa_id == empresa_id
    ).count()

    # Today's movements
    hoy = date.today()
    movimientos_hoy = Movimiento.query.filter(
        func.date(Movimiento.fecha) == hoy,
        Movimiento.empresa_id == empresa_id
    ).count()

    # Critical products (stock <= stock_minimo)
    productos_criticos = Producto.query.filter(
        Producto.stock <= Producto.stock_minimo,
        Producto.empresa_id == empresa_id
    ).order_by(Producto.stock.asc()).limit(10).all()

    # Recent movements
    ultimos_movimientos = Movimiento.query.filter_by(empresa_id=empresa_id).order_by(
        Movimiento.fecha.desc()
    ).limit(10).all()

    return render_template('dashboard.html',
                           total_productos=total_productos,
                           valor_total=valor_inventario,
                           productos_bajo_stock=productos_bajo_stock,
                           movimientos_hoy=movimientos_hoy,
                           productos_criticos=productos_criticos,
                           ultimos_movimientos=ultimos_movimientos)


@dashboard_bp.route('/alertas')
@login_required
def alertas():
    empresa_id = get_empresa_id()
    productos = Producto.query.filter(
        Producto.stock <= Producto.stock_minimo,
        Producto.empresa_id == empresa_id
    ).order_by(Producto.stock.asc()).all()

    sin_stock = [p for p in productos if p.stock <= 0]
    stock_bajo = [p for p in productos if p.stock > 0]

    return render_template('alertas.html',
                           sin_stock=sin_stock,
                           stock_bajo=stock_bajo,
                           total=len(productos))


