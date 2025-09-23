from src.core.historicalSites.site import Site  # noqa: F401
from src.core.database import db


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
    site = Site(**kwargs)
    db.session.add(site)
    db.session.commit()
    return site


def list_all_sites():
    """
    Retrieves all historical site records from the database.
    Returns:
        list: A list of Site objects representing all historical sites.
    """
    return db.session.query(Site).all()


def get_site_by_id(site_id: int):
    """
    Retrieve a Site object from the database by its unique ID.
    Args:
        site_id (int): The unique identifier of the site to retrieve.
    Returns:
        Site: The Site object with the specified ID, or None if not found.
    """
    return db.session.query(Site).filter(Site.id == site_id).first()


def get_site_by_name(name: str):
    """
    Retrieve a Site object from the database by its name.
    Args:
        name (str): The name of the site to search for.
    Returns:
        Site: The Site object with the specified name, or None if not found.
    """
    return db.session.query(Site).filter(Site.name == name).first()


def update_site(site_id: int, **kwargs):
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
