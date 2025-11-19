from flask import jsonify, request, session
from flask_jwt_extended import jwt_required
from sqlalchemy import func, desc, asc
from geoalchemy2 import functions as geofunc
from geoalchemy2.types import Geography
from . import api_bp
from .validators import validate_params, validate_latitude, validate_longitude
from .exceptions import NotFoundError, ValidationError
from .auth import api_auth_required
from src.core.database import db
from src.core.historicalSites.site import Site
from src.core.historicalSites import get_site_by_id
from src.core.historicalSites.tags.tag import Tag
from src.core.reseñas.reseña import Reseña
from src.core.reseñas import (
    get_reviews_by_site_paginated,
    get_reviews_by_site,
    validate_review_data,
    create_review,
    get_review_by_id,
    delete_review,
)
from src.web import helpers
from src.core.historicalSites import tags as tags_service
from flask_jwt_extended import get_jwt_identity, jwt_required


@api_bp.route("/sites/", methods=["GET"])
@validate_params(
    {
        "lat": {"type": float, "validate": validate_latitude},
        "long": {"type": float, "validate": validate_longitude},
        "radius": {"type": float, "min": 0.1, "max": 500},
        "page": {"type": int, "min": 1},
        "per_page": {"type": int, "min": 1, "max": 100},
        "order_by": {
            "type": str,
            "choices": ["latest", "oldest", "rating-5-1", "rating-1-5"],
        },
    }
)
def list_sites():
    """
    GET /api/sites - Lista sitios con filtros y paginación
    """
    name = request.args.get("name", type=str)
    description = request.args.get("description", type=str)
    city = request.args.get("city", type=str)
    province = request.args.get("province", type=str)
    tags = request.args.get("tags", type=str)
    lat = request.args.get("lat", type=float)
    lng = request.args.get("long", type=float)
    radius_km = request.args.get("radius", type=float)
    order_by = request.args.get("order_by", "latest")
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get("per_page", type=int, default=12)

    if (lat is not None or lng is not None) and radius_km is None:
        raise ValidationError(
            message="Geographic search requires lat, long, and radius parameters",
            details={"radius": ["Required when using lat/long"]},
        )

    if lat is not None or lng is not None or radius_km is not None:
        if lat is None or lng is None or radius_km is None:
            missing = []
            if lat is None:
                missing.append("lat")
            if lng is None:
                missing.append("long")
            if radius_km is None:
                missing.append("radius")

            raise ValidationError(
                message="Geographic search requires all three parameters: lat, long, and radius",
                details={
                    param: ["Required for geographic search"] for param in missing
                },
            )

    q = db.session.query(Site).filter(
        Site.deleted.is_(False), Site.visibility.is_(True)
    )

    # Filtros de texto
    if name:
        q = q.filter(Site.name.ilike(f"%{name.strip()}%"))
    if description:
        q = q.filter(Site.description.ilike(f"%{description.strip()}%"))
    if city:
        q = q.filter(func.lower(Site.city) == city.strip().lower())
    if province:
        q = q.filter(func.lower(Site.province) == province.strip().lower())

    # Tags
    if tags:
        tag_names = [t.strip().lower() for t in tags.split(",") if t.strip()]
        if tag_names:
            q = q.join(Site.tags).filter(func.lower(Tag.name).in_(tag_names))

    # Geolocalización
    if lat is not None and lng is not None and radius_km:
        try:
            radius_m = float(radius_km) * 1000.0
            # Usar ST_DWithin con geography para trabajar con metros reales
            q = q.filter(
                geofunc.ST_DWithin(
                    func.cast(Site.location, Geography),
                    func.cast(
                        func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326),
                        Geography,
                    ),
                    radius_m,
                )
            )
        except Exception as e:
            raise ValidationError(
                message="Geographic filter failed", details={"geo": [str(e)]}
            )

    # Orden
    if order_by == "oldest":
        q = q.order_by(asc(Site.registration_date))
    else:
        q = q.order_by(desc(Site.registration_date))

    # Paginación
    total = q.count()
    sites = q.offset((page - 1) * per_page).limit(per_page).all()

    # ----- respuesta

    data = []
    for s in sites:
        main_image = None
        if s.images:
            # Ordenar por 'order' y tomar la primera
            sorted_images = sorted(
                s.images, key=lambda img: img.order if img.order is not None else 999
            )
            main_image = sorted_images[0] if sorted_images else None

        cover_url = None
        if main_image:
            # El campo es 'url', no 'object_name'
            cover_url = helpers.get_image_url(main_image.url)

        data.append(
            {
                "id": s.id,
                "name": s.name,
                "description_short": s.description_short,
                "description": s.description,
                "city": s.city,
                "province": s.province,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "conservation_status": s.conservation_status,
                "years_declared": s.year_declared,
                "category": s.category,
                "registration_date": s.registration_date,
                "avg_rating": None,
                "cover_image": cover_url,
            }
        )

    return jsonify(
        {
            "data": data,
            "page": page,
            "per_page": per_page,
            "total": total,
        }
    )


@api_bp.route("/sites/<int:site_id>", methods=["GET"])
def get_site(site_id):
    """
    GET /api/sites/:id
    Devuelve un sitio específico con todas sus imágenes y datos.
    """
    # 🔹 Usar SQLAlchemy directamente en lugar del módulo
    site = (
        db.session.query(Site)
        .filter_by(id=site_id, deleted=False, visibility=True)
        .first()
    )

    if not site:
        return jsonify({"error": "Sitio no encontrado"}), 404

    images = []
    for img in sorted(
        site.images, key=lambda x: x.order if x.order is not None else 999
    ):
        url_ = helpers.get_image_url(img.url)
        images.append(
            {
                "id": img.id,
                "url": url_,
                "titulo": img.titulo,
                "descripcion": img.descripcion,
                "order": img.order,
            }
        )

    # Construir respuesta
    return jsonify(
        {
            "id": site.id,
            "name": site.name,
            "description": site.description,
            "city": site.city,
            "province": site.province,
            "latitude": float(site.latitude) if site.latitude else None,
            "longitude": float(site.longitude) if site.longitude else None,
            "conservation_status": site.conservation_status,
            "avg_rating": None,  # TODO: calcular promedio real de ratings
            "tags": [tag.name for tag in site.tags] if site.tags else [],
            "images": images,
        }
    )


@api_bp.route("/sites/<int:site_id>/reviews", methods=["GET"])
@api_auth_required
def get_site_reviews(site_id):
    """
    GET /api/sites/:id/reviews?page=1&per_page=10
    Devuelve las reseñas de un sitio específico con paginación.
    Requiere autenticación - retorna 401 si no está logueado.

    Parámetros:
    - page: Número de página (por defecto 1)
    - per_page: Reseñas por página, 1-100 (por defecto 10)
    """
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        if not (1 <= per_page <= 100):
            # Bad request si per_page no está en el rango válido error 400
            return (
                jsonify(
                    {
                        "error": {
                            "code": "invalid_data",
                            "message": "Invalid input data",
                            "details": {"per_page": ["Must be between 1 and 100"]},
                        }
                    }
                ),
                400,
            )

        # Obtener reseñas paginadas usando la función del core
        reviews_paginated = get_reviews_by_site_paginated(
            site_id=site_id, page=page, per_page=per_page
        )

        if reviews_paginated is None:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "not_found",
                            "message": "Site not found",
                        }
                    }
                ),
                404,
            )

        # Construir respuesta con los datos paginados
        data = []
        for r in reviews_paginated.items:
            data.append(
                {
                    "id": r.id,
                    "site_id": r.site_id,
                    "rating": r.calificacion,
                    "comment": r.contenido,
                    "inserted_at": r.fecha_creacion,
                    "updated_at": r.fecha_creacion,
                }
            )

        return jsonify(
            {
                "data": data,
                "meta": {
                    "page": reviews_paginated.page,
                    "per_page": reviews_paginated.per_page,
                    "total": reviews_paginated.total,
                },
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error occurred",
                    }
                }
            ),
            500,
        )


# @api_bp.route("/sites/<int:site_id>/reviews", methods=["POST"])
# @api_auth_required
# def create_site_review(site_id):
#     """
#     POST /api/sites/:id/reviews
#     Crea una nueva reseña para un sitio (requiere autenticación).
#     Retorna 401 si no está autenticado.
#     """
#     try:
#         data = request.get_json()

#         if not data:
#             return jsonify({
#                 "error": {
#                     "code": "invalid_data",
#                     "message": "JSON data required"
#                 }
#             }), 400

#         # Aquí irían las validaciones y creación de la reseña
#         # Por ahora solo devolvemos un ejemplo

#         return jsonify({
#             "message": "Review created successfully",
#             "data": {
#                 "id": 123,
#                 "site_id": site_id,
#                 "rating": data.get("rating"),
#                 "comment": data.get("comment")
#             }
#         }), 201


#     except Exception as e:
#         return jsonify({
#             "error": {
#                 "code": "internal_error",
#                 "message": "Internal server error"
#             }
#         }), 500


@api_bp.route("/sites/<int:site_id>/reviews", methods=["POST"])
@api_auth_required
def create_site_review(site_id):
    """
    POST /api/sites/:id/reviews
    Crea una nueva reseña para un sitio (requiere autenticación).
    Retorna 401 si no está autenticado.
    """
    try:
        # Verificación adicional de usuario (por seguridad)
        user_id = session.get("user")
        if user_id is None:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "unauthorized",
                            "message": "Authentication required to create reviews",
                        }
                    }
                ),
                401,
            )

        if get_site_by_id(site_id) is None:
            return (
                jsonify({"error": {"code": "not_found", "message": "Site not found"}}),
                404,
            )
        # validaciones y creación de la reseña
        is_valid, errors = validate_review_data(request.json, site_id, user_id)

        if not is_valid:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "invalid_data",
                            "message": "Invalid input data",
                            "details": errors,
                        }
                    }
                ),
                400,
            )

        print("DEBUG: Datos válidos, creando reseña...")
        new_review = create_review(
            site_id=site_id,
            user_id=user_id,
            calificacion=request.json.get("calificacion"),
            comentario=request.json.get("contenido"),
        )

        return (
            jsonify(
                {
                    "message": "Review created successfully",
                    "data": {
                        "site_id": site_id,
                        "rating": request.json.get("calificacion"),
                        "comment": request.json.get("contenido"),
                        "inserted_at": new_review.fecha_creacion,
                        "updated_at": new_review.fecha_creacion,
                    },
                }
            ),
            201,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error occurred",
                    }
                }
            ),
            500,
        )


@api_bp.route("/sites/<int:site_id>/reviews/<int:review_id>", methods=["DELETE"])
@api_auth_required
def delete_site_review(site_id, review_id):
    """
    DELETE /api/sites/:site_id/reviews/:review_id
    Elimina una reseña existente (solo si pertenece al usuario autenticado).
    """

    try:
        user_id = session.get("user")

        # Verificación adicional de usuario (por seguridad)
        if user_id is None:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "unauthorized",
                            "message": "Authentication required to delete reviews",
                        }
                    }
                ),
                401,
            )
        # Busco la reseña
        review_to_delete = get_review_by_id(review_id)
        # Manejo del Error 404 (Reseña no encontrada)
        if review_to_delete is None:
            return (
                jsonify(
                    {"error": {"code": "not_found", "message": "Review not found"}}
                ),
                404,
            )

        # Esto asegura que la URL sea canónica (ej: /sites/10/reviews/5 no puede eliminar la reseña 5 si pertenece al sitio 20)
        if review_to_delete.site_id != site_id:
            return (
                jsonify(
                    {"error": {"code": "not_found", "message": "Review not found"}}
                ),
                404,
            )

        # Manejo del Error 403 (No tiene permiso), asumo que solo el dueño de la reseña puede eliminarla
        if review_to_delete.user_id != user_id:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "forbidden",
                            "message": "You do not have permission to delete this review",
                        }
                    }
                ),
                403,
            )

        # Elimino la reseña
        success = delete_review(review_id)

        if not success:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "server_error",
                            "message": "Failed to delete review",
                        }
                    }
                ),
                500,
            )

        # Respuesta Exitosa 204 No Content
        return "", 204

    except Exception:
        # 8. Manejo del Error 500 (Server Error)
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error occurred",
                    }
                }
            ),
            500,
        )


@api_bp.route("/tags/", methods=["GET"])
def get_tags():
    """
    GET /api/tags
    Devuelve la lista de todos los tags disponibles.
    """
    tags = tags_service.get_tags()

    data = []
    for tag in tags:
        data.append(
            {
                "id": tag.id,
                "name": tag.name,
                "slug": tag.slug,
                "description": tag.description,
                "created_at": tag.created_at,
            }
        )

    return jsonify({"data": data})


@api_bp.route("/sites/provinces/", methods=["GET"])
def get_provinces():
    """
    GET /api/sites/provinces
    Devuelve la lista de todas las provincias de los sitios registrados.
    """
    provinces = (
        db.session.query(Site.province)
        .filter(Site.deleted.is_(False), Site.visibility.is_(True))
        .distinct()
        .order_by(asc(Site.province))
        .all()
    )

    province_list = [p.province for p in provinces if p.province]

    return jsonify({"data": province_list})


@api_bp.route("/sites/<int:site_id>/favorite", methods=["PUT"])
@jwt_required()
def put_site_as_fav(site_id):
    """
    PUT /sites/{site_id}/favorite
    Marca un sitio como favorito para el usuario autenticado.
    Requiere autenticación - retorna 401 si no está logueado.
    """
    from src.core.users import marcar_favorito, get_user_by_id

    print("DEBUG: Llamada a PUT /sites/{site_id}/favorite")

    try:
        # user_id = session.get("user")
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "unauthorized",
                            "message": "Authentication required",
                        }
                    }
                ),
                401,
            )

        user = get_user_by_id(int(user_id))

        success = marcar_favorito(user, site_id)
        if not success:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "not_found",
                            "message": "Site not found",
                        }
                    }
                ),
                404,
            )
        # esta devolución 200, debería ser la 204 que marca la espicificación de API?
        return "", 204

    except Exception as e:
        print(f"Error desconocido al cargar el sitio favorito: {e}")
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error ocurred",
                    }
                }
            ),
            500,
        )


@api_bp.route("/sites/<int:site_id>/favorite", methods=["DELETE"])
# @api_auth_required
def delete_site_from_fav(site_id):
    """
    DELETE /sites/{site_id}/favorite
    Quita un sitio de favoritos para el usuario autenticado.
    Requiere autenticación - retorna 401 si no está logueado.
    """

    from src.core.users import eliminar_favorito, get_user_by_id

    try:
        user_id = session.get("user") or 1
        if not user_id:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "unauthorized",
                            "message": "Authentication requiered",
                        }
                    }
                ),
                401,
            )

        user = get_user_by_id(user_id)

        success = eliminar_favorito(user, site_id)
        if not success:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "not_found",
                            "message": "Site not found",
                        }
                    }
                ),
                404,
            )

        return "", 204

    except Exception as e:
        print(f"Error desconocido al eliminar el sitio del listado de favoritos: {e}")
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error ocurred",
                    }
                }
            ),
            500,
        )


@api_bp.route("/me/favorites", methods=["GET"])
@jwt_required()
def get_user_favs():
    """
    GET /me/favorites?page=1&per_page=20
    Obtiene todos los sitios favoritos del usuario autenticado.
    Requiere autenticación - retorna 401 si no está logueado.

    Parámetros:
    - page: Número de página (por defecto 1)
    - per_page: sitios por página, 1-100 (por defecto 10)
    """
    from src.core.users import get_user_by_id, get_user_favs

    try:
        # Obtengo el id del usuario logeado
        user_id = get_jwt_identity()
        if not user_id:
            return (
                jsonify(
                    {
                        "error": {
                            "code": "unauthorized",
                            "message": "Authentication required",
                        }
                    }
                ),
                401,
            )
        # Obtengo el usuario
        user = get_user_by_id(int(user_id))

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        if not (1 <= per_page <= 100):
            return (
                jsonify(
                    {
                        "error": {
                            "code": "invalid_data",
                            "message": "Invalid input data",
                            "details": {"per_page": ["Must be between 1 and 100"]},
                        }
                    }
                ),
                400,
            )

        favs_sites = get_user_favs(user)

        total = len(favs_sites)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_favs = favs_sites[start:end]

        data = []
        for s in paginated_favs:
            data.append(
                {
                    "id": s.id,
                    "name": s.name,
                    "short_description": s.description,
                    "description": s.description,
                    "city": s.city,
                    "province": s.province,
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                    "tags": [tag.name for tag in s.tags] if s.tags else [],
                    "state_conservation": s.conservation_status,
                }
            )

        return jsonify(
            {
                "data": data,
                "meta": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                },
            }
        )

    except Exception as e:
        print(f"Error desconocido al obtener los sitios favoritos del usuario: {e}")
        return (
            jsonify(
                {
                    "error": {
                        "code": "server_error",
                        "message": "An unexpected error ocurred",
                    }
                }
            ),
            500,
        )
