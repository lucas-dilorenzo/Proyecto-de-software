from src.core.historicalSites.site import Site  # noqa: F401
from core.historicalSites.tags.tag import Tag  # noqa: F401
from src.core.database import db

# Retorna todos los tags con nombre ascendente
def get_all_tags():
    session = db.session
    query = Tag.query.order_by(Tag.name.asc()).all()
    return query