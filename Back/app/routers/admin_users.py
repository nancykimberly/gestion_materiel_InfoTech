from datetime import datetime
import secrets

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
from app.schemas.user import UserAdminCreate, UserResponse, UserUpdate
from app.core.security import get_password_hash

from app.services.audit_service import enregistrer_audit
from app.services.notification_service import creer_notification


router = APIRouter(
    prefix="/api/admin/users",
    tags=["Administration - Utilisateurs"]
)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserAdminCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette adresse email est déjà utilisée.")
    if user_data.statut not in {"en_attente", "approuve", "refuse"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Statut invalide.")
    if len(user_data.mot_de_passe_temporaire) < 8:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Le mot de passe temporaire doit contenir au moins 8 caractères.")
    user = User(email=user_data.email, mot_de_passe_hache=get_password_hash(user_data.mot_de_passe_temporaire), nom_complet="À compléter", departement="À compléter", poste="À compléter", role="utilisateur", statut=user_data.statut, doit_changer_mot_de_passe=True, approuve_par_admin_id=current_admin.id)
    db.add(user)
    db.flush()
    creer_notification(db, user.id, "Votre compte InfoTech est créé", f"Votre compte a été créé. Connectez-vous avec votre mot de passe temporaire : {user_data.mot_de_passe_temporaire}. Vous devrez compléter votre profil et choisir un nouveau mot de passe.")
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    return db.query(User).order_by(User.date_creation.desc()).all()


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


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )

    updates = user_data.model_dump(exclude_none=True)
    if updates.get("role") not in {None, "utilisateur", "administrateur"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rôle invalide.")
    if updates.get("statut") not in {None, "en_attente", "approuve", "refuse"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Statut invalide.")
    if user.id == current_admin.id and updates.get("role") == "utilisateur":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vous ne pouvez pas retirer votre rôle administrateur.")

    for field, value in updates.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
    temporary_password = secrets.token_urlsafe(9)
    user.mot_de_passe_hache = get_password_hash(temporary_password)
    user.doit_changer_mot_de_passe = True
    user.statut = "approuve"
    creer_notification(db, user.id, "Mot de passe réinitialisé", f"Un administrateur a réinitialisé votre mot de passe. Mot de passe temporaire : {temporary_password}. Changez-le après connexion.")
    db.commit()
    return {"message": "Mot de passe temporaire envoyé à l'utilisateur."}


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
