from flask import request, g

def get_current_empresa_id():
    """
    Obtiene el ID de la empresa actual desde el contexto de la petición.
    En una arquitectura SaaS, esto se lee desde el subdominio, el JWT, o la sesión del usuario.
    
    Uso futuro:
    if not request.endpoint.startswith('static'):
        g.empresa_id = obtener_de_subdominio(request.host)
        
    Por ahora (Fase 8), retorna None o 1 por defecto para no romper el sistema local.
    """
    return getattr(g, 'empresa_id', None)
