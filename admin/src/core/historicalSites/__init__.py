# from core.database import db
from src.core.database import db
from src.core.historicalSites.site import Site
from sqlalchemy import or_, func
from datetime import datetime
from src.core.historicalSites.tags.tag import Tag
from geoalchemy2 import WKTElement


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
    site = Site(
        name=kwargs.get("name"),
        description_short=kwargs.get("description_short"),
        description=kwargs.get("description"),
        city=kwargs.get("city"),
        province=kwargs.get("province"),
        location=WKTElement(f"POINT({kwargs.get('location')})", srid=4326),
        conservation_status=kwargs.get("conservation_status"),
        year_declared=kwargs.get("year_declared"),
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
        setattr(site, key, value)
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
    db.session.delete(site)
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

    # def get_sites_paginated_by_id(page: int = 1, per_page: int = 25, order: str = "asc"):
    #     """
    #     Retrieves a paginated list of historical sites from the database.
    #     Args:
    #         page (int): The page number to retrieve (default is 1).
    #         per_page (int): The number of sites to display per page (default is 25).
    #         order (str): The order in which to sort the sites by id ('asc' for ascending(default), 'desc' for descending; default is 'asc').
    #     Returns:
    #         sites: A query containing the paginated list of sites and pagination metadata.
    #     """
    #     if order == "desc":
    #         sites = Site.query.order_by(Site.id.desc()).paginate(
    #             page=page, per_page=per_page, error_out=False
    #         )
    #     else:
    #         sites = Site.query.order_by(Site.id.asc()).paginate(
    #             page=page, per_page=per_page, error_out=False
    #         )
    #     return sites


def get_sites_paginated_by_id(
    page: int = 1,
    per_page: int = 25,
    order: str = "asc",
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
    query = Site.query

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

    # ordenar
    if order == "desc":
        query = query.order_by(Site.name.desc())
    else:
        query = query.order_by(Site.name.asc())

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
