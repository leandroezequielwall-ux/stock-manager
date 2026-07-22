from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Categoria, Subcategoria
from app.utils.decorators import admin_required

categorias_bp = Blueprint('categorias_bp', __name__)

@categorias_bp.route('/categorias')
@login_required
@admin_required
def categorias_lista():
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template('categorias/lista.html', categorias=categorias)

@categorias_bp.route('/categorias/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def categoria_nueva():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        if Categoria.query.filter_by(nombre=nombre).first():
            flash('Ya existe una categoría con ese nombre.', 'danger')
        else:
            cat = Categoria(nombre=nombre, descripcion=descripcion)
            db.session.add(cat)
            db.session.commit()
            flash('Categoría creada exitosamente.', 'success')
            return redirect(url_for('categorias_bp.categorias_lista'))
            
    return render_template('categorias/formulario_cat.html', categoria=None, accion='Nueva')

@categorias_bp.route('/categorias/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def categoria_editar(id):
    cat = Categoria.query.get_or_404(id)
    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre', '').strip()
        cat.descripcion = request.form.get('descripcion', '').strip()
        
        existente = Categoria.query.filter(Categoria.nombre == nuevo_nombre, Categoria.id != cat.id).first()
        if existente:
            flash('Ya existe otra categoría con ese nombre.', 'danger')
        else:
            cat.nombre = nuevo_nombre
            db.session.commit()
            flash('Categoría actualizada.', 'success')
            return redirect(url_for('categorias_bp.categorias_lista'))
            
    return render_template('categorias/formulario_cat.html', categoria=cat, accion='Editar')

@categorias_bp.route('/categorias/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def categoria_eliminar(id):
    cat = Categoria.query.get_or_404(id)
    if cat.productos.count() > 0 or cat.subcategorias.count() > 0:
        flash('No se puede eliminar la categoría porque tiene subcategorías o productos asociados.', 'danger')
    else:
        db.session.delete(cat)
        db.session.commit()
        flash('Categoría eliminada.', 'success')
    return redirect(url_for('categorias_bp.categorias_lista'))

@categorias_bp.route('/subcategorias/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def subcategoria_nueva():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        categoria_id = request.form.get('categoria_id')
        
        if Subcategoria.query.filter_by(nombre=nombre, categoria_id=categoria_id).first():
            flash('Ya existe una subcategoría con ese nombre en la categoría seleccionada.', 'danger')
        else:
            sub = Subcategoria(nombre=nombre, categoria_id=categoria_id)
            db.session.add(sub)
            db.session.commit()
            flash('Subcategoría creada exitosamente.', 'success')
            return redirect(url_for('categorias_bp.categorias_lista'))
            
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template('categorias/formulario_sub.html', subcategoria=None, accion='Nueva', categorias=categorias)

@categorias_bp.route('/subcategorias/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def subcategoria_editar(id):
    sub = Subcategoria.query.get_or_404(id)
    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre', '').strip()
        nueva_categoria_id = request.form.get('categoria_id')
        
        existente = Subcategoria.query.filter(Subcategoria.nombre == nuevo_nombre, 
                                              Subcategoria.categoria_id == nueva_categoria_id, 
                                              Subcategoria.id != sub.id).first()
        if existente:
            flash('Ya existe otra subcategoría con ese nombre en la categoría seleccionada.', 'danger')
        else:
            sub.nombre = nuevo_nombre
            sub.categoria_id = nueva_categoria_id
            db.session.commit()
            flash('Subcategoría actualizada.', 'success')
            return redirect(url_for('categorias_bp.categorias_lista'))
            
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template('categorias/formulario_sub.html', subcategoria=sub, accion='Editar', categorias=categorias)

@categorias_bp.route('/subcategorias/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def subcategoria_eliminar(id):
    sub = Subcategoria.query.get_or_404(id)
    if sub.productos.count() > 0:
        flash('No se puede eliminar la subcategoría porque tiene productos asociados.', 'danger')
    else:
        db.session.delete(sub)
        db.session.commit()
        flash('Subcategoría eliminada.', 'success')
    return redirect(url_for('categorias_bp.categorias_lista'))
