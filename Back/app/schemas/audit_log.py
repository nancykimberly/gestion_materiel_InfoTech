from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    administrateur_id: int
    action: str
    type_cible: str
    cible_id: int
    details: str | None
    date_creation: datetime

    model_config = ConfigDict(
        from_attributes=True
    )