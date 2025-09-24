from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(nullable=False, unique=True)
    # created_at: Mapped[DateTime] = mapped_column(DateTime, default=DateTime.utcnow)

    def __repr__(self) -> str:
        return f"<Tag(name={self.name}, slug={self.slug})>"
