from src.core.database import db
from src.core.reseñas.reseña import Reseña
from src.core.users.user import User
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import joinedload
from datetime import datetime


def get_review_by_id(review_id):
    return db.session.query(Reseña).filter(Reseña.id == review_id).first()


def get_reviews_paginated(
    page: int = 1,
    per_page: int = 25,
    order: str = "desc",
    order_by: str = "fecha_creacion",
    estado: str = None,
    site_id: int = None,
    calificacion: int = None,
    fecha_desde: str = None,
    fecha_hasta: str = None,
    usuario: str = None,
):
    """
    Retorna reseñas paginadas aplicando filtros para moderación.
    """
    query = db.session.query(Reseña).options(
        joinedload(Reseña.user), joinedload(Reseña.site)
    )

    if estado:
        estado_q = estado.strip()
        if estado_q:
            query = query.filter(Reseña.estado == estado_q)
    if site_id:
        if site_id:
            query = query.filter(Reseña.site_id == site_id)
    if calificacion is not None:
        query = query.filter(Reseña.calificacion == calificacion)
    if usuario:
        user_q = usuario.strip()
        if user_q:
            q = f"%{user_q}%"
            query = query.join(User, Reseña.user_id == User.id).filter(
                or_(User.nombre.ilike(q), User.apellido.ilike(q))
            )
    if fecha_desde:
        try:
            s = fecha_desde.strip()
            df = None
            try:
                df = datetime.fromisoformat(s).date()
            except Exception:
                from datetime import datetime as _dt

                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                    try:
                        df = _dt.strptime(s, fmt).date()
                        break
                    except Exception:
                        continue

            if df:
                query = query.filter(func.date(Reseña.fecha_creacion) >= df)
        except Exception:
            pass  # Ignorar fecha_desde inválida

    # Fecha Hasta
    if fecha_hasta:
        try:
            s = fecha_hasta.strip()
            dt = None
            try:
                dt = datetime.fromisoformat(s).date()
            except Exception:
                from datetime import datetime as _dt

                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                    try:
                        dt = _dt.strptime(s, fmt).date()
                        break
                    except Exception:
                        continue

            if dt:
                query = query.filter(func.date(Reseña.fecha_creacion) <= dt)
        except Exception:
            pass  # Ignorar fecha_hasta inválida

    # Ordenamiento
    order_field = Reseña.fecha_creacion
    if order_by == "calificacion":
        order_field = Reseña.calificacion

    # Añadir ordenamiento secundario por ID para garantizar consistencia
    if str(order).lower() == "desc":
        query = query.order_by(order_field.desc(), Reseña.id.desc())
    else:
        query = query.order_by(order_field.asc(), Reseña.id.asc())

    return query.paginate(page=page, per_page=per_page, error_out=False)


def aprobar_reseña(review_id):
    """
    Aprueba una reseña cambiando su estado a 'aprobada'.
    Args:
        review_id (int): ID de la reseña a aprobar
    Returns:
        bool: True si se aprobó correctamente, False si no se encontró o hubo error
    """
    from src.core.reseñas.estadoReseña import estadoReseña

    try:
        review = get_review_by_id(review_id)
        if not review:
            return False

        review.estado = estadoReseña.APROBADA.code
        review.motivo_rechazo = None  # Limpiar cualquier motivo de rechazo previo

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al aprobar reseña: {e}")
        return False


def rechazar_reseña(review_id, motivo_rechazo):
    """
    Rechaza una reseña cambiando su estado a 'rechazada' y guardando el motivo.
    Args:
        review_id (int): ID de la reseña a rechazar
        motivo_rechazo (str): Motivo del rechazo
    Returns:
        bool: True si se rechazó correctamente, False si no se encontró o hubo error
    """
    from src.core.reseñas.estadoReseña import estadoReseña

    try:
        review = get_review_by_id(review_id)
        if not review:
            return False

        review.estado = estadoReseña.RECHAZADA.code
        review.motivo_rechazo = motivo_rechazo

        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al rechazar reseña: {e}")
        return False


def eliminar_reseña(review_id):
    """
    Elimina permanentemente una reseña de la base de datos.
    Args:
        review_id (int): ID de la reseña a eliminar
    Returns:
        bool: True si se eliminó correctamente, False si no se encontró o hubo error
    """
    try:
        review = get_review_by_id(review_id)
        if not review:
            return False

        db.session.delete(review)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar reseña: {e}")
        return False


def get_reviews_by_site(site_id):
    """
    Devuelve las reseñas correspondientes a un sitio histórico específico.
    Args:
        site_id (int): ID del sitio histórico.
    Returns:
        list: Una lista de objetos Reseña asociados con el sitio.
    """
    try:
        reviews = db.session.query(Reseña).filter(Reseña.site_id == site_id).all()
        return reviews
    except Exception as e:
        print(f"Error al obtener reseñas por site_id: {e}")
        return []
