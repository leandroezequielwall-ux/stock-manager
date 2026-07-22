from flask import jsonify
from app.api import api_bp

@api_bp.route('/dashboard', methods=['GET'])
def api_dashboard():
    """
    Endpoint para obtener métricas generales del dashboard.
    """
    return jsonify({"status": "not_implemented", "message": "API for dashboard not implemented yet."}), 501
