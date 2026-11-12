import hashlib
import json

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError

from app.models.pedido import Pedido, Solicitud


ESTADOS = ["pendiente", "en_proceso", "enviado", "entregado"]


def obtener(db, pedido_id, bloquear=False):
    consulta = select(Pedido).where(Pedido.id == pedido_id)
    if bloquear:
        consulta = consulta.with_for_update()

    pedido = db.scalar(consulta)
    if pedido is None:
        raise HTTPException(404, "Pedido no encontrado.")
    return pedido


def listar(db, pagina, limite, estado=None, buscar=""):
    filtros = []

    if estado:
        filtros.append(Pedido.estado == estado.value)

    if buscar:
        filtros.append(
            or_(
                Pedido.cliente.contains(buscar, autoescape=True),
                Pedido.producto.contains(buscar, autoescape=True),
            )
        )

    total = db.scalar(
        select(func.count()).select_from(Pedido).where(*filtros)
    )

    items = db.scalars(
        select(Pedido)
        .where(*filtros)
        .order_by(Pedido.id.desc())
        .offset((pagina - 1) * limite)
        .limit(limite)
    ).all()

    return {
        "items": items,
        "total": total,
        "pagina": pagina,
        "limite": limite,
    }


def resolver_reintento(db, solicitud, huella):
    if solicitud.huella != huella:
        raise HTTPException(
            409,
            "Esta clave de solicitud ya se utilizó con otros datos.",
        )

    pedido = db.get(Pedido, solicitud.pedido_id)
    if pedido is None:
        raise HTTPException(
            409,
            "La solicitud ya fue procesada y su pedido fue eliminado.",
        )
    return pedido


def crear(db, datos, clave):
    contenido = json.dumps(
        datos.model_dump(mode="json"),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    huella = hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    anterior = db.get(Solicitud, clave)
    if anterior:
        return resolver_reintento(db, anterior, huella), False

    pedido = Pedido(**datos.model_dump())
    db.add(pedido)

    try:
        db.flush()
        db.add(
            Solicitud(
                clave=clave,
                huella=huella,
                pedido_id=pedido.id,
            )
        )
        db.commit()
    except IntegrityError:
        # Otro nodo pudo procesar simultáneamente la misma clave.
        # El rollback también deshace el pedido de esta transacción.
        db.rollback()
        anterior = db.get(Solicitud, clave)
        if anterior is None:
            raise
        return resolver_reintento(db, anterior, huella), False

    return pedido, True


def actualizar(db, pedido_id, datos):
    pedido = obtener(db, pedido_id, bloquear=True)

    if pedido.version != datos.version:
        raise HTTPException(
            409,
            "El pedido cambió en otra sesión. Recarga antes de editar.",
        )

    actual = ESTADOS.index(pedido.estado)
    nuevo = ESTADOS.index(datos.estado.value)

    if nuevo not in (actual, actual + 1):
        raise HTTPException(
            409,
            "El estado solo puede mantenerse o avanzar un paso.",
        )

    for campo, valor in datos.model_dump(
        exclude={"version", "estado"}
    ).items():
        setattr(pedido, campo, valor)

    pedido.estado = datos.estado.value
    pedido.version += 1
    db.commit()
    db.refresh(pedido)
    return pedido


def eliminar(db, pedido_id, version):
    pedido = obtener(db, pedido_id, bloquear=True)

    if pedido.version != version:
        raise HTTPException(
            409,
            "El pedido cambió. Recarga antes de eliminarlo.",
        )

    db.delete(pedido)
    db.commit()
