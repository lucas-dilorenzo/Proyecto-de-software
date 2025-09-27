from src.core.historicalSites.tags.tag import Tag  # noqa: F401
from src.core.database import db


# Retorna todos los tags con nombre ascendente
def get_all_tags():
    query = db.session.query(Tag).all()
    return query

# Busca un tag por su nombre
# Args: name (str): El nombre del tag a buscar.
# Return: Tag: El objeto Tag si se encuentra, de lo contrario None.
def get_tag_by_name(name: str):
    query = db.session.query(Tag).filter_by(name=name).first()
    return query

# Crea un nuevo tag en la base de datos
# Args: kwargs: Los datos del tag (name, slug, description).
# Returns Tag: El objeto Tag recién creado.
def create_tag(**kwargs):
    tag = Tag(**kwargs)
    session = db.session
    session.add(tag)
    session.commit()
    return tag