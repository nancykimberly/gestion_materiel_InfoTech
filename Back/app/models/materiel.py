from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Materiel(Base):
    __tablename__ = "materiels"

    __table_args__ = (
        CheckConstraint(
            "quantite_totale >= 0",
            name="ck_materiels_quantite_totale"
        ),
        CheckConstraint(
            "quantite_disponible >= 0",
            name="ck_materiels_quantite_disponible"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    nom: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    categorie: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    quantite_totale: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    quantite_disponible: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        default="disponible",
        nullable=False
    )

    cree_par_admin_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False
    )

    modifie_par_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=True
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    date_modification: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    admin_createur = relationship(
        "User",
        foreign_keys=[cree_par_admin_id],
        back_populates="materiels_crees"
    )

    admin_modificateur = relationship(
        "User",
        foreign_keys=[modifie_par_admin_id],
        back_populates="materiels_modifies"
    )

    demandes = relationship(
        "Request",
        back_populates="materiel"
    )