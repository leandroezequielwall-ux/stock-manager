from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.utils.security import get_empresa_id
from app.models import Empresa
from app.extensions import db
from app.utils.decorators import admin_required

billing_bp = Blueprint('billing_bp', __name__)

@billing_bp.route('/suscripcion')
@login_required
@admin_required
def index():
    empresa_id = get_empresa_id()
    empresa = Empresa.query.get(empresa_id)
    
    return render_template('billing/index.html', empresa=empresa)

@billing_bp.route('/suscripcion/checkout/stripe', methods=['POST'])
@login_required
@admin_required
def checkout_stripe():
    # Esqueleto para Stripe Checkout Session
    # Aquí iría el código con la librería stripe: stripe.checkout.Session.create(...)
    flash('Redirigiendo a Stripe (Modo Simulación)', 'info')
    
    # SIMULACIÓN: Activar plan instantáneamente (Solo para fines de desarrollo)
    empresa_id = get_empresa_id()
    empresa = Empresa.query.get(empresa_id)
    plan = request.form.get('plan')
    
    empresa.plan = plan
    empresa.estado = 'Activa'
    empresa.payment_provider = 'stripe'
    db.session.commit()
    
    flash(f'¡Suscripción a {plan} activada con éxito (Simulada)!', 'success')
    return redirect(url_for('billing_bp.index'))

@billing_bp.route('/suscripcion/checkout/mercadopago', methods=['POST'])
@login_required
@admin_required
def checkout_mercadopago():
    # Esqueleto para MercadoPago Preapproval
    # Aquí iría el código con mercadopago SDK para generar la URL de suscripción
    flash('Redirigiendo a Mercado Pago (Modo Simulación)', 'info')
    
    # SIMULACIÓN: Activar plan instantáneamente
    empresa_id = get_empresa_id()
    empresa = Empresa.query.get(empresa_id)
    plan = request.form.get('plan')
    
    empresa.plan = plan
    empresa.estado = 'Activa'
    empresa.payment_provider = 'mercadopago'
    db.session.commit()
    
    flash(f'¡Suscripción a {plan} activada con éxito (Simulada)!', 'success')
    return redirect(url_for('billing_bp.index'))

@billing_bp.route('/suscripcion/cancelar', methods=['POST'])
@login_required
@admin_required
def cancelar_suscripcion():
    empresa_id = get_empresa_id()
    empresa = Empresa.query.get(empresa_id)
    
    # Aquí iría la lógica para cancelar la suscripción en el proveedor (Stripe/MP)
    
    empresa.plan = 'Starter'
    empresa.payment_provider = None
    db.session.commit()
    
    flash('Suscripción cancelada. Has regresado al plan Starter.', 'warning')
    return redirect(url_for('billing_bp.index'))
