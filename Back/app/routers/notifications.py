from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models import Notification, User
from app.schemas.notification import NotificationResponse


router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)


@router.get(
    "",
    response_model=list[NotificationResponse]
)
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retourne les notifications de l'utilisateur connecté.
    """

    notifications = (
        db.query(Notification)
        .filter(
            Notification.utilisateur_id == current_user.id
        )
        .order_by(Notification.date_creation.desc())
        .all()
    )

    return notifications


@router.get(
    "/unread-count"
)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retourne le nombre de notifications non lues.
    """

    count = (
        db.query(Notification)
        .filter(
            Notification.utilisateur_id == current_user.id,
            Notification.est_lu == False
        )
        .count()
    )

    return {
        "count": count
    }


@router.patch(
    "/{notification_id}/read"
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marque une notification comme lue.
    """

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.utilisateur_id == current_user.id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification introuvable."
        )

    notification.est_lu = True

    db.commit()

    return {
        "message": "Notification marquée comme lue."
    }