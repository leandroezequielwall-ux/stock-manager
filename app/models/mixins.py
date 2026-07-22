from app.extensions import db

class TenantMixin:
    """
    Mixin para implementar arquitectura Multi-tenant (SaaS).
    Cualquier modelo que herede de esta clase pertenecerá a una Empresa (Tenant) específica.
    """
    # En el futuro, se cambiará nullable a False cuando el sistema multi-empresa sea obligatorio.
    # empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True, index=True)
    
    # IMPORTANTE: Se encuentra comentado temporalmente para no romper 
    # la compatibilidad con la estructura de base de datos actual (Fase 8).
    
    @classmethod
    def query_tenant(cls, empresa_id):
        """
        Helper para realizar consultas limitadas al scope del Tenant actual.
        Uso futuro: Producto.query_tenant(current_empresa_id).all()
        """
        # return cls.query.filter_by(empresa_id=empresa_id)
        return cls.query # Fallback actual
