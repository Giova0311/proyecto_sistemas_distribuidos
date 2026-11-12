from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine

router = APIRouter(tags=["Salud"])


@router.get("/health/live")
def live():
    return {"estado": "activo", "nodo": settings.node_id}


@router.get("/health/ready")
def ready():
    with engine.connect() as conexion:
        conexion.execute(text("SELECT 1"))
    return {
        "estado": "disponible",
        "nodo": settings.node_id,
        "base_datos": "conectada",
    }
