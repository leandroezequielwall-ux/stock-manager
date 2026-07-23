from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.security import get_empresa_id
from sqlalchemy import or_
from app.extensions import db
from app.models import Producto, Categoria, Subcategoria, Movimiento, Empresa
from app.utils.decorators import admin_required, role_required
from app.utils.helpers import resolve_categoria, resolve_subcategoria
from app.utils.planes import PLANES_LIMITES
from app.utils.auditoria import log_auditoria

productos_bp = Blueprint('productos_bp', __name__)

@productos_bp.route('/productos')
@login_required
def productos_lista():
    page = request.args.get('page', 1, type=int)
    busqueda = request.args.get('q', '').strip()
    per_page = 20

    empresa_id = get_empresa_id()
    query = Producto.query.filter_by(empresa_id=empresa_id)

    if busqueda:
        query = query.filter(
            or_(
                Producto.codigo.ilike(f'%{busqueda}%'),
                Producto.codigo_barras.ilike(f'%{busqueda}%'),
                Producto.nombre.ilike(f'%{busqueda}%'),
                Producto.marca.ilike(f'%{busqueda}%'),
                Producto.proveedor.ilike(f'%{busqueda}%')
            )
        )

    productos = query.order_by(Producto.nombre).paginate(page=page, per_page=per_page)

    empresa = Empresa.query.get(empresa_id)
    tiene_reportes = False
    if empresa:
        tiene_reportes = PLANES_LIMITES.get(empresa.plan, PLANES_LIMITES['Starter']).get('reportes_avanzados', False)

    return render_template('productos/lista.html', 
                           productos=productos, 
                           busqueda=busqueda,
                           tiene_reportes=tiene_reportes)

@productos_bp.route('/productos/<int:id>')
@login_required
def producto_detalle(id):
    empresa_id = get_empresa_id()
    producto = Producto.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()
    movimientos = producto.movimientos.order_by(
        Movimiento.fecha.desc()
    ).limit(15).all()
    
    return render_template('productos/detalle.html', 
                           producto=producto, 
                           movimientos=movimientos)

@productos_bp.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Supervisor')
def producto_nuevo():
    if request.method == 'POST':
        codigo = request.form.get('codigo').strip().upper()
        
        empresa_id = get_empresa_id()
        empresa = Empresa.query.get(empresa_id)
        
        # Validar límites del plan
        if empresa:
            plan_actual = empresa.plan
            limites = PLANES_LIMITES.get(plan_actual, PLANES_LIMITES['Starter'])
            max_productos = limites['max_productos']
            
            productos_actuales = Producto.query.filter_by(empresa_id=empresa_id).count()
            if productos_actuales >= max_productos:
                flash(f'Has alcanzado el límite de {max_productos} productos de tu plan {plan_actual}.', 'warning')
                return redirect(url_for('productos_bp.productos_lista'))
                
        # Check if code exists
        if Producto.query.filter_by(codigo=codigo, empresa_id=empresa_id).first():
            flash(f'El código {codigo} ya existe en el inventario.', 'danger')
            return redirect(request.url)

        codigo_barras = request.form.get('codigo_barras', '').strip()
        if codigo_barras and Producto.query.filter_by(codigo_barras=codigo_barras, empresa_id=empresa_id).first():
            flash(f'El código de barras {codigo_barras} ya existe en el inventario.', 'danger')
            return redirect(request.url)

        cat_id = resolve_categoria(request.form)
        subcat_id = resolve_subcategoria(request.form, cat_id)

        try:
            producto = Producto(
                codigo=codigo,
                codigo_barras=codigo_barras or None,
                nombre=request.form.get('nombre').strip(),
                descripcion=request.form.get('descripcion', '').strip(),
                marca=request.form.get('marca', '').strip(),
                categoria_id=cat_id,
                subcategoria_id=subcat_id,
                proveedor=request.form.get('proveedor', '').strip(),
                costo=float(request.form.get('costo') or 0),
                precio=float(request.form.get('precio') or 0),
                stock=int(request.form.get('stock') or 0),
                stock_minimo=int(request.form.get('stock_minimo') or 1),
                ubicacion=request.form.get('ubicacion', '').strip(),
                estado=request.form.get('estado', 'activo'),
                observaciones=request.form.get('observaciones', '').strip(),
                empresa_id=empresa_id
            )

            db.session.add(producto)
            db.session.commit()

            # Record initial stock movement if > 0
            if producto.stock > 0:
                from app.models import Movimiento
                mov = Movimiento(
                    producto_id=producto.id,
                    tipo='ENTRADA',
                    cantidad=producto.stock,
                    motivo='Stock inicial',
                    empresa_id=empresa_id
                )
                db.session.add(mov)
                db.session.commit()

            flash('Producto creado exitosamente.', 'success')
            log_auditoria('CREAR', 'productos', producto.id, {'codigo': producto.codigo, 'nombre': producto.nombre})
            return redirect(url_for('productos_bp.producto_detalle', id=producto.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el producto: {e}', 'danger')

    empresa_id = get_empresa_id()
    categorias = Categoria.query.filter_by(empresa_id=empresa_id).order_by(Categoria.nombre).all()
    subcategorias = Subcategoria.query.filter_by(empresa_id=empresa_id).order_by(Subcategoria.nombre).all()
    return render_template('productos/formulario.html', 
                           producto=None, accion='Nuevo',
                           categorias=categorias, subcategorias=subcategorias)

@productos_bp.route('/productos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('Administrador', 'Supervisor')
def producto_editar(id):
    empresa_id = get_empresa_id()
    producto = Producto.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()

    if request.method == 'POST':
        nuevo_codigo = request.form.get('codigo').strip().upper()
        
        # Check if new code exists and is not the current product
        existente = Producto.query.filter(Producto.codigo == nuevo_codigo, Producto.id != id, Producto.empresa_id == empresa_id).first()
        if existente:
            flash(f'El código {nuevo_codigo} ya está siendo usado por otro producto.', 'danger')
            return redirect(request.url)

        nuevo_codigo_barras = request.form.get('codigo_barras', '').strip()
        if nuevo_codigo_barras:
            existente_cb = Producto.query.filter(Producto.codigo_barras == nuevo_codigo_barras, Producto.id != id, Producto.empresa_id == empresa_id).first()
            if existente_cb:
                flash(f'El código de barras {nuevo_codigo_barras} ya está registrado.', 'danger')
                return redirect(request.url)

        cat_id = resolve_categoria(request.form)
        subcat_id = resolve_subcategoria(request.form, cat_id)

        try:
            producto.codigo = nuevo_codigo
            producto.codigo_barras = nuevo_codigo_barras or None
            producto.nombre = request.form.get('nombre').strip()
            producto.descripcion = request.form.get('descripcion', '').strip()
            producto.marca = request.form.get('marca', '').strip()
            producto.categoria_id = cat_id
            producto.subcategoria_id = subcat_id
            producto.proveedor = request.form.get('proveedor', '').strip()
            producto.costo = float(request.form.get('costo') or 0)
            producto.precio = float(request.form.get('precio') or 0)
            producto.stock_minimo = int(request.form.get('stock_minimo') or 1)
            producto.ubicacion = request.form.get('ubicacion', '').strip()
            producto.estado = request.form.get('estado', 'activo')
            producto.observaciones = request.form.get('observaciones', '').strip()

            db.session.commit()
            flash('Producto actualizado correctamente.', 'success')
            log_auditoria('EDITAR', 'productos', producto.id, {'codigo': producto.codigo, 'nombre': producto.nombre})
            return redirect(url_for('productos_bp.producto_detalle', id=producto.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {e}', 'danger')

    empresa_id = get_empresa_id()
    categorias = Categoria.query.filter_by(empresa_id=empresa_id).order_by(Categoria.nombre).all()
    subcategorias = Subcategoria.query.filter_by(empresa_id=empresa_id).order_by(Subcategoria.nombre).all()
    return render_template('productos/formulario.html', 
                           producto=producto, accion='Editar',
                           categorias=categorias, subcategorias=subcategorias)

@productos_bp.route('/productos/<int:id>/eliminar', methods=['POST'])
@login_required
@role_required('Administrador', 'Supervisor')
def producto_eliminar(id):
    empresa_id = get_empresa_id()
    producto = Producto.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()
    try:
        codigo = producto.codigo
        prod_id = producto.id
        db.session.delete(producto)
        db.session.commit()
        flash(f'Producto {codigo} eliminado del sistema.', 'success')
        log_auditoria('ELIMINAR', 'productos', prod_id, {'codigo': codigo})
    except Exception as e:
        db.session.rollback()
        flash(f'No se pudo eliminar el producto. Error: {e}', 'danger')
        
    return redirect(url_for('productos_bp.productos_lista'))
