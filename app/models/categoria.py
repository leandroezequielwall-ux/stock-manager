from app.extensions import db

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    
    # Relationships
    productos = db.relationship('Producto', backref='categoria', lazy='dynamic')
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy='dynamic', cascade='all, delete-orphan')


class Subcategoria(db.Model):
    __tablename__ = 'subcategorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    
    # Relationships
    productos = db.relationship('Producto', backref='subcategoria', lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint('nombre', 'categoria_id', name='uix_subcat_nombre_categoria'),
    )
