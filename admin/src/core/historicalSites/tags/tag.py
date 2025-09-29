from src.core.database import db
from src.core.historicalSites.tags.tags_sites import site_tags
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(70), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    # color = db.Column(db.String(7), nullable=True, default="#FFFFFF")  
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<Tag(nombre={self.name}, slug={self.slug})>"


