from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    description_short: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    province: Mapped[str] = mapped_column(nullable=True)
    location: Mapped[str] = mapped_column(nullable=True)  # Could be coordinates
    conservation_status: Mapped[str] = mapped_column(nullable=True)
    year_declared: Mapped[int] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(nullable=True)
    registration_date: Mapped[date] = mapped_column(nullable=True)
    visibility: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"<Site(id={self.id}, name={self.name}, city={self.city}, province={self.province})>"
