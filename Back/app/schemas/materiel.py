from pydantic import BaseModel, ConfigDict, Field


class MaterielCreate(BaseModel):
    nom: str
    categorie: str
    description: str | None = None
    image_url: str | None = None

    quantite_totale: int = Field(
        ge=0
    )

    quantite_disponible: int = Field(
        ge=0
    )

    statut: str = "disponible"


class MaterielUpdate(BaseModel):
    nom: str | None = None
    categorie: str | None = None
    description: str | None = None
    image_url: str | None = None

    quantite_totale: int | None = Field(
        default=None,
        ge=0
    )

    quantite_disponible: int | None = Field(
        default=None,
        ge=0
    )

    statut: str | None = None


class MaterielResponse(BaseModel):
    id: int
    nom: str
    categorie: str
    description: str | None
    image_url: str | None

    quantite_totale: int
    quantite_disponible: int

    statut: str

    model_config = ConfigDict(
        from_attributes=True
    )
