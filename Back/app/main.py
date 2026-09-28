from fastapi import Depends, FastAPI

from app.core.dependencies import (
    get_current_user,
    get_current_admin_user
)
from app.models import User
from app.routers.auth import router as auth_router
from app.routers.admin_users import router as admin_users_router
from app.routers.materiel import (
    router as materiels_router,
    admin_router as admin_materiels_router
)
from app.routers.requests import (
    router as requests_router,
    admin_router as admin_requests_router
)

from app.routers.notifications import (
    router as notifications_router
)

from app.routers.audit_logs import (
    router as audit_logs_router
)
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="InfoTech API",
    description="API du projet InfoTech",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(auth_router)
app.include_router(admin_users_router)  
app.include_router(materiels_router)
app.include_router(admin_materiels_router)  
app.include_router(requests_router)
app.include_router(admin_requests_router)
app.include_router(notifications_router)
app.include_router(audit_logs_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {
        "message": "API InfoTech opérationnelle"
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/api/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nom_complet": current_user.nom_complet,
        "departement": current_user.departement,
        "poste": current_user.poste,
        "role": current_user.role,
        "statut": current_user.statut
    }


@app.get("/api/admin-test")
def admin_test(
    current_admin: User = Depends(get_current_admin_user)
):
    return {
        "message": "Bienvenue dans l'espace administrateur.",
        "administrateur": current_admin.nom_complet
    }