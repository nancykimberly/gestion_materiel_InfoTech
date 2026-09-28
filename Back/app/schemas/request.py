from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RequestCreate(BaseModel):
    materiel_id: int
    quantite: int = Field(
        default=1,
        ge=1
    )
    motif: str
    type_emprunt: str
    date_debut: date | None = None
    date_fin_prevue: date | None = None


class RequestResponse(BaseModel):
    id: int
    utilisateur_id: int
    materiel_id: int
    quantite: int
    motif: str
    type_emprunt: str
    date_debut: date | None
    date_fin_prevue: date | None
    statut: str
    motif_refus: str | None
    traite_par_admin_id: int | None
    date_traitement: datetime | None
    retour_traite_par_admin_id: int | None
    date_retour_effective: datetime | None
    date_creation: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class RequestReject(BaseModel):
    motif_refus: str


class RequestStatusResponse(BaseModel):
    message: str
    demande: RequestResponse