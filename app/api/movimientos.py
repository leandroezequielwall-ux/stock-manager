from flask import jsonify, request
from app.api import api_bp

@api_bp.route('/movimientos', methods=['GET', 'POST'])
def api_movimientos():
    """
    Endpoint para listar y registrar movimientos de stock.
    """
    return jsonify({"status": "not_implemented", "message": "API for movimientos not implemented yet."}), 501

@api_bp.route('/movimientos/<int:movimiento_id>', methods=['GET'])
def api_movimiento_detalle(movimiento_id):
    """
    Endpoint para ver detalle de un movimiento.
    """
    return jsonify({"status": "not_implemented", "message": f"API for movimiento {movimiento_id} not implemented yet."}), 501
