from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Estado(str, Enum):
    pendiente = "pendiente"
    en_proceso = "en_proceso"
    enviado = "enviado"
    entregado = "entregado"


class DatosPedido(BaseModel):
    cliente: str = Field(min_length=2, max_length=100)
    producto: str = Field(min_length=2, max_length=150)
    cantidad: int = Field(ge=1, le=100000)
    precio_unitario: Decimal = Field(
        gt=0, max_digits=12, decimal_places=2
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )


class PedidoCrear(DatosPedido):
    pass


class PedidoActualizar(DatosPedido):
    estado: Estado
    version: int = Field(ge=1)


class PedidoSalida(DatosPedido):
    id: int
    estado: Estado
    version: int
    total: Decimal
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginaPedidos(BaseModel):
    items: list[PedidoSalida]
    total: int
    pagina: int
    limite: int
