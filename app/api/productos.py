from flask import jsonify, request
from app.api import api_bp

@api_bp.route('/productos', methods=['GET', 'POST'])
def api_productos():
    """
    Endpoint para listar y crear productos.
    """
    return jsonify({"status": "not_implemented", "message": "API for productos not implemented yet."}), 501

@api_bp.route('/productos/<int:producto_id>', methods=['GET', 'PUT', 'DELETE'])
def api_producto_detalle(producto_id):
    """
    Endpoint para ver, editar o eliminar un producto específico.
    """
    return jsonify({"status": "not_implemented", "message": f"API for producto {producto_id} not implemented yet."}), 501
