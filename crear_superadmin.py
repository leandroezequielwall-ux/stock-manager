from app import create_app
from app.extensions import db
from app.models import Usuario

app = create_app()

def crear_superadmin(email, password):
    with app.app_context():
        # Verificar si el email ya existe
        existente = Usuario.query.filter_by(email=email).first()
        if existente:
            print(f"Error: El email {email} ya está registrado.")
            return

        superadmin = Usuario(
            nombre="System Owner",
            email=email,
            rol="SuperAdmin",
            empresa_id=None # El SuperAdmin no pertenece a ninguna empresa inquilina
        )
        superadmin.set_password(password)

        db.session.add(superadmin)
        db.session.commit()
        print(f"SuperAdmin creado con éxito: {email}")

if __name__ == '__main__':
    print("=== Creación de SuperAdmin Global ===")
    email = input("Email: ").strip()
    password = input("Contraseña: ").strip()
    if email and password:
        crear_superadmin(email, password)
    else:
        print("El email y la contraseña son obligatorios.")
