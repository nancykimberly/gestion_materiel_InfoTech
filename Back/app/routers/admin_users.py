from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_admin_user,
    get_db
)

from app.models import (
    Notification,
    User
)

from app.services.audit_service import enregistrer_audit
from app.services.notification_service import creer_notification


router = APIRouter(
    prefix="/api/admin/users",
    tags=["Administration - Utilisateurs"]
)


# ============================================================
# UTILISATEURS EN ATTENTE
# ============================================================

@router.get("/pending")
def get_pending_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Retourne la liste des utilisateurs
    dont le compte est encore en attente.
    """

    users = (
        db.query(User)
        .filter(User.statut == "en_attente")
        .order_by(User.date_creation.desc())
        .all()
    )

    return users


# ============================================================
# APPROUVER UN UTILISATEUR
# ============================================================

@router.patch("/{user_id}/approve")
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Approuve le compte d'un utilisateur.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    if user.statut == "approuve":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est déjà approuvé."
        )

    # Mise à jour du compte
    user.statut = "approuve"
    user.approuve_par_admin_id = current_admin.id
    user.date_traitement = datetime.utcnow()

    # ========================================================
    # NOTIFICATION
    # ========================================================

    notification = creer_notification(
        db=db,
        utilisateur_id=user.id,
        titre="Compte approuvé",
        message=(
            "Votre compte InfoTech a été approuvé. "
            "Vous pouvez maintenant vous connecter."
        )
    )

    # ========================================================
    # JOURNAL D'AUDIT
    # ========================================================

    enregistrer_audit(
        db=db,
        administrateur_id=current_admin.id,
        action="APPROBATION_UTILISATEUR",
        type_cible="utilisateur",
        cible_id=user.id,
        details=(
            f"Le compte de {user.email} "
            f"a été approuvé par l'administrateur."
        )
    )

    db.commit()
    db.refresh(user)

    return {
        "message": "Compte approuvé avec succès.",
        "user": user,
        "notification": notification
    }


# ============================================================
# REFUSER UN UTILISATEUR
# ============================================================

@router.patch("/{user_id}/reject")
def reject_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Refuse le compte d'un utilisateur.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    if user.statut == "refuse":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est déjà refusé."
        )

    user.statut = "refuse"
    user.approuve_par_admin_id = current_admin.id
    user.date_traitement = datetime.utcnow()

    # ========================================================
    # NOTIFICATION
    # ========================================================

    notification = creer_notification(
        db=db,
        utilisateur_id=user.id,
        titre="Compte refusé",
        message=(
            "Votre demande de création de compte "
            "InfoTech a été refusée."
        )
    )

    # ========================================================
    # AUDIT
    # ========================================================

    enregistrer_audit(
        db=db,
        administrateur_id=current_admin.id,
        action="REFUS_UTILISATEUR",
        type_cible="utilisateur",
        cible_id=user.id,
        details=(
            f"Le compte de {user.email} "
            f"a été refusé par l'administrateur."
        )
    )

    db.commit()
    db.refresh(user)

    return {
        "message": "Compte refusé.",
        "user": user,
        "notification": notification
    }