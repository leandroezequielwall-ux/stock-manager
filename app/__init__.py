from flask import Flask, redirect, url_for
from app.config import Config
from app.extensions import db, login_manager
from app.database.migrations import migrate_database

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    from app.extensions import migrate
    migrate.init_app(app, db, render_as_batch=True)

    # User loader for Flask-Login
    from app.models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    # Context processors
    @app.context_processor
    def inject_alertas():
        from flask_login import current_user
        from app.models import Producto
        from app.utils.security import get_empresa_id
        if current_user.is_authenticated and current_user.empresa_id:
            empresa_id = get_empresa_id()
            alertas_count = Producto.query.filter(
                Producto.stock <= Producto.stock_minimo,
                Producto.empresa_id == empresa_id
            ).count()
            return dict(alertas_count=alertas_count)
        return dict(alertas_count=0)

    # Middleware global para verificar suscripción
    from flask import request
    @app.before_request
    def verificar_suscripcion():
        from flask_login import current_user
        from flask import flash
        
        # Ignorar rutas estáticas
        if request.endpoint and request.endpoint.startswith('static'):
            return
            
        # Rutas permitidas incluso si está suspendida (login, logout, facturación, superadmin)
        rutas_permitidas = [
            'auth_bp.login', 
            'auth_bp.logout', 
            'auth_bp.registro',
            'billing_bp.index',
            'billing_bp.checkout_stripe',
            'billing_bp.checkout_mercadopago',
            'billing_bp.cancelar_suscripcion'
        ]
        
        if request.endpoint in rutas_permitidas or (request.endpoint and request.endpoint.startswith('superadmin')):
            return
            
        if current_user.is_authenticated and current_user.rol != 'SuperAdmin':
            from app.models import Empresa
            empresa = db.session.get(Empresa, current_user.empresa_id)
            if empresa and empresa.estado == 'Suspendida':
                flash('El acceso a tu empresa está suspendido por falta de pago o vencimiento de la suscripción.', 'danger')
                return redirect(url_for('billing_bp.index'))

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return redirect(url_for('dashboard_bp.dashboard'))

    @app.errorhandler(401)
    def unauthorized(e):
        return redirect(url_for('auth_bp.login'))

    # Register Blueprints
    from app.routes import (
        auth_bp, dashboard_bp, productos_bp, 
        categorias_bp, movimientos_bp, usuarios_bp
    )
    from app.routes.categorias import categorias_bp
    from app.routes.superadmin import superadmin_bp
    from app.routes.auditoria import auditoria_bp
    from app.routes.billing import billing_bp
    from app.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(movimientos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(superadmin_bp)
    app.register_blueprint(auditoria_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Automatically migrate DB schema contextually if needed
    with app.app_context():
        migrate_database()

    return app
