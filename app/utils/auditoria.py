from flask import request
from flask_login import current_user
from app.extensions import db
from app.models.auditoria import Auditoria
import json

def log_auditoria(accion, tabla, registro_id=None, detalles=None):
    """
    Registra un evento en la tabla de auditoría.
    
    :param accion: Ej. 'CREAR', 'EDITAR', 'ELIMINAR', 'LOGIN', 'LOGOUT'
    :param tabla: Nombre del módulo afectado, ej. 'productos', 'usuarios'
    :param registro_id: ID del elemento creado/modificado
    :param detalles: Un dict con información extra, se guardará como JSON string
    """
    try:
        # Obtener IP (si estamos detras de un proxy, usamos HTTP_X_FORWARDED_FOR)
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()

        # Determinar usuario y empresa
        usuario_id = current_user.id if current_user and current_user.is_authenticated else None
        
        # SuperAdmin no tiene empresa_id, los inquilinos sí
        empresa_id = None
        if current_user and current_user.is_authenticated:
            if current_user.rol != 'SuperAdmin':
                empresa_id = current_user.empresa_id

        # Convertir detalles a JSON string si viene como dict
        detalles_str = None
        if detalles:
            if isinstance(detalles, dict):
                detalles_str = json.dumps(detalles)
            else:
                detalles_str = str(detalles)

        registro_id_str = str(registro_id) if registro_id else None

        evento = Auditoria(
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            ip_address=ip,
            accion=accion,
            tabla=tabla,
            registro_id=registro_id_str,
            detalles=detalles_str
        )
        
        db.session.add(evento)
        db.session.commit()
    except Exception as e:
        print(f"Error al registrar auditoria: {e}")
        db.session.rollback()
