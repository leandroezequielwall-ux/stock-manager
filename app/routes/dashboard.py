from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from datetime import date
from app.models import Producto, Movimiento

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/')
@login_required
def dashboard():
    # Basic statistics
    total_productos = Producto.query.count()
    valor_inventario = db_sum(Producto.costo * Producto.stock)
    
    productos_bajo_stock = Producto.query.filter(
        Producto.stock <= Producto.stock_minimo
    ).count()

    # Today's movements
    hoy = date.today()
    movimientos_hoy = Movimiento.query.filter(
        func.date(Movimiento.fecha) == hoy
    ).count()

    # Critical products (stock <= stock_minimo)
    productos_criticos = Producto.query.filter(
        Producto.stock <= Producto.stock_minimo
    ).order_by(Producto.stock.asc()).limit(10).all()

    # Recent movements
    ultimos_movimientos = Movimiento.query.order_by(
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
    productos = Producto.query.filter(
        Producto.stock <= Producto.stock_minimo
    ).order_by(Producto.stock.asc()).all()

    sin_stock = [p for p in productos if p.stock <= 0]
    stock_bajo = [p for p in productos if p.stock > 0]

    return render_template('alertas.html',
                           sin_stock=sin_stock,
                           stock_bajo=stock_bajo,
                           total=len(productos))

def db_sum(expression):
    from app.extensions import db
    result = db.session.query(func.sum(expression)).scalar()
    return result or 0
