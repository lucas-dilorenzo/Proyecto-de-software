from datetime import datetime, timezone
from src.core.database import db


class FeatureFlag(db.Model):
    __tablename__ = "feature_flags"

    key = db.Column(db.String(64), primary_key=True)
    value_bool = db.Column(db.Boolean, nullable=False, default=False)
    message = db.Column(db.String(200), nullable=False, default="")
    updated_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def set(self, *, value_bool: bool, message: str, user_id: int | None):
        self.value_bool = value_bool
        self.message = message or ""
        self.updated_by_user_id = user_id
        self.updated_at = datetime.now(datetime.timezone.utc)

    @staticmethod
    def get(key: str):
        return FeatureFlag.query.get(key)

    @staticmethod
    def ensure_defaults():
        defaults = [
            ("admin_maintenance_mode", False, ""),
            ("portal_maintenance_mode", False, ""),
            ("reviews_enabled", True, ""),
        ]
        changed = False
        for k, v, m in defaults:
            if not FeatureFlag.get(k):
                db.session.add(FeatureFlag(key=k, value_bool=v, message=m))
                changed = True
        if changed:
            db.session.commit()
