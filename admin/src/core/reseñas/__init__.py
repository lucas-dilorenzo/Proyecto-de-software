from src.core.database import db
from src.core.reseñas.reseña import Reseña
from src.core.users.user import User
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import joinedload
from datetime import datetime
from src.core.historicalSites.site import Site


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


def get_reviews_by_site_paginated(site_id: int, page: int = 1, per_page: int = 10):
    """
    Devuelve las reseñas de un sitio específico con paginación.
    Args:
        site_id (int): ID del sitio histórico.
        page (int): Número de página (por defecto 1).
        per_page (int): Cantidad de reseñas por página (por defecto 10).
    Returns:
        Pagination: Objeto de paginación de SQLAlchemy con las reseñas.
        None: Si el sitio no existe o hay error.
    """
    try:
        # Verificar que el sitio existe y es válido

        site = (
            db.session.query(Site)
            .filter_by(id=site_id, deleted=False, visibility=True)
            .first()
        )

        if not site:
            return None

        # Construir consulta base con orden por fecha de creación descendente (solo reseñas aprobadas)
        from src.core.reseñas.estadoReseña import estadoReseña

        query = (
            db.session.query(Reseña)
            .filter(Reseña.site_id == site_id)
            .filter(Reseña.estado == estadoReseña.APROBADA.code)
            .order_by(Reseña.fecha_creacion.desc(), Reseña.id.desc())
        )

        # Aplicar paginación usando SQLAlchemy paginate()
        return query.paginate(page=page, per_page=per_page, error_out=False)

    except Exception as e:
        print(f"Error al obtener reseñas paginadas por site_id: {e}")
        return None


def validate_review_data(data, site_id, user_id):
    """
    Valida los datos de una reseña para su creación.
    Args:
        data (dict): Datos de la reseña a validar.
        site_id (int): ID del sitio histórico asociado.
        user_id (int): ID del usuario que crea la reseña.
    Returns:
        tuple: (is_valid (bool), errors (list))
    """
    errors = []

    # Validar calificacion (entre 1 y 5)
    calificacion = data.get("rating")
    if calificacion is None:
        errors.append("La calificación es obligatoria.")
    elif not isinstance(calificacion, int) or not (1 <= calificacion <= 5):
        errors.append("La calificación debe estar entre 1 y 5.")

    # Validar contenido
    contenido = data.get("comment", "").strip()
    if contenido is not None and len(contenido) > 500:
        errors.append("El comentario no puede exceder los 500 caracteres.")

    # Validar unicidad de reseña por usuario y sitio
    existing_review = (
        db.session.query(Reseña)
        .filter(and_(Reseña.site_id == site_id, Reseña.user_id == user_id))
        .first()
    )
    if existing_review:
        errors.append(
            "Ya existe una reseña para este sitio por el usuario especificado."
        )

    return (False, errors) if errors else (True, None)


def create_review(site_id, user_id, calificacion, comentario):
    """
    Crea una nueva reseña en la base de datos.
    Args:
        site_id (int): ID del sitio histórico asociado.
        user_id (int): ID del usuario que crea la reseña.
        calificacion (int): Calificación de la reseña.
        contenido (str): Contenido de la reseña.
    Returns:
        Reseña: El objeto Reseña recién creado.
    """
    try:
        review = Reseña(
            site_id=site_id,
            user_id=user_id,
            calificacion=calificacion,
            contenido=comentario,
        )
        session = db.session
        session.add(review)
        session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear reseña: {e}")
        raise ValueError(f"No se pudo crear la reseña: {e}")
    return review


def get_review_by_id(review_id):
    return db.session.query(Reseña).filter(Reseña.id == review_id).first()


def delete_review(review_id):
    try:
        review = get_review_by_id(review_id)
        if review:
            db.session.delete(review)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar reseña: {e}")
        return False


def update_review(review_id, calificacion, comentario):
    """
    Actualiza una reseña existente con nuevos valores de calificación y comentario.
    Solo se pueden editar reseñas en estado 'pendiente'.
    Args:
        review_id (int): ID de la reseña a actualizar
        calificacion (int): Nueva calificación (1-5)
        comentario (str): Nuevo comentario
    Returns:
        Reseña: El objeto Reseña actualizado si fue exitoso
        None: Si no se encontró la reseña o no está en estado pendiente
    """
    from src.core.reseñas.estadoReseña import estadoReseña
    
    try:
        review = get_review_by_id(review_id)
        if not review:
            return None
            
        # Solo permitir editar reseñas en estado pendiente
        if review.estado != estadoReseña.PENDIENTE.code:
            return None
            
        # Actualizar los campos
        review.calificacion = calificacion
        review.contenido = comentario
        
        db.session.commit()
        return review
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar reseña: {e}")
        return None


def get_reviews_by_user_paginated(user_id: int, page: int = 1, per_page: int = 10):
    """
    Devuelve las reseñas creadas por un usuario específico con paginación.
    Args:
        user_id (int): ID del usuario.
        page (int): Número de página (por defecto 1).
        per_page (int): Cantidad de reseñas por página (por defecto 10).
    Returns:
        Pagination: Objeto de paginación de SQLAlchemy con las reseñas.
    """
    try:
        query = (
            db.session.query(Reseña)
            .filter(Reseña.user_id == user_id)
            .order_by(Reseña.fecha_creacion.desc(), Reseña.id.desc())
        )

        return query.paginate(page=page, per_page=per_page, error_out=False)

    except Exception as e:
        print(f"Error al obtener reseñas paginadas por user_id: {e}")
        return None
