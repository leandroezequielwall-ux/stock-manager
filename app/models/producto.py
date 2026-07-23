from app.extensions import db
from datetime import datetime

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, index=True)
    codigo_barras = db.Column(db.String(50), index=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    marca = db.Column(db.String(100))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('subcategorias.id'))
    proveedor = db.Column(db.String(150))
    costo = db.Column(db.Float, default=0.0)
    precio = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5)
    ubicacion = db.Column(db.String(100))
    estado = db.Column(db.String(20), default='activo')
    observaciones = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True, index=True)

    # Relationships
    movimientos = db.relationship('Movimiento', backref='producto', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('codigo', 'empresa_id', name='uix_producto_codigo_empresa'),
        db.UniqueConstraint('codigo_barras', 'empresa_id', name='uix_producto_codigo_barras_empresa'),
    )

    @property
    def ganancia(self):
        return self.precio - self.costo
