"""
init_db.py — Initialize the database with optional sample data.
Run: python init_db.py
"""
from app import create_app
from app.extensions import db
from app.models import Categoria, Subcategoria, Producto, Movimiento
from datetime import datetime


SAMPLE_CATEGORIAS = [
    {'nombre': 'Herramientas', 'descripcion': 'Herramientas manuales y eléctricas'},
    {'nombre': 'Tornillería', 'descripcion': 'Tornillos, tuercas, arandelas y fijaciones'},
    {'nombre': 'Electricidad', 'descripcion': 'Material eléctrico e iluminación'},
    {'nombre': 'Pinturas', 'descripcion': 'Pinturas, esmaltes y accesorios'},
    {'nombre': 'Plomería', 'descripcion': 'Artículos de plomería y sanitarios'},
]

SAMPLE_SUBCATEGORIAS = [
    {'nombre': 'Manuales', 'categoria': 'Herramientas'},
    {'nombre': 'Eléctricas', 'categoria': 'Herramientas'},
    {'nombre': 'Seguridad', 'categoria': 'Herramientas'},
    {'nombre': 'Tornillos', 'categoria': 'Tornillería'},
    {'nombre': 'Cables', 'categoria': 'Electricidad'},
    {'nombre': 'Interruptores', 'categoria': 'Electricidad'},
    {'nombre': 'Tomas', 'categoria': 'Electricidad'},
    {'nombre': 'Látex', 'categoria': 'Pinturas'},
    {'nombre': 'Accesorios', 'categoria': 'Pinturas'},
    {'nombre': 'Grifería', 'categoria': 'Plomería'},
]

SAMPLE_DATA = [
    {
        'codigo': 'HER-001',
        'codigo_barras': '7790100100017',
        'nombre': 'Taladro Percutor 13mm 750W',
        'descripcion': 'Velocidad variable, mandril 13mm, cable 3m',
        'marca': 'Bosch',
        'categoria': 'Herramientas',
        'subcategoria': 'Eléctricas',
        'proveedor': 'Distribuidora Norte',
        'costo': 45000,
        'precio': 72000,
        'stock': 8,
        'stock_minimo': 2,
        'ubicacion': 'Estante A-1',
        'estado': 'activo',
        'observaciones': '',
    },
    {
        'codigo': 'HER-002',
        'codigo_barras': '7790100100024',
        'nombre': 'Set Destornilladores x10 piezas',
        'descripcion': 'Phillips y planos, mango ergonómico',
        'marca': 'Stanley',
        'categoria': 'Herramientas',
        'subcategoria': 'Manuales',
        'proveedor': 'Herramientas Express',
        'costo': 12000,
        'precio': 19500,
        'stock': 15,
        'stock_minimo': 5,
        'ubicacion': 'Estante A-2',
        'estado': 'activo',
        'observaciones': '',
    },
    {
        'codigo': 'TOR-001',
        'nombre': 'Tornillo Autoperforante 6x1"',
        'descripcion': 'Caja x100 unidades, cabeza hexagonal',
        'marca': '',
        'categoria': 'Tornillería',
        'subcategoria': 'Tornillos',
        'proveedor': 'Bulonera Central',
        'costo': 3500,
        'precio': 5800,
        'stock': 50,
        'stock_minimo': 10,
        'ubicacion': 'Estante B-1',
        'estado': 'activo',
        'observaciones': 'Reponer cuando baje de 10 cajas',
    },
    {
        'codigo': 'ELE-001',
        'codigo_barras': '7790200300015',
        'nombre': 'Cable Unipolar 2.5mm x100m',
        'descripcion': 'Rojo, norma IRAM 2183, uso domiciliario',
        'marca': 'IMSA',
        'categoria': 'Electricidad',
        'subcategoria': 'Cables',
        'proveedor': 'Eléctrica del Sur',
        'costo': 28000,
        'precio': 45000,
        'stock': 3,
        'stock_minimo': 5,
        'ubicacion': 'Estante C-1',
        'estado': 'activo',
        'observaciones': '',
    },
    {
        'codigo': 'ELE-002',
        'nombre': 'Llave Térmica Bipolar 2x20A',
        'descripcion': 'Din, curva C, 6kA',
        'marca': 'Schneider',
        'categoria': 'Electricidad',
        'subcategoria': 'Interruptores',
        'proveedor': 'Eléctrica del Sur',
        'costo': 15000,
        'precio': 24000,
        'stock': 12,
        'stock_minimo': 3,
        'ubicacion': 'Estante C-2',
        'estado': 'activo',
        'observaciones': '',
    },
    {
        'codigo': 'PIN-001',
        'nombre': 'Pintura Látex Interior 20L',
        'descripcion': 'Blanco mate, alto rendimiento',
        'marca': 'Alba',
        'categoria': 'Pinturas',
        'subcategoria': 'Látex',
        'proveedor': 'Pinturas Mayorista',
        'costo': 32000,
        'precio': 52000,
        'stock': 0,
        'stock_minimo': 3,
        'ubicacion': 'Depósito D-1',
        'estado': 'activo',
        'observaciones': 'Reponer urgente',
    },
    {
        'codigo': 'PIN-002',
        'nombre': 'Cinta de Papel 18mm x50m',
        'descripcion': 'Para enmascarar, fácil despegado',
        'marca': '3M',
        'categoria': 'Pinturas',
        'subcategoria': 'Accesorios',
        'proveedor': 'Pinturas Mayorista',
        'costo': 2800,
        'precio': 4500,
        'stock': 25,
        'stock_minimo': 8,
        'ubicacion': 'Estante D-2',
        'estado': 'activo',
        'observaciones': '',
    },
    {
        'codigo': 'PLO-001',
        'codigo_barras': '7790400500019',
        'nombre': 'Canilla Monocomando Cocina',
        'descripcion': 'Cromada, caño alto giratorio',
        'marca': 'FV',
        'categoria': 'Plomería',
        'subcategoria': 'Grifería',
        'proveedor': 'Sanitarios del Centro',
        'costo': 38000,
        'precio': 62000,
        'stock': 4,
        'stock_minimo': 2,
        'ubicacion': 'Estante E-1',
        'estado': 'activo',
        'observaciones': 'Modelo nuevo 2026',
    },
    {
        'codigo': 'HER-003',
        'nombre': 'Candado Bronce 50mm',
        'descripcion': 'Arco endurecido, 3 llaves',
        'marca': 'Mamboretá',
        'categoria': 'Herramientas',
        'subcategoria': 'Seguridad',
        'proveedor': 'Distribuidora Norte',
        'costo': 8500,
        'precio': 14000,
        'stock': 1,
        'stock_minimo': 3,
        'ubicacion': 'Vitrina F-1',
        'estado': 'activo',
        'observaciones': '',
    },
    {
        'codigo': 'ELE-003',
        'codigo_barras': '7790200300039',
        'nombre': 'Tomacorriente Doble 10A',
        'descripcion': 'Línea Siglo XXI, blanco',
        'marca': 'Cambre',
        'categoria': 'Electricidad',
        'subcategoria': 'Tomas',
        'proveedor': 'Eléctrica del Sur',
        'costo': 4200,
        'precio': 7000,
        'stock': 20,
        'stock_minimo': 5,
        'ubicacion': 'Estante C-3',
        'estado': 'activo',
        'observaciones': '',
    },
]


def init_database(with_samples=True):
    """Create tables and optionally load sample data."""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("[OK] Base de datos creada exitosamente.")

        if with_samples:
            # Create default admin user
            from app.models import Usuario
            if Usuario.query.count() == 0:
                admin_user = Usuario(nombre="Administrador", email="admin", es_admin=True)
                admin_user.set_password("admin123")
                db.session.add(admin_user)
                db.session.flush()
                print("[OK] Usuario administrador por defecto creado.")

            # Create categories if empty
            if Categoria.query.count() == 0:
                cat_map = {}
                for data in SAMPLE_CATEGORIAS:
                    cat = Categoria(**data)
                    db.session.add(cat)
                    db.session.flush()
                    cat_map[cat.nombre] = cat.id
                print(f"[OK] {len(SAMPLE_CATEGORIAS)} categorías creadas.")
            else:
                cat_map = {c.nombre: c.id for c in Categoria.query.all()}

            # Create subcategories if empty
            if Subcategoria.query.count() == 0:
                sub_map = {}
                for data in SAMPLE_SUBCATEGORIAS:
                    cat_nombre = data.pop('categoria')
                    cat_id = cat_map.get(cat_nombre)
                    if cat_id:
                        sub = Subcategoria(nombre=data['nombre'], categoria_id=cat_id)
                        db.session.add(sub)
                        db.session.flush()
                        sub_map[(cat_nombre, sub.nombre)] = sub.id
                print(f"[OK] {len(SAMPLE_SUBCATEGORIAS)} subcategorías creadas.")
            else:
                sub_map = {
                    (s.categoria.nombre, s.nombre): s.id
                    for s in Subcategoria.query.all()
                }

            # Only add samples if table is empty
            if Producto.query.count() == 0:
                for data in SAMPLE_DATA:
                    cat_nombre = data.pop('categoria', '')
                    sub_nombre = data.pop('subcategoria', '')
                    data['categoria_id'] = cat_map.get(cat_nombre)
                    data['subcategoria_id'] = sub_map.get((cat_nombre, sub_nombre))
                    producto = Producto(**data)
                    db.session.add(producto)
                db.session.flush()

                # Add sample movements for each product with stock
                for producto in Producto.query.all():
                    if producto.stock > 0:
                        mov = Movimiento(
                            producto_id=producto.id,
                            tipo='ENTRADA',
                            cantidad=producto.stock,
                            motivo='Stock inicial',
                        )
                        db.session.add(mov)

                db.session.commit()
                print(f"[OK] {len(SAMPLE_DATA)} productos de ejemplo cargados.")
            else:
                print("[INFO] La base de datos ya contiene productos. No se cargaron datos de ejemplo.")


if __name__ == '__main__':
    init_database(with_samples=True)
