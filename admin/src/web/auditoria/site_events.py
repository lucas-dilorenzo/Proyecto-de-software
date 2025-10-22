from sqlalchemy import event, inspect
from flask import session
from src.core.database import db
from src.core.historicalSites.site import Site, SiteLog
import json
import datetime

# Importaciones para manejo de geometrías
try:
    from geoalchemy2.shape import to_shape
    from geoalchemy2 import WKBElement

    GEOALCHEMY_AVAILABLE = True
except ImportError:
    GEOALCHEMY_AVAILABLE = False


# 🔹 Helper para obtener el user_id desde la sesión
def get_current_user_id():
    """Retrieve the current user's ID from the session.
    Returns:
        int or None: The user ID if available, None otherwise."""
    if session is None:
        return
    user = session.get("user")
    if not user:
        return None
    return user.get("id") if isinstance(user, dict) else user


# -------------------- EVENTOS SQLALCHEMY -------------------- #
@event.listens_for(Site, "after_insert")
def after_insert(mapper, connection, target):
    """Log the creation of a new Site.
    Args:
        mapper: The mapper.
        connection: The database connection.
        target (Site): The Site instance that was created."""
    user_id = get_current_user_id()
    if not user_id:
        return

    connection.execute(
        SiteLog.__table__.insert(),
        {
            "site_id": target.id,
            "user_id": user_id,
            "action": "Alta",
            "details": target.name,
        },
    )


@event.listens_for(Site, "after_update")
def after_update(mapper, connection, target):
    """Log modifications made to a Site.
    Args:
        mapper: The mapper.
        connection: The database connection.
        target (Site): The Site instance that was modified."""
    user_id = get_current_user_id()
    if not user_id:
        return

    state = inspect(target)
    changes = {}

    def serialize_value(v):
        """Try to convert v into a JSON-serializable value.

        Rules:
        - None, str, int, float, bool kept as-is
        - date/datetime -> ISO string
        - list/tuple/set -> list with serialized elements
        - Geometry objects -> WKT format for consistent comparison
        - SQLAlchemy mapped instances -> try to expose identity and repr
        - Fallback to str(v)
        """
        # primitives
        if v is None or isinstance(v, (str, int, float, bool)):
            return v

        # datetimes / dates
        if isinstance(v, (datetime.datetime, datetime.date)):
            try:
                return v.isoformat()
            except Exception:
                return str(v)

        # Geometry objects (GeoAlchemy2)
        if GEOALCHEMY_AVAILABLE and (
            hasattr(v, "desc")
            or (
                isinstance(v, str)
                and (v.startswith("POINT(") or v.startswith("0101000020"))
            )
        ):
            try:
                # If it's already a WKT string, return normalized
                if isinstance(v, str) and v.startswith("POINT("):
                    return v
                # If it has desc attribute (GeoAlchemy geometry), get WKT
                elif hasattr(v, "desc"):
                    # Try to get the WKT representation
                    shape = to_shape(v)
                    return shape.wkt
                # If it's a WKB hex string, convert to WKT
                elif (
                    isinstance(v, str)
                    and len(v) > 20
                    and all(c in "0123456789abcdefABCDEF" for c in v)
                ):
                    wkb_element = WKBElement(bytes.fromhex(v))
                    shape = to_shape(wkb_element)
                    return shape.wkt
            except Exception as e:
                # If geometry conversion fails, fallback to string
                print(f"Warning: Could not serialize geometry value {v}: {e}")
                pass

        # collections
        if isinstance(v, (list, tuple, set)):
            return [serialize_value(x) for x in v]

        # try JSON dump directly
        try:
            json.dumps(v)
            return v
        except TypeError:
            pass

        # SQLAlchemy mapped instance: expose primary key identity if available
        try:
            insp = inspect(v)
            # if inspect() returns an object with identity, use it
            identity = getattr(insp, "identity", None)
            if identity:
                return {"_sa_identity": identity, "repr": str(v)}
        except Exception:
            # not a mappable object
            pass

        # fallback
        return str(v)

    # Recorro los atributos del objeto para detectar cambios
    for attr in state.attrs:
        # Obtengo el historial de cambios de cada atributo
        hist = attr.history
        # Veo si hay cambios en el atributo
        if hist.has_changes():
            old_value = serialize_value(hist.deleted[0]) if hist.deleted else None
            new_value = serialize_value(hist.added[0]) if hist.added else None
            if old_value != new_value:
                # Si hubo cambio, lo registro en el diccionario (serializando valores)
                changes[attr.key] = {"old": old_value, "new": new_value}

    if not changes:
        return  # No hubo cambios relevantes
    if "deleted" in changes:
        # Si el cambio fue en el campo "deleted", registro una acción específica
        if changes["deleted"] == {"old": False, "new": True}:
            connection.execute(
                SiteLog.__table__.insert(),
                {
                    "site_id": target.id,
                    "user_id": user_id,
                    "action": "Eliminado",
                    "details": changes,
                },
            )
    else:
        print(changes)
        connection.execute(
            SiteLog.__table__.insert(),
            {
                "site_id": target.id,
                "user_id": user_id,
                "action": "Modificacion",
                "details": changes,
            },
        )


# # 🔹 Eventos sobre la relación many-to-many (tags)
# @event.listens_for(Site.tags, "append")
# def tag_added(target, value, initiator):
#     user_id = get_current_user_id()
#     if not user_id:
#         return
#     db.session.add(
#         SiteLog(site_id=target.id, user_id=user_id, action=f"TAG_ADDED:{value.id}")
#     )


# @event.listens_for(Site.tags, "remove")
# def tag_removed(target, value, initiator):
#     user_id = get_current_user_id()
#     if not user_id:
#         return
#     db.session.add(
#         SiteLog(site_id=target.id, user_id=user_id, action=f"TAG_REMOVED:{value.id}")
#     )
