from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.pedido import (
    Estado,
    PaginaPedidos,
    PedidoActualizar,
    PedidoCrear,
    PedidoSalida,
)
from app.services import pedidos_service as servicio

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])
DB = Annotated[Session, Depends(get_db)]


@router.get("", response_model=PaginaPedidos)
def listar(
    db: DB,
    pagina: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=100),
    estado: Estado | None = None,
    buscar: str = Query("", max_length=100),
):
    return servicio.listar(db, pagina, limite, estado, buscar)


@router.get("/{pedido_id}", response_model=PedidoSalida)
def obtener(pedido_id: int, db: DB):
    return servicio.obtener(db, pedido_id)


@router.post("", response_model=PedidoSalida, status_code=201)
def crear(
    datos: PedidoCrear,
    response: Response,
    db: DB,
    idempotency_key: Annotated[UUID, Header()],
):
    pedido, nuevo = servicio.crear(db, datos, str(idempotency_key))
    response.status_code = 201 if nuevo else 200
    return pedido


@router.put("/{pedido_id}", response_model=PedidoSalida)
def actualizar(pedido_id: int, datos: PedidoActualizar, db: DB):
    return servicio.actualizar(db, pedido_id, datos)


@router.delete("/{pedido_id}", status_code=204)
def eliminar(
    pedido_id: int,
    db: DB,
    version: int = Query(..., ge=1),
):
    servicio.eliminar(db, pedido_id, version)
    return Response(status_code=204)
