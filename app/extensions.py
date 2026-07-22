from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# Configure login manager
login_manager.login_view = 'auth_bp.login'
login_manager.login_message = 'Por favor, iniciá sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'
