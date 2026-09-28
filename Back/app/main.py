from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.dependencies import (
    get_current_admin_user,
    get_current_user
)
from app.core.security import get_password_hash, verify_password
from app.database.session import SessionLocal
from app.schemas.user import UserProfileUpdate
from app.models import User
from app.routers.admin_users import router as admin_users_router
from app.routers.audit_logs import router as audit_logs_router
from app.routers.auth import router as auth_router
from app.routers.materiel import (
    admin_router as admin_materiels_router,
    router as materiels_router
)
from app.routers.notifications import router as notifications_router
from app.routers.requests import (
    admin_router as admin_requests_router,
    router as requests_router
)

app = FastAPI(
    title="InfoTech API",
    description="API du projet InfoTech",
    version="1.0.0"
)

# Inclusion des routeurs
app.include_router(auth_router)
app.include_router(admin_users_router)  
app.include_router(materiels_router)
app.include_router(admin_materiels_router)  
app.include_router(requests_router)
app.include_router(admin_requests_router)
app.include_router(notifications_router)
app.include_router(audit_logs_router)

# Configuration CORS sécurisée
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    # Autorise automatiquement tous les domaines de prévisualisation et production Vercel
    allow_origin_regex=r"https://.*\.vercel\.app",
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
        ,"doit_changer_mot_de_passe": current_user.doit_changer_mot_de_passe
        ,"avatar_url": current_user.avatar_url
    }


@app.get("/api/admin-test")
def admin_test(
    current_admin: User = Depends(get_current_admin_user)
):
    return {
        "message": "Bienvenue dans l'espace administrateur.",
        "administrateur": current_admin.nom_complet
    }


@app.put("/api/me")
def update_me(profile: UserProfileUpdate, current_user: User = Depends(get_current_user)):
    if profile.nouveau_mot_de_passe:
        if not profile.mot_de_passe_actuel or not verify_password(profile.mot_de_passe_actuel, current_user.mot_de_passe_hache):
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Le mot de passe actuel est incorrect.")
        current_user.mot_de_passe_hache = get_password_hash(profile.nouveau_mot_de_passe)
    current_user.nom_complet = profile.nom_complet.strip()
    current_user.departement = profile.departement.strip()
    current_user.poste = profile.poste.strip()
    current_user.avatar_url = profile.avatar_url
    db = SessionLocal()
    try:
        db.merge(current_user)
        db.commit()
        db.refresh(current_user)
    finally:
        db.close()
    return {"message": "Profil mis à jour."}
