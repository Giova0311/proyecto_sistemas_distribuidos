import os
from uuid import uuid4

import httpx
import pytest

BASE = os.getenv("API_URL", "http://nginx/api")


@pytest.fixture
def cliente():
    with httpx.Client(base_url=BASE + "/", timeout=25) as client:
        yield client


def datos():
    return {
        "cliente": "Cliente prueba",
        "producto": "Producto prueba",
        "cantidad": 2,
        "precio_unitario": "15000.50",
    }


def test_crud_idempotencia_y_version(cliente):
    clave = str(uuid4())
    cabeceras = {"Idempotency-Key": clave}
    pedido = None

    try:
        creado = cliente.post("pedidos", json=datos(), headers=cabeceras)
        assert creado.status_code == 201, creado.text
        pedido = creado.json()
        assert pedido["total"] == "30001.00"

        repetido = cliente.post("pedidos", json=datos(), headers=cabeceras)
        assert repetido.status_code == 200
        assert repetido.json()["id"] == pedido["id"]

        distinto = cliente.post(
            "pedidos",
            json={**datos(), "cantidad": 3},
            headers=cabeceras,
        )
        assert distinto.status_code == 409

        consulta = cliente.get(f"pedidos/{pedido['id']}")
        assert consulta.status_code == 200

        cambios = {
            **datos(),
            "estado": "en_proceso",
            "version": pedido["version"],
        }
        editado = cliente.put(f"pedidos/{pedido['id']}", json=cambios)
        assert editado.status_code == 200, editado.text
        pedido = editado.json()
        assert pedido["version"] == 2

        obsoleto = cliente.put(f"pedidos/{pedido['id']}", json=cambios)
        assert obsoleto.status_code == 409

        salto = cliente.put(
            f"pedidos/{pedido['id']}",
            json={
                **datos(),
                "estado": "entregado",
                "version": pedido["version"],
            },
        )
        assert salto.status_code == 409

        eliminado = cliente.delete(
            f"pedidos/{pedido['id']}",
            params={"version": pedido["version"]},
        )
        assert eliminado.status_code == 204
        assert cliente.get(f"pedidos/{pedido['id']}").status_code == 404

        tardio = cliente.post("pedidos", json=datos(), headers=cabeceras)
        assert tardio.status_code == 409
        pedido = None

    finally:
        if pedido:
            actual = cliente.get(f"pedidos/{pedido['id']}")
            if actual.status_code == 200:
                cliente.delete(
                    f"pedidos/{pedido['id']}",
                    params={"version": actual.json()["version"]},
                )


@pytest.mark.parametrize("cambio", [
    {"cantidad": 0},
    {"precio_unitario": "-1"},
    {"cliente": " "},
    {"precio_unitario": "1.234"},
])
def test_validacion(cliente, cambio):
    resultado = cliente.post(
        "pedidos",
        json={**datos(), **cambio},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert resultado.status_code == 422


def test_clave_obligatoria(cliente):
    assert cliente.post("pedidos", json=datos()).status_code == 422


def test_balanceo(cliente):
    nodos = {
        cliente.get("health/ready").headers.get("X-Node-ID")
        for _ in range(12)
    }
    assert nodos == {"backend-1", "backend-2"}
