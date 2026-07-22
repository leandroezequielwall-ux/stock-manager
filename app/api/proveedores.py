from flask import jsonify, request
from app.api import api_bp

@api_bp.route('/proveedores', methods=['GET', 'POST'])
def api_proveedores():
    """
    Endpoint para listar y crear proveedores.
    """
    return jsonify({"status": "not_implemented", "message": "API for proveedores not implemented yet."}), 501

@api_bp.route('/proveedores/<int:proveedor_id>', methods=['GET', 'PUT', 'DELETE'])
def api_proveedor_detalle(proveedor_id):
    """
    Endpoint para ver, editar o eliminar un proveedor específico.
    """
    return jsonify({"status": "not_implemented", "message": f"API for proveedor {proveedor_id} not implemented yet."}), 501
