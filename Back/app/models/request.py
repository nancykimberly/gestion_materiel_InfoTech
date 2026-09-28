from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Request(Base):
    __tablename__ = "demandes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=False
    )

    materiel_id: Mapped[int] = mapped_column(
        ForeignKey("materiels.id"),
        nullable=False
    )

    quantite: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    motif: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    type_emprunt: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    date_debut: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    date_fin_prevue: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        default="en_attente",
        nullable=False
    )

    motif_refus: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    traite_par_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=True
    )

    date_traitement: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    retour_traite_par_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=True
    )

    date_retour_effective: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    utilisateur = relationship(
        "User",
        foreign_keys=[utilisateur_id],
        back_populates="demandes"
    )

    materiel = relationship(
        "Materiel",
        back_populates="demandes"
    )

    admin_traitement = relationship(
        "User",
        foreign_keys=[traite_par_admin_id],
        back_populates="demandes_traitees"
    )

    admin_retour = relationship(
        "User",
        foreign_keys=[retour_traite_par_admin_id],
        back_populates="retours_traites"
    )