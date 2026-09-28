from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    mot_de_passe_hache: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    nom_complet: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    departement: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    poste: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="utilisateur",
        nullable=False
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        default="en_attente",
        nullable=False
    )

    approuve_par_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("utilisateurs.id"),
        nullable=True
    )

    date_traitement: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Administrateur ayant traité ce compte
    admin_approbateur = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[approuve_par_admin_id]
    )

    # Comptes traités par cet administrateur
    comptes_traites = relationship(
        "User",
        foreign_keys=[approuve_par_admin_id],
        back_populates="admin_approbateur"
    )

    demandes = relationship(
        "Request",
        foreign_keys="Request.utilisateur_id",
        back_populates="utilisateur"
    )

    demandes_traitees = relationship(
        "Request",
        foreign_keys="Request.traite_par_admin_id",
        back_populates="admin_traitement"
    )

    retours_traites = relationship(
        "Request",
        foreign_keys="Request.retour_traite_par_admin_id",
        back_populates="admin_retour"
    )

    materiels_crees = relationship(
        "Materiel",
        foreign_keys="Materiel.cree_par_admin_id",
        back_populates="admin_createur"
    )

    materiels_modifies = relationship(
        "Materiel",
        foreign_keys="Materiel.modifie_par_admin_id",
        back_populates="admin_modificateur"
    )

    notifications = relationship(
        "Notification",
        back_populates="utilisateur"
    )

    journaux_audit = relationship(
        "AuditLog",
        back_populates="administrateur"
    )

    doit_changer_mot_de_passe: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
