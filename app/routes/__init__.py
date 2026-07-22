from .auth import auth_bp
from .dashboard import dashboard_bp
from .productos import productos_bp
from .categorias import categorias_bp
from .movimientos import movimientos_bp
from .usuarios import usuarios_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'productos_bp',
    'categorias_bp',
    'movimientos_bp',
    'usuarios_bp'
]
