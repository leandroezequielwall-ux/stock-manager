from app.extensions import db
from app.models import Categoria, Subcategoria

def resolve_categoria(form_data):
    cat_id = form_data.get('categoria_id')
    if cat_id == 'nueva':
        nueva_cat = form_data.get('nueva_categoria', '').strip()
        if nueva_cat:
            cat = Categoria.query.filter_by(nombre=nueva_cat).first()
            if not cat:
                cat = Categoria(nombre=nueva_cat)
                db.session.add(cat)
                db.session.flush()
            return cat.id
    return int(cat_id) if cat_id and cat_id != 'nueva' else None

def resolve_subcategoria(form_data, parent_cat_id):
    subcat_id = form_data.get('subcategoria_id')
    if subcat_id == 'nueva' and parent_cat_id:
        nueva_sub = form_data.get('nueva_subcategoria', '').strip()
        if nueva_sub:
            sub = Subcategoria.query.filter_by(nombre=nueva_sub, categoria_id=parent_cat_id).first()
            if not sub:
                sub = Subcategoria(nombre=nueva_sub, categoria_id=parent_cat_id)
                db.session.add(sub)
                db.session.flush()
            return sub.id
    return int(subcat_id) if subcat_id and subcat_id != 'nueva' else None
