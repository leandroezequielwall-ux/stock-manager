import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-super-secreta-cambiar-en-produccion')
    
    # Path Configuration (supports PyInstaller bundle)
    if getattr(sys, 'frozen', False):
        # Running as compiled .exe
        BUNDLE_DIR = sys._MEIPASS
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        # Running as python script
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    DB_PATH = os.path.join(BASE_DIR, 'inventario.db')
    
    # Use DATABASE_URL from .env (for PostgreSQL) or fallback to SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
