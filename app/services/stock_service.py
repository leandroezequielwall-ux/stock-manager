from app.extensions import db
from app.models import Movimiento
from app.utils.security import get_empresa_id

from flask_login import current_user

def registrar_movimiento(producto, tipo, cantidad, motivo):
    """
    Business logic for recording a stock movement and updating product stock.
    Runs within the current DB session but does NOT call db.session.commit()
    so it can be wrapped in a larger transaction by the caller.
    """
    if tipo == 'ENTRADA':
        producto.stock += cantidad
    elif tipo == 'SALIDA':
        if producto.stock < cantidad:
            raise ValueError(f"Stock insuficiente para {producto.codigo}")
        producto.stock -= cantidad
    else:
        raise ValueError(f"Tipo de movimiento inválido: {tipo}")

    empresa_id = get_empresa_id()
    mov = Movimiento(
        producto_id=producto.id,
        tipo=tipo,
        cantidad=cantidad,
        motivo=motivo,
        empresa_id=empresa_id
    )
    db.session.add(mov)
    db.session.add(producto)
    db.session.commit()  # Committing here since this is the primary action
