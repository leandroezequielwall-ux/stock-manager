from app.extensions import db
from datetime import datetime

class Auditoria(db.Model):
    __tablename__ = 'auditorias'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True, index=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True, index=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    accion = db.Column(db.String(50), nullable=False)
    tabla = db.Column(db.String(50), nullable=False)
    registro_id = db.Column(db.String(50), nullable=True)
    detalles = db.Column(db.Text, nullable=True)

    # Relaciones
    usuario = db.relationship('Usuario', backref='auditorias', lazy=True)
