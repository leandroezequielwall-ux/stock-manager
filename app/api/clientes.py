from flask import jsonify, request
from app.api import api_bp

@api_bp.route('/clientes', methods=['GET', 'POST'])
def api_clientes():
    """
    Endpoint para listar y crear clientes.
    """
    return jsonify({"status": "not_implemented", "message": "API for clientes not implemented yet."}), 501

@api_bp.route('/clientes/<int:cliente_id>', methods=['GET', 'PUT', 'DELETE'])
def api_cliente_detalle(cliente_id):
    """
    Endpoint para ver, editar o eliminar un cliente específico.
    """
    return jsonify({"status": "not_implemented", "message": f"API for cliente {cliente_id} not implemented yet."}), 501
