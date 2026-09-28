import logging
import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Notification, User


logger = logging.getLogger(__name__)


def envoyer_email(destinataire: str, titre: str, message: str) -> None:
    if not settings.EMAIL_ENABLED:
        return

    email = EmailMessage()
    email["Subject"] = titre
    email["From"] = settings.SMTP_FROM
    email["To"] = destinataire
    email.set_content(message)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
        if settings.SMTP_USE_TLS:
            smtp.starttls()
        if settings.SMTP_USERNAME:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(email)


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

    utilisateur = db.query(User).filter(User.id == utilisateur_id).first()
    if utilisateur:
        try:
            envoyer_email(utilisateur.email, titre, message)
        except (OSError, smtplib.SMTPException) as error:
            logger.warning("Envoi e-mail impossible pour %s: %s", utilisateur.email, error)

    return notification
