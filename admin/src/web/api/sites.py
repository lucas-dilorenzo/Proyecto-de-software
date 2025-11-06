from flask import jsonify, request
from sqlalchemy import func, desc, asc
from geoalchemy2 import functions as geofunc
from . import api_bp
from src.core.database import db
from src.core.historicalSites.site  import Site
from src.core.historicalSites.tags.tag import Tag

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

    q = db.session.query(Site).filter(Site.deleted.is_(False), Site.visibility.is_(True))

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
                    radius_m
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
    data = [
        {
            "id": s.id,
            "name": s.name,
            "city": s.city,
            "province": s.province,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "avg_rating": None,
            "cover_image": None,
        }
        for s in sites
    ]

    return jsonify({
        "data": data,
        "page": page,
        "per_page": per_page,
        "total": total,
    })
