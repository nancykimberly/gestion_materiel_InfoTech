from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_admin_user,
    get_db
)
from app.models import AuditLog, User
from app.schemas.audit_log import AuditLogResponse


router = APIRouter(
    prefix="/api/admin/audit-logs",
    tags=["Administration - Audit"]
)


@router.get(
    "",
    response_model=list[AuditLogResponse]
)
def get_audit_logs(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Retourne les journaux d'audit.
    """

    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.date_creation.desc())
        .all()
    )

    return logs