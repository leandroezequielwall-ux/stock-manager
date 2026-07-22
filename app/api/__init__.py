from .endpoints import api_bp

# Import submodules to register their routes with api_bp
from . import auth
from . import productos
from . import clientes
from . import proveedores
from . import movimientos
from . import dashboard

__all__ = ['api_bp']
