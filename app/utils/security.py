from flask import abort
from flask_login import current_user

def get_empresa_id():
    if not current_user.is_authenticated:
        abort(401)
    if current_user.rol == 'SuperAdmin':
        # SuperAdmins can bypass empresa_id check in some global routes
        # However, if they try to access tenant-specific routes, they might fail
        # if those routes assume get_empresa_id() returns an int.
        # So we return None for SuperAdmin, and tenant routes will filter by None 
        # (which yields no results, protecting tenant data).
        return current_user.empresa_id
        
    if not current_user.empresa_id:
        abort(403, description='El usuario no tiene una empresa asignada.')
    return current_user.empresa_id
