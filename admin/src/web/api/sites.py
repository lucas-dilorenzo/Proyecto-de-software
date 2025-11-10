from flask import jsonify, request, current_app
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
            sorted_images = sorted(s.images, key=lambda img: img.order if img.order is not None else 999)
            main_image = sorted_images[0] if sorted_images else None

        # Construir URL
        cover_url = None
        if main_image:
            # El campo es 'url', no 'object_name'
            cover_url = f"{protocol}://{minio_endpoint}/{bucket_name}/{main_image.url}"

        data.append({
            "id": s.id,
            "name": s.name,
            "city": s.city,
            "province": s.province,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "avg_rating": None,
            "cover_image": cover_url,
        })

    return jsonify({
        "data": data,
        "page": page,
        "per_page": per_page,
        "total": total,
    })

@api_bp.route("/sites/<int:site_id>", methods=["GET"])
def get_site(site_id):
    """
    GET /api/sites/:id
    Devuelve un sitio específico con todas sus imágenes y datos.
    """
    # 🔹 Usar SQLAlchemy directamente en lugar del módulo
    site = db.session.query(Site).filter_by(id=site_id, deleted=False, visibility=True).first()
    
    if not site:
        return jsonify({"error": "Sitio no encontrado"}), 404
    
    # Construir URLs de imágenes desde MinIO
    minio_endpoint = current_app.config.get("MINIO_ENDPOINT", "localhost:9000")
    bucket_name = current_app.config.get("MINIO_BUCKET_NAME", "grupo37")
    minio_secure = current_app.config.get("MINIO_SECURE", False)
    protocol = "https" if minio_secure else "http"
    
    images = []
    for img in sorted(site.images, key=lambda x: x.order if x.order is not None else 999):
        images.append({
            "id": img.id,
            "url": f"{protocol}://{minio_endpoint}/{bucket_name}/{img.url}",
            "titulo": img.titulo,
            "descripcion": img.descripcion,
            "order": img.order,
        })
    
    # Construir respuesta
    return jsonify({
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
    })