from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cliente: Mapped[str] = mapped_column(String(100))
    producto: Mapped[str] = mapped_column(String(150))
    cantidad: Mapped[int] = mapped_column(Integer)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    version: Mapped[int] = mapped_column(Integer, default=1)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    @property
    def total(self) -> Decimal:
        return self.precio_unitario * self.cantidad


class Solicitud(Base):
    # Se conserva aunque se elimine el pedido, para que un reintento
    # tardío no vuelva a crearlo.
    __tablename__ = "solicitudes"

    clave: Mapped[str] = mapped_column(String(36), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64))
    pedido_id: Mapped[int] = mapped_column(Integer)
