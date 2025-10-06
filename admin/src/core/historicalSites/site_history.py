from src.core.database import db
from datetime import datetime, timezone

class SiteHistory(db.Model):
    __tablename__ = "site_histories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    details = db.Column(db.Text, nullable=True)

    site = db.relationship("Site", backref="history_entries")
    user = db.relationship("User")  # Asumiendo que ya tenés modelo User

    def __repr__(self):
        return f"<SiteHistory site={self.site_id}, user={self.user_id}, action={self.action}>"
