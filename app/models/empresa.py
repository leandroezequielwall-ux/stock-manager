from app.extensions import db
from datetime import datetime

class Empresa(db.Model):
    __tablename__ = 'empresas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    razon_social = db.Column(db.String(150), nullable=False)
    cuit = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(120), nullable=True)
    telefono = db.Column(db.String(50), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    plan = db.Column(db.String(50), default='Starter')
    estado = db.Column(db.String(50), default='Activa')
    fecha_alta = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime, nullable=True)
    
    # Campos de Facturación / Integración de Pagos
    payment_provider = db.Column(db.String(50), nullable=True) # 'stripe', 'mercadopago'
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    stripe_subscription_id = db.Column(db.String(100), nullable=True)
    mp_customer_id = db.Column(db.String(100), nullable=True)
    mp_preapproval_id = db.Column(db.String(100), nullable=True)

    # Relaciones Fase 1
    usuarios = db.relationship('Usuario', backref='empresa', lazy='dynamic', cascade='all, delete-orphan')
    productos = db.relationship('Producto', backref='empresa', lazy='dynamic', cascade='all, delete-orphan')
    categorias = db.relationship('Categoria', backref='empresa', lazy='dynamic', cascade='all, delete-orphan')
    subcategorias = db.relationship('Subcategoria', backref='empresa', lazy='dynamic', cascade='all, delete-orphan')
    movimientos = db.relationship('Movimiento', backref='empresa', lazy='dynamic', cascade='all, delete-orphan')

    # Relaciones SaaS (Fase 8)
    suscripciones = db.relationship('Suscripcion', backref='empresa', lazy=True)
    licencias = db.relationship('Licencia', backref='empresa', lazy=True)
    backups = db.relationship('Backup', backref='empresa', lazy=True)
