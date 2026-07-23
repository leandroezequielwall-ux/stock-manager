from app.extensions import db

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True, index=True)
    
    # Relationships
    productos = db.relationship('Producto', backref='categoria', lazy='dynamic')
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('nombre', 'empresa_id', name='uix_categoria_nombre_empresa'),
    )


class Subcategoria(db.Model):
    __tablename__ = 'subcategorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True, index=True)
    
    # Relationships
    productos = db.relationship('Producto', backref='subcategoria', lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint('nombre', 'categoria_id', 'empresa_id', name='uix_subcat_nombre_categoria_empresa'),
    )
