from pydantic import BaseModel, EmailStr, ConfigDict


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

    model_config = ConfigDict(
        from_attributes=True
    )