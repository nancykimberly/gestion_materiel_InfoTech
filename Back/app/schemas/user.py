from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    mot_de_passe: str
    nom_complet: str
    departement: str
    poste: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nom_complet: str
    departement: str
    poste: str
    role: str
    statut: str
    date_creation: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class UserUpdate(BaseModel):
    nom_complet: str | None = None
    departement: str | None = None
    poste: str | None = None
    role: str | None = None
    statut: str | None = None


class UserAdminCreate(BaseModel):
    email: EmailStr
    mot_de_passe_temporaire: str
    statut: str = "approuve"


class UserActivation(BaseModel):
    nom_complet: str
    departement: str
    poste: str
    nouveau_mot_de_passe: str


class UserProfileUpdate(BaseModel):
    nom_complet: str
    departement: str
    poste: str
    avatar_url: str | None = None
    mot_de_passe_actuel: str | None = None
    nouveau_mot_de_passe: str | None = None


class PasswordForgotRequest(BaseModel):
    email: EmailStr
