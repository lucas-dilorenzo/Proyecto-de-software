from src.core.images.images import Image
from src.core.database import db


def create_image(
    site_id: int, url: str, order: int = 0, titulo: str = None, descripcion: str = None
) -> Image:
    """Create a new Image instance.
    Args:
        site_id (int): The ID of the associated site.
        url (str): The URL of the image.
        order (int, optional): The display order of the image. Defaults to 0.
        titulo (str, optional): The title of the image. Defaults to None.
        descripcion (str, optional): The description of the image. Defaults to None.

    Returns:
        Image: The created Image instance.
    """
    image = Image(
        site_id=site_id, url=url, order=order, titulo=titulo, descripcion=descripcion
    )
    db.session.add(image)
    db.session.commit()
    return image


def delete_image(image: Image) -> None:
    """Delete an Image instance.
    Args:
        image (Image): The Image instance to be deleted.
    """

    db.session.delete(image)
    db.session.commit()


def get_image_by_id(image_id: int) -> Image:
    """Retrieve an image by its unique ID.
    Args:
        image_id (int): The ID of the image.

    Returns:
        Image: The Image instance with the specified ID.
    """
    image = Image.query.get(image_id)
    return image if image else None


def get_images_by_site(site_id: int) -> list:
    """Retrieve all images associated with a specific site.
    Args:
        site_id (int): The ID of the site.

    Returns:
        list: A list of Image instances associated with the site.
    """
    images = Image.query.filter_by(site_id=site_id).order_by(Image.order).all()
    return images if images else []


def get_main_image_by_site(site_id: int) -> Image:
    """Retrieve the main image associated with a specific site.
    Args:
        site_id (int): The ID of the site.

    Returns:
        Image: The main Image instance associated with the site.
    """
    main_image = Image.query.filter_by(site_id=site_id, order=0).first()
    return main_image if main_image else None


def get_secondary_images_by_site(site_id: int) -> list:
    """Retrieve all secondary images associated with a specific site.
    Args:
        site_id (int): The ID of the site.

    Returns:
        list: A list of secondary Image instances associated with the site.
    """
    secondary_images = (
        Image.query.filter(Image.site_id == site_id, Image.order != 0)
        .order_by(Image.order)
        .all()
    )
    return secondary_images if secondary_images else []


def set_image_order(image: Image, new_order: int) -> None:
    """Set the display order of an image.
    Args:
        image (Image): The Image instance to be updated.
        new_order (int): The new display order for the image.
    """

    # buscar si otra imagen tiene ese order en ese site, y si lo tiene, intercambiar los orders
    existing_image = Image.query.filter_by(
        site_id=image.site_id, order=new_order
    ).first()
    if existing_image:
        existing_image.order = image.order
    image.order = new_order
    db.session.commit()


def edit_image_metadata(
    image: Image, titulo: str = None, descripcion: str = None
) -> None:
    """Edit the metadata of an image.
    Args:
        image (Image): The Image instance to be updated.
        titulo (str, optional): The new title for the image. Defaults to None.
        descripcion (str, optional): The new description for the image. Defaults to None.
    """
    if titulo is not None:
        image.titulo = titulo
    if descripcion is not None:
        image.descripcion = descripcion
    db.session.commit()


def get_max_order_for_site(site_id):
    """Obtiene el order máximo de las imágenes de un sitio"""

    max_order = (
        db.session.query(db.func.max(Image.order)).filter_by(site_id=site_id).scalar()
    )
    return max_order if max_order is not None else 0
