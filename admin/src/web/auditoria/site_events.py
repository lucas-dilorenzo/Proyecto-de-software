from sqlalchemy import event
from flask import session
from src.core.database import db
from src.core.historicalSites.site import Site, SiteLog

# 🔹 Helper para obtener el user_id desde la sesión
def get_current_user_id():
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
        {"site_id": target.id, "user_id": user_id, "action": "CREATED", "details": target.name},
    )


# @event.listens_for(Site, "after_update")
# def after_update(mapper, connection, target):
#     user_id = get_current_user_id()
#     if not user_id:
#         return

#     connection.execute(
#         SiteLog.__table__.insert(),
#         {"site_id": target.id, "user_id": user_id, "action": "UPDATED"},
#     )


# @event.listens_for(Site, "after_delete")
# def after_delete(mapper, connection, target):
#     user_id = get_current_user_id()
#     if not user_id:
#         return

#     connection.execute(
#         SiteLog.__table__.insert(),
#         {"site_id": target.id, "user_id": user_id, "action": "DELETED"},
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
