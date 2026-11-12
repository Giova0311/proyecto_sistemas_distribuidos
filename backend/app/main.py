import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api import health, pedidos
from app.core.config import settings

app = FastAPI(
    title="Sistema distribuido de pedidos",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

app.include_router(pedidos.router, prefix="/api")
app.include_router(health.router, prefix="/api")


@app.middleware("http")
async def identificar_nodo(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Node-ID"] = settings.node_id
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(SQLAlchemyError)
async def error_base_datos(request: Request, exc: SQLAlchemyError):
    logging.exception("Error de persistencia", exc_info=exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "Base de datos no disponible. "
                "Reintenta conservando la clave de la solicitud."
            )
        },
    )
