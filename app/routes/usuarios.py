from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Usuario
from app.utils.decorators import admin_required

usuarios_bp = Blueprint('usuarios_bp', __name__)

@usuarios_bp.route('/usuarios')
@login_required
@admin_required
def usuarios_lista():
    usuarios = Usuario.query.all()
    return render_template('usuarios/lista.html', usuarios=usuarios)

@usuarios_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def usuario_nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        es_admin = True if request.form.get('es_admin') else False

        if Usuario.query.filter_by(email=email).first():
            flash('Ya existe un usuario con ese email.', 'danger')
            return redirect(request.url)

        nuevo_usuario = Usuario(nombre=nombre, email=email, es_admin=es_admin)
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('usuarios_bp.usuarios_lista'))

    return render_template('usuarios/formulario.html', usuario=None, accion='Nuevo')

@usuarios_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def usuario_editar(id):
    usuario = Usuario.query.get_or_404(id)

    if request.method == 'POST':
        usuario.nombre = request.form.get('nombre').strip()
        
        nuevo_email = request.form.get('email').strip()
        if nuevo_email != usuario.email:
            if Usuario.query.filter_by(email=nuevo_email).first():
                flash('El email ya está en uso por otro usuario.', 'danger')
                return redirect(request.url)
            usuario.email = nuevo_email

        if request.form.get('password'):
            usuario.set_password(request.form.get('password'))

        # Only allow changing admin status/active if it's not the last admin
        # or if you are not trying to demote yourself
        if current_user.id != usuario.id:
            usuario.es_admin = True if request.form.get('es_admin') else False
            usuario.activo = True if request.form.get('activo') else False
        else:
            if not request.form.get('es_admin') or not request.form.get('activo'):
                flash('No podés quitarte privilegios de administrador ni desactivar tu propia cuenta.', 'warning')

        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('usuarios_bp.usuarios_lista'))

    return render_template('usuarios/formulario.html', usuario=usuario, accion='Editar')

@usuarios_bp.route('/usuarios/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def usuario_eliminar(id):
    if current_user.id == id:
        flash('No podés eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('usuarios_bp.usuarios_lista'))

    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado.', 'success')
    return redirect(url_for('usuarios_bp.usuarios_lista'))
