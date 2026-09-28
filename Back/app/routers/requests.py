from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_admin_user,
    get_current_user,
    get_db
)

from app.models import (
    Materiel,
    Notification,
    Request,
    User
)

from app.schemas.request import (
    RequestCreate,
    RequestReject,
    RequestResponse,
    RequestStatusResponse
)

from app.services.audit_service import enregistrer_audit
from app.services.notification_service import creer_notification


# ============================================================
# ROUTES UTILISATEUR
# ============================================================

router = APIRouter(
    prefix="/api/requests",
    tags=["Demandes"]
)


@router.post(
    "",
    response_model=RequestResponse,
    status_code=status.HTTP_201_CREATED
)
def create_request(
    request_data: RequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crée une nouvelle demande d'emprunt.
    """

    materiel = (
        db.query(Materiel)
        .filter(Materiel.id == request_data.materiel_id)
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
            detail="Ce matériel est retiré du catalogue."
        )

    if materiel.statut == "maintenance":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce matériel est actuellement en maintenance."
        )

    if request_data.type_emprunt not in [
        "temporaire",
        "definitif"
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type d'emprunt invalide."
        )

    if (
        request_data.date_debut
        and request_data.date_fin_prevue
        and request_data.date_fin_prevue < request_data.date_debut
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de fin ne peut pas être antérieure à la date de début."
        )

    if request_data.quantite <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La quantité doit être supérieure à zéro."
        )

    if request_data.quantite > materiel.quantite_disponible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La quantité demandée dépasse la quantité disponible."
        )

    new_request = Request(
        utilisateur_id=current_user.id,
        materiel_id=request_data.materiel_id,
        quantite=request_data.quantite,
        motif=request_data.motif,
        type_emprunt=request_data.type_emprunt,
        date_debut=request_data.date_debut,
        date_fin_prevue=request_data.date_fin_prevue,
        statut="en_attente"
    )

    db.add(new_request)

    db.commit()
    db.refresh(new_request)

    return new_request


# ============================================================
# MES DEMANDES
# ============================================================

@router.get(
    "/my",
    response_model=list[RequestResponse]
)
def get_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retourne les demandes de l'utilisateur connecté.
    """

    requests = (
        db.query(Request)
        .filter(Request.utilisateur_id == current_user.id)
        .order_by(Request.date_creation.desc())
        .all()
    )

    return requests


# ============================================================
# ROUTES ADMINISTRATEUR
# ============================================================

admin_router = APIRouter(
    prefix="/api/admin/requests",
    tags=["Administration - Demandes"]
)


# ============================================================
# DEMANDES EN ATTENTE
# ============================================================

@admin_router.get(
    "/pending",
    response_model=list[RequestResponse]
)
def get_pending_requests(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Retourne toutes les demandes en attente.
    """

    requests = (
        db.query(Request)
        .filter(Request.statut == "en_attente")
        .order_by(Request.date_creation.asc())
        .all()
    )

    return requests


# ============================================================
# APPROUVER UNE DEMANDE
# ============================================================

@admin_router.patch(
    "/{request_id}/approve",
    response_model=RequestStatusResponse
)
def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Approuve une demande et diminue le stock.
    """

    request = (
        db.query(Request)
        .filter(Request.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande introuvable."
        )

    if request.statut != "en_attente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seules les demandes en attente peuvent être approuvées."
        )

    materiel = (
        db.query(Materiel)
        .filter(Materiel.id == request.materiel_id)
        .first()
    )

    if not materiel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matériel associé introuvable."
        )

    if request.quantite > materiel.quantite_disponible:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock insuffisant pour approuver cette demande."
        )

    # Diminution du stock
    materiel.quantite_disponible -= request.quantite

    # Modification de la demande
    request.statut = "approuve"
    request.traite_par_admin_id = current_admin.id
    request.date_traitement = datetime.utcnow()

    # ========================================================
    # NOTIFICATION UTILISATEUR
    # ========================================================

    notification = creer_notification(
        db=db,
        utilisateur_id=request.utilisateur_id,
        titre="Demande approuvée",
        message=(
            f"Votre demande pour le matériel "
            f"« {materiel.nom} » a été approuvée."
        )
    )

    # ========================================================
    # JOURNAL D'AUDIT
    # ========================================================

    enregistrer_audit(
        db=db,
        administrateur_id=current_admin.id,
        action="APPROBATION_DEMANDE",
        type_cible="demande",
        cible_id=request.id,
        details=(
            f"Demande approuvée. "
            f"Matériel : {materiel.nom}. "
            f"Quantité : {request.quantite}."
        )
    )

    db.commit()
    db.refresh(request)

    return {
        "message": "Demande approuvée avec succès.",
        "demande": request
    }


# ============================================================
# REFUSER UNE DEMANDE
# ============================================================

@admin_router.patch(
    "/{request_id}/reject",
    response_model=RequestStatusResponse
)
def reject_request(
    request_id: int,
    request_data: RequestReject,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Refuse une demande.
    """

    request = (
        db.query(Request)
        .filter(Request.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande introuvable."
        )

    if request.statut != "en_attente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seules les demandes en attente peuvent être refusées."
        )

    if not request_data.motif_refus.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le motif du refus est obligatoire."
        )

    request.statut = "refuse"
    request.motif_refus = request_data.motif_refus
    request.traite_par_admin_id = current_admin.id
    request.date_traitement = datetime.utcnow()

    materiel = (
        db.query(Materiel)
        .filter(Materiel.id == request.materiel_id)
        .first()
    )

    nom_materiel = materiel.nom if materiel else "Matériel inconnu"

    # ========================================================
    # NOTIFICATION
    # ========================================================

    creer_notification(
        db=db,
        utilisateur_id=request.utilisateur_id,
        titre="Demande refusée",
        message=(
            f"Votre demande pour le matériel "
            f"« {nom_materiel} » a été refusée. "
            f"Motif : {request_data.motif_refus}"
        )
    )

    # ========================================================
    # AUDIT
    # ========================================================

    enregistrer_audit(
        db=db,
        administrateur_id=current_admin.id,
        action="REFUS_DEMANDE",
        type_cible="demande",
        cible_id=request.id,
        details=(
            f"Demande refusée. "
            f"Motif : {request_data.motif_refus}"
        )
    )

    db.commit()
    db.refresh(request)

    return {
        "message": "Demande refusée.",
        "demande": request
    }


# ============================================================
# RESTITUTION
# ============================================================

@admin_router.patch(
    "/{request_id}/return",
    response_model=RequestStatusResponse
)
def return_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Enregistre la restitution d'un matériel.
    """

    request = (
        db.query(Request)
        .filter(Request.id == request_id)
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demande introuvable."
        )

    if request.statut != "approuve":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seules les demandes approuvées peuvent être restituées."
        )

    materiel = (
        db.query(Materiel)
        .filter(Materiel.id == request.materiel_id)
        .first()
    )

    if not materiel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matériel associé introuvable."
        )

    # Restitution
    materiel.quantite_disponible += request.quantite

    if materiel.quantite_disponible > materiel.quantite_totale:
        materiel.quantite_disponible = materiel.quantite_totale

    request.statut = "restitue"
    request.retour_traite_par_admin_id = current_admin.id
    request.date_retour_effective = datetime.utcnow()

    # ========================================================
    # NOTIFICATION
    # ========================================================

    creer_notification(
        db=db,
        utilisateur_id=request.utilisateur_id,
        titre="Matériel restitué",
        message=(
            f"La restitution de « {materiel.nom} » "
            f"a été enregistrée avec succès."
        )
    )

    # ========================================================
    # AUDIT
    # ========================================================

    enregistrer_audit(
        db=db,
        administrateur_id=current_admin.id,
        action="RESTITUTION_MATERIEL",
        type_cible="demande",
        cible_id=request.id,
        details=(
            f"Restitution enregistrée. "
            f"Matériel : {materiel.nom}. "
            f"Quantité : {request.quantite}."
        )
    )

    db.commit()
    db.refresh(request)

    return {
        "message": "Restitution enregistrée avec succès.",
        "demande": request
    }