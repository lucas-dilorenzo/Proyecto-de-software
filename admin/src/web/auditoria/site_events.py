from sqlalchemy import event, inspect
from flask import session
from src.core.database import db
from src.core.historicalSites.site import Site, SiteLog

# 🔹 Helper para obtener el user_id desde la sesión
def get_current_user_id():
    if session is None:
        return
    user = session.get("user")
    if not user:
        return None
    return user.get("id") if isinstance(user, dict) else user


# -------------------- EVENTOS SQLALCHEMY -------------------- #
@event.listens_for(Site, "after_insert")
def after_insert(mapper, connection, target):
    user_id = get_current_user_id()
    if not user_id:
        return

    connection.execute(
        SiteLog.__table__.insert(),
        {"site_id": target.id, "user_id": user_id, "action": "Alta", "details": target.name},
    )


@event.listens_for(Site, "after_update")
def after_update(mapper, connection, target):
    user_id = get_current_user_id()
    if not user_id:
        return

    state = inspect(target)
    changes = {}

    # Recorro los atributos del objeto para detectar cambios
    for attr in state.attrs:
        # Obtengo el historial de cambios de cada atributo
        hist = attr.history
        # Veo si hay cambios en el atributo 
        if hist.has_changes():
            old_value = hist.deleted[0] if hist.deleted else None
            new_value = hist.added[0] if hist.added else None
            if old_value != new_value:
                # Si hubo cambio, lo registro en el diccionario
                changes[attr.key] = {"old": old_value, "new": new_value}

    if not changes:
        return  # No hubo cambios relevantes            
    if "deleted" in changes:
        # Si el cambio fue en el campo "deleted", registro una acción específica
        if changes["deleted"] == {"old": False, "new": True}:
            connection.execute(
                SiteLog.__table__.insert(),
                {"site_id": target.id, "user_id": user_id, "action": "Eliminado", "details": target.name},
            )
    else:
        print(changes)
        connection.execute(
            SiteLog.__table__.insert(),
            {"site_id": target.id, "user_id": user_id, "action": "Modificacion", "details": target.name},
        )
        print("entré al else")

# @event.listens_for(Site, "after_delete")
# def after_delete(mapper, connection, target):
#     user_id = get_current_user_id()
#     if not user_id:
#         return

#     connection.execute(
#         SiteLog.__table__.insert(),
#         {"site_id": target.id, "user_id": user_id, "action": "Baja", "details": target.name},
#     )


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
