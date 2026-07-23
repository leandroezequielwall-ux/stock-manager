from flask import Blueprint, jsonify, send_file
from flask_login import login_required, current_user
from app.utils.decorators import plan_feature_required
from app.utils.security import get_empresa_id
from datetime import datetime
import io
import openpyxl
from app.models import Subcategoria, Producto

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/subcategorias/<int:categoria_id>')
@login_required
def api_subcategorias(categoria_id):
    empresa_id = get_empresa_id()
    subcats = Subcategoria.query.filter_by(categoria_id=categoria_id, empresa_id=empresa_id).order_by(Subcategoria.nombre).all()
    return jsonify([{'id': s.id, 'nombre': s.nombre} for s in subcats])

@api_bp.route('/exportar')
@login_required
@plan_feature_required('reportes_avanzados')
def api_exportar():
    empresa_id = get_empresa_id()
    productos = Producto.query.filter_by(empresa_id=empresa_id).order_by(Producto.nombre).all()
    
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

# --- WEBHOOKS DE FACTURACIÓN (ESQUELETOS) ---

from flask import request
from app.extensions import db
from app.models import Empresa

@api_bp.route('/webhooks/stripe', methods=['POST'])
def webhook_stripe():
    # En producción: validar stripe_signature
    payload = request.json
    
    if not payload:
        return jsonify({'status': 'invalid payload'}), 400
        
    event_type = payload.get('type')
    
    if event_type == 'invoice.payment_succeeded':
        # customer_id = payload['data']['object']['customer']
        # Buscar empresa y habilitar
        pass
    elif event_type in ['invoice.payment_failed', 'customer.subscription.deleted']:
        # customer_id = payload['data']['object']['customer']
        # Buscar empresa y suspender
        pass
        
    return jsonify({'status': 'success'}), 200

@api_bp.route('/webhooks/mercadopago', methods=['POST'])
def webhook_mercadopago():
    # En producción: validar firma / x-signature
    # MP envía notificaciones por IPN o Webhooks
    payload = request.json
    
    if not payload:
        return jsonify({'status': 'invalid payload'}), 400
        
    # Verificar si es un evento de subscripción "preapproval"
    if payload.get('type') == 'subscription_preapproval':
        # mp_preapproval_id = payload.get('data', {}).get('id')
        # Verificar estado en API de MP ('authorized', 'cancelled', 'paused')
        # Actualizar estado de la empresa
        pass
        
    return jsonify({'status': 'success'}), 200
