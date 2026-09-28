from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AuditLog(Base):
    __tablename__ = "journaux_audit"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    administrateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    type_cible: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    cible_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    administrateur = relationship(
        "User",
        back_populates="journaux_audit"
    )