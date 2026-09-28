from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.core.dependencies import get_current_user, get_db
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import PasswordForgotRequest, UserActivation, UserCreate, UserResponse
from app.services.notification_service import creer_notification
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentification"]
)



@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau compte utilisateur.
    """

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette adresse email est déjà utilisée."
        )

    hashed_password = get_password_hash(
        user_data.mot_de_passe
    )

    new_user = User(
        email=user_data.email,
        mot_de_passe_hache=hashed_password,
        nom_complet=user_data.nom_complet,
        departement=user_data.departement,
        poste=user_data.poste,
        role="utilisateur",
        statut="en_attente",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.patch("/activate", response_model=UserResponse)
def activate_account(
    activation_data: UserActivation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.doit_changer_mot_de_passe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce compte est déjà activé.")
    if len(activation_data.nouveau_mot_de_passe) < 8:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Le mot de passe doit contenir au moins 8 caractères.")
    current_user.nom_complet = activation_data.nom_complet.strip()
    current_user.departement = activation_data.departement.strip()
    current_user.poste = activation_data.poste.strip()
    current_user.mot_de_passe_hache = get_password_hash(activation_data.nouveau_mot_de_passe)
    current_user.doit_changer_mot_de_passe = False
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/forgot-password")
def forgot_password(payload: PasswordForgotRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        admins = db.query(User).filter(User.role == "administrateur", User.statut == "approuve").all()
        for admin in admins:
            creer_notification(db, admin.id, "Réinitialisation demandée", f"{user.nom_complet} ({user.email}) demande une réinitialisation de mot de passe.")
        db.commit()
    return {"message": "Si ce compte existe, les administrateurs ont été informés."}


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authentifie un utilisateur et retourne un JWT.
    """

    user = (
        db.query(User)
        .filter(User.email == login_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect."
        )

    password_valid = verify_password(
        login_data.mot_de_passe,
        user.mot_de_passe_hache
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect."
        )

    if user.statut != "approuve":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre compte n'est pas encore approuvé."
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "email": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
