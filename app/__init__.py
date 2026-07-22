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
    migrate.init_app(app, db)

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
        if current_user.is_authenticated:
            alertas_count = Producto.query.filter(Producto.stock <= Producto.stock_minimo).count()
            return dict(alertas_count=alertas_count)
        return dict(alertas_count=0)

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
    from app.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(movimientos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Automatically migrate DB schema contextually if needed
    with app.app_context():
        migrate_database()

    return app
