from flask import jsonify, request
from app.api import api_bp

@api_bp.route('/login', methods=['POST'])
def api_login():
    """
    Endpoint para autenticación de API.
    En el futuro devolverá un Token JWT válido.
    """
    return jsonify({"status": "not_implemented", "message": "API authentication not implemented yet."}), 501
