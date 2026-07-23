import os
from sqlalchemy import text
from app.extensions import db
from app.config import Config

def migrate_database():
    # No ejecutar esta migración si estamos usando PostgreSQL
    if Config.SQLALCHEMY_DATABASE_URI.startswith("postgres"):
        return

    # Migrate from automotive-specific schema to generic schema if needed.
    if not os.path.exists(Config.DB_PATH):
        return

    try:
        # Check if 'productos' table exists
        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'"))
        table_exists = result.fetchone()

        if not table_exists:
            # Step 1: Rename the table from 'repuestos' to 'productos'
            db.session.execute(text("ALTER TABLE repuestos RENAME TO productos"))

            # Step 2: Read current schema of 'productos'
            pragma_result = db.session.execute(text("PRAGMA table_info(productos)"))
            columns = [row[1] for row in pragma_result.fetchall()]

            # Add missing columns
            if 'codigo_barras' not in columns:
                db.session.execute(text("ALTER TABLE productos ADD COLUMN codigo_barras VARCHAR(50)"))
                db.session.execute(text("CREATE UNIQUE INDEX ix_productos_codigo_barras ON productos(codigo_barras)"))
            if 'estado' not in columns:
                db.session.execute(text("ALTER TABLE productos ADD COLUMN estado VARCHAR(20) DEFAULT 'activo'"))
            if 'subcategoria_id' not in columns:
                db.session.execute(text("ALTER TABLE productos ADD COLUMN subcategoria_id INTEGER REFERENCES subcategorias(id)"))

            # Migrate data: nombre = marca + modelo, descripcion = motor
            if 'modelo' in columns and 'motor' in columns:
                db.session.execute(text("""
                    UPDATE productos 
                    SET nombre = marca || ' ' || COALESCE(modelo, ''),
                        descripcion = COALESCE(motor, '')
                    WHERE nombre IS NULL OR nombre = ''
                """))
            db.session.commit()
            print("[INFO] Migración de tabla 'repuestos' a 'productos' completada.")
        else:
            # Table already renamed, just ensure new columns exist (for instances updated post-rename)
            pragma_result = db.session.execute(text("PRAGMA table_info(productos)"))
            columns = [row[1] for row in pragma_result.fetchall()]

            added_cols = False
            if 'codigo_barras' not in columns:
                db.session.execute(text("ALTER TABLE productos ADD COLUMN codigo_barras VARCHAR(50)"))
                db.session.execute(text("CREATE UNIQUE INDEX ix_productos_codigo_barras ON productos(codigo_barras)"))
                added_cols = True
            if 'estado' not in columns:
                db.session.execute(text("ALTER TABLE productos ADD COLUMN estado VARCHAR(20) DEFAULT 'activo'"))
                added_cols = True
            if 'subcategoria_id' not in columns:
                db.session.execute(text("ALTER TABLE productos ADD COLUMN subcategoria_id INTEGER REFERENCES subcategorias(id)"))
                added_cols = True

            if added_cols:
                db.session.commit()
                print("[INFO] Esquema de 'productos' actualizado con nuevos campos.")

        # Ensure 'subcategorias' table exists
        subcat_result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='subcategorias'"))
        if not subcat_result.fetchone():
            db.session.execute(text("""
                CREATE TABLE subcategorias (
                    id INTEGER NOT NULL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    categoria_id INTEGER NOT NULL,
                    FOREIGN KEY(categoria_id) REFERENCES categorias (id),
                    CONSTRAINT uix_subcat_nombre_categoria UNIQUE (nombre, categoria_id)
                )
            """))
            db.session.commit()
            print("[INFO] Tabla 'subcategorias' creada mediante migración.")

    except Exception as e:
        print(f"[ERROR] Ocurrió un error durante la migración: {e}")
        db.session.rollback()
