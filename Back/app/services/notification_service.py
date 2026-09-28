from sqlalchemy.orm import Session

from app.models import Notification


def creer_notification(
    db: Session,
    utilisateur_id: int,
    titre: str,
    message: str
):
    """
    Crée une notification pour un utilisateur.
    """

    notification = Notification(
        utilisateur_id=utilisateur_id,
        titre=titre,
        message=message,
        est_lu=False
    )

    db.add(notification)

    return notification