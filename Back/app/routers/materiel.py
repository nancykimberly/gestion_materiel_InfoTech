from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import Materiel, User
from app.core.dependencies import (
    get_current_admin_user,
    get_current_user,
    get_db
)
from app.schemas.materiel import (
    MaterielCreate,
    MaterielResponse,
    MaterielUpdate
)


# ============================================================
# ROUTES POUR LES UTILISATEURS
# ============================================================

router = APIRouter(
    prefix="/api/materiels",
    tags=["Matériels"]
)


@router.get(
    "",
    response_model=list[MaterielResponse]
)
def get_materiels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retourne la liste des matériels non retirés.
    """

    materiels = (
        db.query(Materiel)
        .filter(Materiel.statut != "retire")
        .order_by(Materiel.nom.asc())
        .all()
    )

    return materiels


@router.get(
    "/{materiel_id}",
    response_model=MaterielResponse
)
def get_materiel(
    materiel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retourne un matériel précis.
    """

    materiel = (
        db.query(Materiel)
        .filter(
            Materiel.id == materiel_id,
            Materiel.statut != "retire"
        )
        .first()
    )

    if not materiel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matériel introuvable."
        )

    return materiel


# ============================================================
# ROUTES ADMINISTRATEUR
# ============================================================

admin_router = APIRouter(
    prefix="/api/admin/materiels",
    tags=["Administration - Matériels"]
)


@admin_router.post(
    "",
    response_model=MaterielResponse,
    status_code=status.HTTP_201_CREATED
)
def create_materiel(
    materiel_data: MaterielCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Crée un nouveau matériel.
    """

    # Vérification de la cohérence des quantités
    if materiel_data.quantite_disponible > materiel_data.quantite_totale:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "La quantité disponible ne peut pas "
                "être supérieure à la quantité totale."
            )
        )

    # Vérification du statut
    statuts_valides = [
        "disponible",
        "maintenance",
        "retire"
    ]

    if materiel_data.statut not in statuts_valides:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Statut invalide. Utilisez : "
                "disponible, maintenance ou retire."
            )
        )

    new_materiel = Materiel(
        nom=materiel_data.nom,
        categorie=materiel_data.categorie,
        description=materiel_data.description,
        image_url=materiel_data.image_url,
        quantite_totale=materiel_data.quantite_totale,
        quantite_disponible=materiel_data.quantite_disponible,
        statut=materiel_data.statut,
        cree_par_admin_id=current_admin.id,
    )

    db.add(new_materiel)
    db.commit()
    db.refresh(new_materiel)

    return new_materiel


@admin_router.put(
    "/{materiel_id}",
    response_model=MaterielResponse
)
def update_materiel(
    materiel_id: int,
    materiel_data: MaterielUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Modifie un matériel existant.
    """

    materiel = (
        db.query(Materiel)
        .filter(Materiel.id == materiel_id)
        .first()
    )

    if not materiel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matériel introuvable."
        )

    # Mise à jour uniquement des champs fournis
    if materiel_data.nom is not None:
        materiel.nom = materiel_data.nom

    if materiel_data.categorie is not None:
        materiel.categorie = materiel_data.categorie

    if materiel_data.description is not None:
        materiel.description = materiel_data.description

    if materiel_data.image_url is not None:
        materiel.image_url = materiel_data.image_url

    if materiel_data.quantite_totale is not None:
        materiel.quantite_totale = materiel_data.quantite_totale

    if materiel_data.quantite_disponible is not None:
        materiel.quantite_disponible = materiel_data.quantite_disponible

    if materiel_data.statut is not None:
        statuts_valides = [
            "disponible",
            "maintenance",
            "retire"
        ]

        if materiel_data.statut not in statuts_valides:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Statut invalide. Utilisez : "
                    "disponible, maintenance ou retire."
                )
            )

        materiel.statut = materiel_data.statut

    # Vérification finale des quantités
    if materiel.quantite_disponible > materiel.quantite_totale:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "La quantité disponible ne peut pas "
                "être supérieure à la quantité totale."
            )
        )

    materiel.modifie_par_admin_id = current_admin.id
    materiel.date_modification = datetime.utcnow()

    db.commit()
    db.refresh(materiel)

    return materiel


@admin_router.delete(
    "/{materiel_id}"
)
def delete_materiel(
    materiel_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Retire un matériel du catalogue.

    On ne supprime pas réellement la ligne en base.
    On passe simplement son statut à 'retire'.
    """

    materiel = (
        db.query(Materiel)
        .filter(Materiel.id == materiel_id)
        .first()
    )

    if not materiel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matériel introuvable."
        )

    if materiel.statut == "retire":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce matériel est déjà retiré."
        )

    materiel.statut = "retire"
    materiel.modifie_par_admin_id = current_admin.id
    materiel.date_modification = datetime.utcnow()

    db.commit()

    return {
        "message": "Matériel retiré du catalogue avec succès."
    }
