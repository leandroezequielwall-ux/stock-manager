from flask import Blueprint, jsonify, send_file
from flask_login import login_required
from datetime import datetime
import io
import openpyxl
from app.models import Subcategoria, Producto

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/subcategorias/<int:categoria_id>')
@login_required
def api_subcategorias(categoria_id):
    """Return subcategories for a given category (AJAX endpoint for cascading dropdown)."""
    subcats = Subcategoria.query.filter_by(categoria_id=categoria_id).order_by(Subcategoria.nombre).all()
    return jsonify([{'id': s.id, 'nombre': s.nombre} for s in subcats])

@api_bp.route('/exportar')
@login_required
def api_exportar():
    """Export inventory to Excel."""
    productos = Producto.query.order_by(Producto.nombre).all()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventario"
    
    headers = [
        "Código", "Código de Barras", "Nombre", "Descripción", "Marca", 
        "Categoría", "Subcategoría", "Proveedor", "Costo", "Precio Venta", 
        "Stock", "Stock Mínimo", "Ubicación", "Estado", "Observaciones"
    ]
    ws.append(headers)
    
    for header in ws[1]:
        header.font = openpyxl.styles.Font(bold=True)
        
    for p in productos:
        cat_nombre = p.categoria.nombre if p.categoria else ''
        subcat_nombre = p.subcategoria.nombre if p.subcategoria else ''
        ws.append([
            p.codigo,
            p.codigo_barras,
            p.nombre,
            p.descripcion,
            p.marca,
            cat_nombre,
            subcat_nombre,
            p.proveedor,
            p.costo,
            p.precio,
            p.stock,
            p.stock_minimo,
            p.ubicacion,
            p.estado,
            p.observaciones
        ])
        
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    
    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    return send_file(
        out, 
        as_attachment=True, 
        download_name=f'inventario_{fecha}.xlsx', 
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
