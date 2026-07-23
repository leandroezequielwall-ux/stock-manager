from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.security import get_empresa_id
from app.extensions import db
from app.models import Usuario, Empresa
from app.utils.decorators import admin_required
from app.utils.planes import PLANES_LIMITES
from app.utils.auditoria import log_auditoria

usuarios_bp = Blueprint('usuarios_bp', __name__)

@usuarios_bp.route('/usuarios')
@login_required
@admin_required
def usuarios_lista():
    empresa_id = get_empresa_id()
    usuarios = Usuario.query.filter_by(empresa_id=empresa_id).all()
    return render_template('usuarios/lista.html', usuarios=usuarios)

@usuarios_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def usuario_nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        rol = request.form.get('rol') or 'Operador'

        empresa_id = get_empresa_id()
        empresa = Empresa.query.get(empresa_id)
        
        # Validar límites del plan
        if empresa:
            plan_actual = empresa.plan
            limites = PLANES_LIMITES.get(plan_actual, PLANES_LIMITES['Starter'])
            max_usuarios = limites['max_usuarios']
            
            usuarios_actuales = Usuario.query.filter_by(empresa_id=empresa_id).count()
            if usuarios_actuales >= max_usuarios:
                flash(f'Has alcanzado el límite de {max_usuarios} usuarios de tu plan {plan_actual}.', 'warning')
                return redirect(url_for('usuarios_bp.usuarios_lista'))

        if Usuario.query.filter_by(email=email, empresa_id=empresa_id).first():
            flash('Ya existe un usuario con ese email en tu empresa.', 'danger')
            return redirect(request.url)

        nuevo_usuario = Usuario(
            nombre=nombre, 
            email=email, 
            rol=rol,
            empresa_id=empresa_id
        )
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario creado exitosamente.', 'success')
        log_auditoria('CREAR', 'usuarios', nuevo_usuario.id, {'email': nuevo_usuario.email, 'rol': nuevo_usuario.rol})
        return redirect(url_for('usuarios_bp.usuarios_lista'))

    return render_template('usuarios/formulario.html', usuario=None, accion='Nuevo')

@usuarios_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def usuario_editar(id):
    empresa_id = get_empresa_id()
    usuario = Usuario.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()

    if request.method == 'POST':
        usuario.nombre = request.form.get('nombre').strip()
        
        nuevo_email = request.form.get('email').strip()
        if nuevo_email != usuario.email:
            if Usuario.query.filter_by(email=nuevo_email, empresa_id=empresa_id).first():
                flash('El email ya está en uso por otro usuario.', 'danger')
                return redirect(request.url)
            usuario.email = nuevo_email

        if request.form.get('password'):
            usuario.set_password(request.form.get('password'))

        # Only allow changing active or rol if it's not the last admin
        # or if you are not trying to demote yourself
        if current_user.id != usuario.id:
            usuario.rol = request.form.get('rol') or 'Operador'
            usuario.activo = True if request.form.get('activo') else False
        else:
            if request.form.get('rol') != 'Administrador' or not request.form.get('activo'):
                flash('No podés quitarte privilegios de administrador ni desactivar tu propia cuenta.', 'warning')

        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        log_auditoria('EDITAR', 'usuarios', usuario.id, {'email': usuario.email, 'rol': usuario.rol, 'activo': usuario.activo})
        return redirect(url_for('usuarios_bp.usuarios_lista'))

    return render_template('usuarios/formulario.html', usuario=usuario, accion='Editar')

@usuarios_bp.route('/usuarios/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def usuario_eliminar(id):
    if current_user.id == id:
        flash('No podés eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('usuarios_bp.usuarios_lista'))

    empresa_id = get_empresa_id()
    usuario = Usuario.query.filter_by(id=id, empresa_id=empresa_id).first_or_404()
    email = usuario.email
    user_id = usuario.id
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado.', 'success')
    log_auditoria('ELIMINAR', 'usuarios', user_id, {'email': email})
    return redirect(url_for('usuarios_bp.usuarios_lista'))
