from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    utilisateur_id: int
    titre: str
    message: str
    est_lu: bool
    date_creation: datetime

    model_config = ConfigDict(
        from_attributes=True
    )