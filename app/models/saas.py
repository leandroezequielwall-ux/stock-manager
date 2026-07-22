from app.extensions import db
from datetime import datetime

class Plan(db.Model):
    """
    Modelo para los planes de suscripción (e.g. Free, Pro, Enterprise).
    """
    __tablename__ = 'planes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    limite_usuarios = db.Column(db.Integer, nullable=False, default=1)
    limite_productos = db.Column(db.Integer, nullable=False, default=100)
    
    # Relación uno-a-muchos con Suscripcion
    suscripciones = db.relationship('Suscripcion', backref='plan', lazy=True)

class Empresa(db.Model):
    """
    Modelo principal del Tenant (Empresa o Cliente SaaS).
    """
    __tablename__ = 'empresas'
    
    id = db.Column(db.Integer, primary_key=True)
    razon_social = db.Column(db.String(150), nullable=False)
    cuit = db.Column(db.String(20), unique=True, nullable=True)
    email_contacto = db.Column(db.String(120), nullable=True)
    fecha_alta = db.Column(db.DateTime, default=datetime.utcnow)
    activa = db.Column(db.Boolean, default=True)
    
    # Relación uno-a-muchos con Suscripcion
    suscripciones = db.relationship('Suscripcion', backref='empresa', lazy=True)
    # Relación uno-a-muchos con Licencias
    licencias = db.relationship('Licencia', backref='empresa', lazy=True)
    # Relación uno-a-muchos con Backups
    backups = db.relationship('Backup', backref='empresa', lazy=True)

class Suscripcion(db.Model):
    """
    Modelo para gestionar el estado de facturación de una empresa.
    """
    __tablename__ = 'suscripciones'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('planes.id'), nullable=False)
    
    fecha_inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default='activa') # activa, suspendida, cancelada

class Licencia(db.Model):
    """
    Modelo para claves de validación o licencias asignadas.
    """
    __tablename__ = 'licencias'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    llave = db.Column(db.String(64), unique=True, nullable=False)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    valida_hasta = db.Column(db.DateTime, nullable=True)

class Backup(db.Model):
    """
    Modelo para registrar copias de seguridad de cada Tenant.
    """
    __tablename__ = 'backups'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    archivo_url = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    tamaño_bytes = db.Column(db.Integer, nullable=True)
