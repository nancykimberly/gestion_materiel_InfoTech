from sqlalchemy.orm import Session

from app.models import AuditLog


def enregistrer_audit(
    db: Session,
    administrateur_id: int,
    action: str,
    type_cible: str,
    cible_id: int,
    details: str | None = None
):
    """
    Enregistre une action effectuée par un administrateur
    dans le journal d'audit.
    """

    journal = AuditLog(
        administrateur_id=administrateur_id,
        action=action,
        type_cible=type_cible,
        cible_id=cible_id,
        details=details
    )

    db.add(journal)

    return journal
