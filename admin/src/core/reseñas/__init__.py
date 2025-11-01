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
    joinedload(Reseña.user), 
    joinedload(Reseña.site)
)

    # Aplicar filtros basados en los parámetros proporcionados
    if estado:
        estado_q = estado.strip()
        if estado_q:
            query = query.filter(Reseña.estado == estado_q)
    if site_id:
        if site_id:
            query = query.filter(Reseña.site_id == site_id)
    if calificacion is not None:
        query = query.filter(Reseña.calificacion == calificacion)
    # Filtrar por texto contenido en el email del usuario (case-insensitive)
    if usuario:
        user_q = usuario.strip()
        if user_q:
            q = f"%{user_q}%"
            # Hacemos join con User para poder filtrar por su email
            query = query.join(Reseña.user).filter(User.email.ilike(q))
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
            pass # Ignorar fecha_desde inválida

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
            pass # Ignorar fecha_hasta inválida

    # Ordenamiento
    order_field = Reseña.fecha_creacion
    if order_by == 'calificacion':
        order_field = Reseña.calificacion

    # Añadir ordenamiento secundario por ID para garantizar consistencia
    if str(order).lower() == 'desc':
        query = query.order_by(order_field.desc(), Reseña.id.desc())
    else:
        query = query.order_by(order_field.asc(), Reseña.id.asc())

    return query.paginate(page=page, per_page=per_page, error_out=False)