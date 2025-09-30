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

# Busca un tag por su ID
# Args: id (int): El ID del tag a buscar.
# Return: Tag: El objeto Tag si se encuentra, de lo contrario None.
def get_tag_by_id(id: int):
    query = db.session.query(Tag).filter_by(id=id).first()
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

# Crea un nuevo tag en la base de datos
# Args: kwargs: Los datos del tag (name, slug, description).
# Returns Tag: El objeto Tag recién creado.
def update_tag(tag_id, **kwargs):
    tag = Tag.query.get(tag_id)
    if not tag:
        raise ValueError("El tag no existe.")
    # Actualizar solo las claves que existan en el modelo
    for key, value in kwargs.items():
        if hasattr(tag, key):
            setattr(tag, key, value)
    db.session.commit()
    return tag

# Función para generar un slug a partir de un texto(nombre del tag)
# Args: text (str): El texto del cual generar el slug.
# Returns str: El slug generado.
def crear_slug(text):
    # 1. Paso a minúsculas
    text = text.lower()
    # 2. Saco acentos 
    reemplazos = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "à": "a", "è": "e", "ì": "i", "ò": "o", "ù": "u",
        "ä": "a", "ë": "e", "ï": "i", "ö": "o", "ü": "u",
        "ñ": "n",
    }
    texto_sin_acentos = ""
    for c in text:
        if c in reemplazos:
            texto_sin_acentos += reemplazos[c]
        else:
            texto_sin_acentos += c
    # 3. Reemplazo espacios por guiones
    texto_slug = ""
    for c in texto_sin_acentos:
        if c == " ":
            texto_slug += "-"
        # 4. Solo dejo letras, números y guiones
        elif c.isalnum() or c == "-":
            texto_slug += c
        # ignorar cualquier otro caracter
    # 5. Evitar guiones duplicados o al borde
    while "--" in texto_slug:
        texto_slug = texto_slug.replace("--", "-")
    texto_slug = texto_slug.strip("-")
    return texto_slug


def get_tags(busqueda: str = None):
    """
    Retorna una lista de Tag ordenados por nombre. 
    Si viene cargado el parametro busqueda, lo filtro.
    """
    query = db.session.query(Tag)
    if busqueda:
        query = query.filter(Tag.name.ilike(f"%{busqueda}%"))
    return query.order_by(Tag.name.asc(), Tag.created_at.desc()).all()

def delete_tag(tag_id):
    tag = get_tag_by_id(tag_id)
    if not tag:
        return False
    db.session.delete(tag)
    db.session.commit()