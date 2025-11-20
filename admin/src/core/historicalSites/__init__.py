# from core.database import db
from src.core.users.user import User
from src.core.database import db
from src.core.historicalSites.site import Site
from src.core.historicalSites.site import SiteLog
from src.core.historicalSites.enums import ConservationStatus, SiteCategory
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import aliased
from datetime import datetime
from src.core.historicalSites.tags.tag import Tag
from geoalchemy2 import WKTElement
from src.core.historicalSites.site import SiteLog
from sqlalchemy.orm.attributes import flag_modified


def create_site(**kwargs):
    """
    Creates and saves a new Site instance in the database.

    Keyword Arguments:
        name (str): Name of the site.
        description_short (str): Short description of the site.
        description (str): Detailed description of the site.
        city (str): City where the site is located.
        province (str): Province where the site is located.
        location (str): Geographical location of the site.
        conservation_status (str): Current conservation status of the site.
        year_declared (int): Year the site was declared.
        category (str): Category of the site.
        registration_date (date): Date the site was registered.
        visibility (bool): Visibility status of the site.

    Returns:
        Site: The newly created Site object.
    """

    # Process location
    location = kwargs.get("location")
    if location is not None:
        location = WKTElement(f"POINT({location})", srid=4326)

    # Process year_declared to ensure it's an integer
    year_declared = kwargs.get("year_declared")
    if year_declared is not None:
        if isinstance(year_declared, str):
            try:
                year_declared = int(year_declared) if year_declared.strip() else None
            except (ValueError, TypeError):
                year_declared = None

    site = Site(
        name=kwargs.get("name"),
        description_short=kwargs.get("description_short"),
        description=kwargs.get("description"),
        city=kwargs.get("city"),
        province=kwargs.get("province"),
        location=location,
        conservation_status=kwargs.get("conservation_status"),
        year_declared=year_declared,
        category=kwargs.get("category"),
        registration_date=kwargs.get("registration_date"),
        visibility=kwargs.get("visibility", True),
    )
    db.session.add(site)
    db.session.commit()
    return site


def list_all_sites():
    """
    Retrieves all historical site records from the database.
    Returns:
        list: A list of Site objects representing all historical sites.
    """
    return Site.query.all()


def get_all_sites():
    """
    Retrieves all active historical site records from the database.
    Returns:
        list: A list of Site objects representing all active historical sites.
    """
    return Site.query.filter(Site.deleted == False).all()


def get_site_by_id(site_id: int):
    """
    Retrieve a Site object from the database by its unique ID.
    Args:
        site_id (int): The unique identifier of the site to retrieve.
    Returns:
        Site: The Site object with the specified ID, or None if not found.
    """
    return Site.query.filter(Site.id == site_id).first()


def get_site_by_name(name):
    """
    Retrieve a Site object from the database by its name.
    Args:
        name (str): The name of the site to search for.
    Returns:
        Site: The Site object with the specified name, or None if not found.
    """
    return Site.query.filter(Site.name == name).first()


def update_site(site_id, **kwargs):
    """
    Updates the attributes of a historical site with the given site_id.
    Retrieves the site object by its ID, updates its attributes based on the provided keyword arguments,
    commits the changes to the database, and returns the updated site object.
    Args:
        site_id (int): The unique identifier of the site to update.
        **kwargs: Arbitrary keyword arguments representing the attributes to update and their new values.
    Returns:
        The updated site object if found and updated successfully, otherwise None.
    """

    site = get_site_by_id(site_id)
    if not site:
        return None
    for key, value in kwargs.items():
        if key == "location" and value is not None:
            value = WKTElement(f"POINT({value})", srid=4326)
            print(f"Updating location to: {value}")
        elif key == "year_declared" and value is not None:
            # Ensure year_declared is always an integer
            if isinstance(value, str):
                try:
                    value = int(value) if value.strip() else None
                except (ValueError, TypeError):
                    value = None
        setattr(site, key, value)
    db.session.commit()
    return site


def add_image_to_site(site_id, object_name, main=False):
    """
    Adds an image to a historical site by its ID.
    Args:
        site_id (int): The unique identifier of the site to which the image will be added.
        object_name (str): The name/path of the image object to be added.
    Returns:
        Site: The updated Site object with the new image added, or None if the site does not exist.
    """

    site = get_site_by_id(site_id)
    if not site:
        return None

    if main:
        site.main_image = object_name
    else:
        if site.images is None:
            site.images = []
        site.images.append(object_name)

        flag_modified(site, "images")

    db.session.commit()
    return site


def delete_site(site_id: int):
    """
    Deletes a historical site from the database by its ID.
    Args:
        site_id (int): The unique identifier of the site to be deleted.
    Returns:
        bool: True if the site was successfully deleted, False if the site does not exist.
    """

    site = get_site_by_id(site_id)
    if not site:
        return False

    site.deleted = True
    db.session.commit()
    return True


def get_sites_paginated_by_name(page: int = 1, per_page: int = 25, order: str = "asc"):
    """
    Retrieves a paginated list of historical sites from the database.
    Args:
        page (int): The page number to retrieve (default is 1).
        per_page (int): The number of sites to display per page (default is 25).
        order (str): The order in which to sort the sites by name ('asc' for ascending(default), 'desc' for descending; default is 'asc').
    Returns:
        sites: A query containing the paginated list of sites and pagination metadata.
    """
    if order == "desc":
        sites = Site.query.order_by(Site.name.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        sites = Site.query.order_by(Site.name.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    return sites


def get_sites_paginated_by_id(
    page: int = 1,
    per_page: int = 25,
    # order: str = "asc",
    order="asc",
    order_by="name",
    city: str = None,
    province: str = None,
    tags: list = None,
    conservation_status: str = None,
    date_from: str = None,
    date_to: str = None,
    visibility: bool = None,
    search_text: str = None,
):
    """
    Retorna sitios paginados aplicando filtros opcionales.
    """
    query = Site.query.filter(Site.deleted == False)

    if city:
        city_q = city.strip()
        if city_q:
            query = query.filter(Site.city.ilike(f"%{city_q}%"))

    if province:
        province_q = province.strip()
        if province_q:
            query = query.filter(Site.province.ilike(f"%{province_q}%"))

    if conservation_status:
        cs_q = conservation_status.strip()
        if cs_q:
            query = query.filter(Site.conservation_status.ilike(f"%{cs_q}%"))

    if visibility is not None:
        query = query.filter(Site.visibility == visibility)

    if search_text:
        st_q = search_text.strip()
        if st_q:
            q = f"%{st_q}%"
            query = query.filter(
                or_(
                    Site.name.ilike(q),
                    Site.description_short.ilike(q),
                )
            )

    if tags:
        try:
            # Normalizar y convertir a enteros, ignorando valores vacíos
            tag_ids = [int(t) for t in tags if str(t).strip() != ""]
            if tag_ids:
                # Si se seleccionó un solo tag, filtrar por existencia (OR de 1)
                if len(tag_ids) == 1:
                    query = query.filter(Site.tags.any(Tag.id == tag_ids[0]))
                else:
                    # Para múltiples tags, requerir que el sitio tenga todos los tags (AND)
                    for tid in tag_ids:
                        query = query.filter(Site.tags.any(Tag.id == tid))
        except Exception:
            # ignore invalid tag ids
            pass

    # rango de fechas (registration_date)
    if date_from:
        try:
            s = date_from.strip()
            df = None
            # intentar parsear ISO primero, luego formatos comunes
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
                # comparar por la parte fecha (ignorar hora)
                query = query.filter(func.date(Site.registration_date) >= df)
        except Exception:
            pass

    if date_to:
        try:
            s = date_to.strip()
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
                query = query.filter(func.date(Site.registration_date) <= dt)
        except Exception:
            pass

    # Campos para ordenamiento
    order_fields = {
        "name": Site.name,
        "city": Site.city,
        "date": Site.registration_date,
    }
    field = order_fields.get(order_by, Site.name)

    # Aplicar orden asc o desc
    if order.lower() == "desc":
        query = query.order_by(field.desc())
    else:
        query = query.order_by(field.asc())
    # # ordenar
    # if order == "desc":
    #     query = query.order_by(Site.name.desc())
    # else:
    #     query = query.order_by(Site.name.asc())

    sites = query.paginate(page=page, per_page=per_page, error_out=False)
    return sites


def asignar_tags_a_sitio(site: Site, tags: list):
    """
    Asigna tags a un sitio histórico.
    Args:
        site (Site): El objeto Site al que se le asignarán los tags.
        tags (list): Una lista de objetos Tag a asignar al sitio.
    Returns:
        Site: El objeto Site actualizado con los tags asignados.
    """
    site.tags = tags
    db.session.commit()
    return site


def get_all_provinces():
    """
    Retorna una lista de todas las provincias.
    """
    return Site.query.with_entities(Site.province).distinct().all()


def get_site_logs(
    site_id=None,
    user_filtrado=None,
    action_filtrado=None,
    fecha_desde_filtrado=None,  # 'YYYY-MM-DD'
    fecha_hasta_filtrado=None,  # 'YYYY-MM-DD'
):
    """Devuelve los logs de un sitio ordenados por fecha descendente, filtra por condiciones de movimientos historial"""
    try:
        query = SiteLog.query.filter_by(site_id=site_id)
        if user_filtrado:
            query = query.filter(SiteLog.user_id == user_filtrado)
        if action_filtrado:
            query = query.filter(SiteLog.action == action_filtrado)
        if fecha_desde_filtrado:
            query = query.filter(SiteLog.timestamp >= fecha_desde_filtrado)
        if fecha_hasta_filtrado:
            query = query.filter(SiteLog.timestamp <= fecha_hasta_filtrado)

        logs = query.order_by(SiteLog.timestamp.desc()).all()
        return logs
    except Exception:
        return []


def get_deleted_sites():
    """Retorna todos los sitios marcados como eliminados (deleted == True)."""
    try:
        return Site.query.filter(Site.deleted == True).all()
    except Exception:
        return []


def get_sites_filtered(
    city=None,
    province=None,
    tags=None,  # lista de ids (str/int)
    conservation_status=None,
    date_from=None,  # 'YYYY-MM-DD'
    date_to=None,  # 'YYYY-MM-DD'
    visibility=None,  # None (no filtrar) | True | False
    search_text=None,
    order_by="name",  # name | city | registration_date
    order_dir="asc",  # asc | desc
    only_active=True,  # excluye eliminados
):
    q = Site.query

    if only_active:
        q = q.filter(Site.deleted == False)

    if city:
        q = q.filter(Site.city.ilike(f"%{city}%"))
    if province:
        q = q.filter(Site.province.ilike(f"%{province}%"))
    if conservation_status:
        q = q.filter(Site.conservation_status == conservation_status)
    if visibility is not None:
        q = q.filter(Site.visibility == bool(visibility))

    # Rango por fecha de registro
    if date_from:
        q = q.filter(Site.registration_date >= date_from)
    if date_to:
        q = q.filter(Site.registration_date <= date_to)

    # Texto libre: nombre, descripciones, ciudad, provincia
    if search_text:
        st = f"%{search_text}%"
        q = q.filter(
            or_(
                Site.name.ilike(st),
                Site.description_short.ilike(st),
                Site.description.ilike(st),
                Site.city.ilike(st),
                Site.province.ilike(st),
            )
        )

    # Tags (OR). Si querés AND, ver bloque comentado abajo.
    if tags:
        try:
            tag_ids = [int(t) for t in tags if str(t).strip() != ""]
        except Exception:
            tag_ids = []
        if tag_ids:
            q = q.join(Site.tags).filter(Tag.id.in_(tag_ids)).distinct()

        # === AND estricto (tiene TODOS los tags seleccionados) ===
        # for tid in tag_ids:
        #     alias_tag = aliased(Tag)
        #     q = q.join(alias_tag, Site.tags).filter(alias_tag.id == tid)

    # Orden seguro (whitelist)
    order_map = {
        "name": Site.name,
        "city": Site.city,
        "registration_date": Site.registration_date,
    }
    col = order_map.get(order_by, Site.name)
    if str(order_dir).lower() == "desc":
        q = q.order_by(col.desc())
    else:
        q = q.order_by(col.asc())

    return q.all()


def get_site_log_users(site_id):
    """Devuelve una lista de usuarios que han realizado acciones en un sitio específico.

    Args:
        site_id (int): ID del sitio del que queremos obtener los usuarios.

    Returns:
        list: Lista de diccionarios con id y nombre de usuarios únicos ordenados por nombre.
    """
    try:
        users = (
            db.session.query(User.id, User.nombre)
            .join(SiteLog)
            .filter(SiteLog.site_id == site_id)
            .distinct()
            .order_by(User.nombre)
            .all()
        )
        return [{"id": u[0], "nombre": u[1]} for u in users]
    except Exception:
        return []


def get_all_log_actions(site_id=None):
    """Devuelve una lista de todas las acciones únicas en los logs de sitios históricos.

    Args:
        site_id (int, optional): Si se proporciona, filtra las acciones solo para ese sitio.

    Returns:
        list[str]: Lista de acciones únicas ordenadas alfabéticamente.
    """
    try:
        query = db.session.query(SiteLog.action).distinct()

        if site_id is not None:
            query = query.filter(SiteLog.site_id == site_id)

        actions = query.order_by(SiteLog.action.asc()).all()
        return [a[0] for a in actions]
    except Exception:
        return []


"""
        logs = (
            SiteLog.query.filter_by(site_id=site_id)
            .order_by(SiteLog.timestamp.desc())
            .all()
        )
        # Rango por fecha de registro
        if fecha_desde_filtrado:
            logs = [log for log in logs if (log.site.registration_date >= fecha_desde_filtrado)]
            ##logs = logs.filter(Site.registration_date >= fecha_desde_filtrado)
        if fecha_hasta_filtrado:
            logs = [log for log in logs if (log.site.registration_date <= fecha_hasta_filtrado)]
            ##logs = logs.filter(Site.registration_date <= fecha_hasta_filtrado)

        if action_filtrado:
            logs = [log for log in logs if str(log.action) == str(action_filtrado)]
        if user_filtrado:
            logs = [log for log in logs if str(log.user_id) == str(user_filtrado)]
        return logs
        """
