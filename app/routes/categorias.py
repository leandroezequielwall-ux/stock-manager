from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.security import get_empresa_id
from app.extensions import db
from app.models import Categoria, Subcategoria
from app.utils.decorators import admin_required, role_required
from app.utils.auditoria import log_auditoria

categorias_bp = Blueprint('categorias_bp', __name__)

@categorias_bp.route('/categorias')
@login_required
@role_required('Administrador', 'Supervisor')
def categorias_lista():
    empresa_id = get_empresa_id()
    categorias = Categoria.query.filter_by(empresa_id=empresa_id).order_by(Categoria.nombre).all()
    return render_template('categorias/lista.html', categorias=categorias)

@categorias_bp.route('/categorias/nueva', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Supervisor')
def categoria_nueva():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        empresa_id = get_empresa_id()
        
        if Categoria.query.filter_by(nombre=nombre, empresa_id=empresa_id).first():
            flash('Ya existe una categoría con ese nombre.', 'danger')
        else:
            cat = Categoria(nombre=nombre, descripcion=descripcion, empresa_id=empresa_id)
            db.session.add(cat)
            db.session.commit()
            flash('Categoría creada exitosamente.', 'success')
            log_auditoria('CREAR', 'categorias', cat.id, {'nombre': cat.nombre})
            return redirect(url_for('categorias_bp.categorias_lista'))
            
    return render_template('categorias/formulario_cat.html', categoria=None, accion='Nueva')

@categorias_bp.route('/categorias/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Supervisor')
def categoria_editar(id):
    empresa_id = get_empresa_id()
    cat = Categoria.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()
    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre', '').strip()
        cat.descripcion = request.form.get('descripcion', '').strip()
        
        existente = Categoria.query.filter(Categoria.nombre == nuevo_nombre, Categoria.id != cat.id, Categoria.empresa_id == empresa_id).first()
        if existente:
            flash('Ya existe otra categoría con ese nombre.', 'danger')
        else:
            cat.nombre = nuevo_nombre
            db.session.commit()
            flash('Categoría actualizada.', 'success')
            log_auditoria('EDITAR', 'categorias', cat.id, {'nombre': cat.nombre})
            return redirect(url_for('categorias_bp.categorias_lista'))
            
    return render_template('categorias/formulario_cat.html', categoria=cat, accion='Editar')

@categorias_bp.route('/categorias/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Supervisor')
def categoria_eliminar(id):
    empresa_id = get_empresa_id()
    cat = Categoria.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()
    if cat.productos.count() > 0 or cat.subcategorias.count() > 0:
        flash('No se puede eliminar la categoría porque tiene subcategorías o productos asociados.', 'danger')
    else:
        cat_id = cat.id
        db.session.delete(cat)
        db.session.commit()
        flash('Categoría eliminada.', 'success')
        log_auditoria('ELIMINAR', 'categorias', cat_id, {'nombre': cat.nombre})
    return redirect(url_for('categorias_bp.categorias_lista'))

@categorias_bp.route('/subcategorias/nueva', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Supervisor')
def subcategoria_nueva():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        categoria_id = request.form.get('categoria_id')
        
        empresa_id = get_empresa_id()
        
        if Subcategoria.query.filter_by(nombre=nombre, categoria_id=categoria_id, empresa_id=empresa_id).first():
            flash('Ya existe una subcategoría con ese nombre en la categoría seleccionada.', 'danger')
        else:
            sub = Subcategoria(nombre=nombre, categoria_id=categoria_id, empresa_id=empresa_id)
            db.session.add(sub)
            db.session.commit()
            flash('Subcategoría creada exitosamente.', 'success')
            log_auditoria('CREAR', 'subcategorias', sub.id, {'nombre': sub.nombre})
            return redirect(url_for('categorias_bp.categorias_lista'))
            
    empresa_id = get_empresa_id()
    categorias = Categoria.query.filter_by(empresa_id=empresa_id).order_by(Categoria.nombre).all()
    return render_template('categorias/formulario_sub.html', subcategoria=None, accion='Nueva', categorias=categorias)

@categorias_bp.route('/subcategorias/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Supervisor')
def subcategoria_editar(id):
    empresa_id = get_empresa_id()
    sub = Subcategoria.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()
    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre', '').strip()
        nueva_categoria_id = request.form.get('categoria_id')
        
        existente = Subcategoria.query.filter(Subcategoria.nombre == nuevo_nombre, 
                                              Subcategoria.categoria_id == nueva_categoria_id, 
                                              Subcategoria.id != sub.id,
                                              Subcategoria.empresa_id == empresa_id).first()
        if existente:
            flash('Ya existe otra subcategoría con ese nombre en la categoría seleccionada.', 'danger')
        else:
            sub.nombre = nuevo_nombre
            sub.categoria_id = nueva_categoria_id
            db.session.commit()
            flash('Subcategoría actualizada.', 'success')
            log_auditoria('EDITAR', 'subcategorias', sub.id, {'nombre': sub.nombre})
            return redirect(url_for('categorias_bp.categorias_lista'))
            
    empresa_id = get_empresa_id()
    categorias = Categoria.query.filter_by(empresa_id=empresa_id).order_by(Categoria.nombre).all()
    return render_template('categorias/formulario_sub.html', subcategoria=sub, accion='Editar', categorias=categorias)

@categorias_bp.route('/subcategorias/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Supervisor')
def subcategoria_eliminar(id):
    empresa_id = get_empresa_id()
    sub = Subcategoria.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()
    if sub.productos.count() > 0:
        flash('No se puede eliminar la subcategoría porque tiene productos asociados.', 'danger')
    else:
        sub_id = sub.id
        db.session.delete(sub)
        db.session.commit()
        flash('Subcategoría eliminada.', 'success')
        log_auditoria('ELIMINAR', 'subcategorias', sub_id, {'nombre': sub.nombre})
    return redirect(url_for('categorias_bp.categorias_lista'))
