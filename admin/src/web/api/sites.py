from flask import jsonify, request, current_app
from sqlalchemy import func, desc, asc
from geoalchemy2 import functions as geofunc
from . import api_bp
from .validators import validate_params, validate_latitude, validate_longitude
from .exceptions import NotFoundError, ValidationError
from src.core.database import db
from src.core.historicalSites.site import Site
from src.core.historicalSites.tags.tag import Tag
from src.web import helpers



@api_bp.route("/sites", methods=["GET"])
@validate_params({
    'lat': {'type': float, 'validate': validate_latitude},
    'long': {'type': float, 'validate': validate_longitude},
    'radius': {'type': float, 'min': 0.1, 'max': 500},
    'page': {'type': int, 'min': 1},
    'per_page': {'type': int, 'min': 1, 'max': 100},
    'order_by': {'type': str, 'choices': ['latest', 'oldest', 'rating-5-1', 'rating-1-5']},
})
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
            details={
                "radius": ["Required when using lat/long"]
            }
        )
    
    if (lat is not None or lng is not None or radius_km is not None):
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
                }
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
            q = q.filter(
                geofunc.ST_DWithin(
                    Site.location,
                    func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326),
                    radius_m,
                )
            )
        except Exception as e:
            raise ValidationError(
                message="Geographic filter failed",
                details={"geo": [str(e)]}
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
