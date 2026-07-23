from flask import Blueprint, render_template, request
from flask_login import login_required
from app.utils.security import get_empresa_id
from app.models.auditoria import Auditoria
from app.utils.decorators import admin_required
import json

auditoria_bp = Blueprint('auditoria_bp', __name__)

@auditoria_bp.route('/auditoria')
@login_required
@admin_required
def auditoria_lista():
    empresa_id = get_empresa_id()
    page = request.args.get('page', 1, type=int)
    
    # Obtener logs ordenados por fecha descendente
    query = Auditoria.query.filter_by(empresa_id=empresa_id).order_by(Auditoria.fecha.desc())
    
    # Paginación
    logs = query.paginate(page=page, per_page=30)
    
    # Convertir JSON details a diccionarios manejables en la plantilla
    for log in logs.items:
        if log.detalles:
            try:
                log.detalles_dict = json.loads(log.detalles)
            except:
                log.detalles_dict = {'info': log.detalles}
        else:
            log.detalles_dict = {}

    return render_template('auditoria/lista.html', logs=logs)
