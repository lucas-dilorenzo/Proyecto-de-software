from datetime import datetime, timezone
from src.core.database import db
from src.core.users.user import User


class FeatureFlag(db.Model):
    __tablename__ = "feature_flags"

    key = db.Column(db.String(64), primary_key=True)
    value_bool = db.Column(db.Boolean, nullable=False, default=False)
    message = db.Column(db.String(200), nullable=False, default="")
    updated_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    @property
    def updated_by(self):
        if not hasattr(self, "_updated_by"):
            self._updated_by = (
                User.query.get(self.updated_by_user_id)
                if self.updated_by_user_id
                else None
            )
        return self._updated_by

    def set(self, *, value_bool: bool, message: str, user_id: int | None):
        """Actualiza los valores del flag y guarda en la base de datos"""
        self.value_bool = value_bool
        self.message = message or ""
        self.updated_by_user_id = user_id
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return self

    @classmethod
    def get(cls, key: str):
        """Obtiene un flag por su clave"""
        return cls.query.get(key)

    @classmethod
    def get_all_with_users(cls):
        """Obtiene todos los flags con información de usuarios"""
        flags = (
            db.session.query(cls, User)
            .outerjoin(User, cls.updated_by_user_id == User.id)
            .all()
        )

        # Asignar usuario relacionado al flag
        result = []
        for flag, user in flags:
            flag._updated_by = user
            result.append(flag)

        return result

    @classmethod
    def update(cls, key, value_bool, message, user_id):
        """Actualiza un flag validando datos"""
        flag = cls.get(key)
        if not flag:
            return False, "Flag inválido"

        # Validaciones
        is_maintenance = key in ("admin_maintenance_mode", "portal_maintenance_mode")
        if is_maintenance and value_bool and not message:
            return (
                False,
                "El mensaje de mantenimiento es obligatorio cuando el modo está ON.",
            )

        if len(message) > 200:
            return False, "El mensaje no puede superar 200 caracteres."

        if key == "portal_maintenance_mode" and value_bool and len(message) < 10:
            return (
                False,
                "El mensaje de mantenimiento debe ser descriptivo (mínimo 10 caracteres).",
            )

        # Evitar activación simultánea de ambos modos mantenimiento
        if value_bool and key == "admin_maintenance_mode":
            portal_flag = cls.get("portal_maintenance_mode")
            if portal_flag and portal_flag.value_bool:
                return (
                    False,
                    "No se puede activar el mantenimiento de admin mientras el portal está en mantenimiento.",
                )

        # Actualizar el flag
        flag.value_bool = value_bool
        flag.message = message
        flag.updated_by_user_id = user_id
        flag.updated_at = datetime.now(timezone.utc)
        db.session.commit()

        return True, "Flag actualizado"

    @classmethod
    def ensure_defaults(cls):
        """Asegura que existan los flags predeterminados"""
        defaults = [
            ("admin_maintenance_mode", False, ""),
            ("portal_maintenance_mode", False, ""),
            ("reviews_enabled", True, ""),
        ]
        changed = False
        for k, v, m in defaults:
            if not cls.get(k):
                db.session.add(cls(key=k, value_bool=v, message=m))
                changed = True
        if changed:
            db.session.commit()
