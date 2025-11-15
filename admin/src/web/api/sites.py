from flask import jsonify, request, current_app
from sqlalchemy import func, desc, asc
from geoalchemy2 import functions as geofunc
from . import api_bp
from .auth import api_auth_required
from src.core.database import db
from src.core.historicalSites.site import Site
from src.core.historicalSites.tags.tag import Tag
from src.core.reseñas.reseña import Reseña
from src.core.reseñas import get_reviews_by_site, get_reviews_by_site_paginated
from flask import session


@api_bp.route("/sites", methods=["GET"])
def list_sites():
    """
    GET /api/sites?name=&description=&city=&province=&tags=&lat=&long=&radius=&order_by=latest&page=1&per_page=12
    Devuelve sitios visibles filtrados y paginados.
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
    page = max(1, request.args.get("page", type=int) or 1)
    per_page = min(max(1, request.args.get("per_page", type=int) or 12), 100)

    q = db.session.query(Site).filter(
        Site.deleted.is_(False), Site.visibility.is_(True)
    )

    # ----- filtros
    if name:
        q = q.filter(Site.name.ilike(f"%{name.strip()}%"))
    if description:
        q = q.filter(Site.description.ilike(f"%{description.strip()}%"))
    if city:
        q = q.filter(func.lower(Site.city) == city.strip().lower())
    if province:
        q = q.filter(func.lower(Site.province) == province.strip().lower())

    # ----- tags
    if tags:
        tag_names = [t.strip().lower() for t in tags.split(",") if t.strip()]
        if tag_names:
            q = q.join(Site.tags).filter(func.lower(Tag.name).in_(tag_names))

    # ----- geolocalización (usa PostGIS)
    if lat is not None and lng is not None and radius_km:
        try:
            radius_m = float(radius_km) * 1000.0
            q = q.filter(
                geofunc.ST_DWithin(
                    Site.location,
                    func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326),
                    radius_m,
                )
            )
        except Exception as e:
            print(f"[WARN] filtro geográfico deshabilitado: {e}")

    # ----- orden
    if order_by == "oldest":
        q = q.order_by(asc(Site.registration_date))
    else:  # latest por defecto
        q = q.order_by(desc(Site.registration_date))

    # ----- total + paginación
    total = q.count()
    sites = q.offset((page - 1) * per_page).limit(per_page).all()

    # ----- respuesta
    # Leer configuración de MinIO desde config
    minio_endpoint = current_app.config.get("MINIO_ENDPOINT", "localhost:9000")
    bucket_name = current_app.config.get("MINIO_BUCKET_NAME", "grupo37")
    minio_secure = current_app.config.get("MINIO_SECURE", False)
    protocol = "https" if minio_secure else "http"

    data = []
    for s in sites:
        # 🔹 Buscar imagen principal: la de menor order (0 o 1)
        main_image = None
        if s.images:
            # Ordenar por 'order' y tomar la primera
            sorted_images = sorted(
                s.images, key=lambda img: img.order if img.order is not None else 999
            )
            main_image = sorted_images[0] if sorted_images else None

        # Construir URL
        cover_url = None
        if main_image:
            # El campo es 'url', no 'object_name'
            cover_url = f"{protocol}://{minio_endpoint}/{bucket_name}/{main_image.url}"

        data.append(
            {
                "id": s.id,
                "name": s.name,
                "city": s.city,
                "province": s.province,
                "latitude": s.latitude,
                "longitude": s.longitude,
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

    # Construir URLs de imágenes desde MinIO
    minio_endpoint = current_app.config.get("MINIO_ENDPOINT", "localhost:9000")
    bucket_name = current_app.config.get("MINIO_BUCKET_NAME", "grupo37")
    minio_secure = current_app.config.get("MINIO_SECURE", False)
    protocol = "https" if minio_secure else "http"

    images = []
    for img in sorted(
        site.images, key=lambda x: x.order if x.order is not None else 999
    ):
        images.append(
            {
                "id": img.id,
                "url": f"{protocol}://{minio_endpoint}/{bucket_name}/{img.url}",
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


@api_bp.route("/sites/<int:site_id>/favorite", methods=["PUT"])
# @api_auth_required
def put_site_as_fav(site_id):
    """
    PUT /sites/{site_id}/favorite
    Marca un sitio como favorito para el usuario autenticado.
    Requiere autenticación - retorna 401 si no está logueado.
    """
    from src.core.users import marcar_favorito, get_user_by_id

    try:
        user_id = session.get("user") or 1
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

        user = get_user_by_id(user_id)

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
