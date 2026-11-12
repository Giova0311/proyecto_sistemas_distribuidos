from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.pedido import PedidoCrear


def datos_validos():
    return {
        "cliente": "  Cliente de prueba  ",
        "producto": "  Cuaderno  ",
        "cantidad": 3,
        "precio_unitario": "5000.50",
    }


def test_acepta_datos_validos_y_limpia_espacios():
    pedido = PedidoCrear(**datos_validos())

    assert pedido.cliente == "Cliente de prueba"
    assert pedido.producto == "Cuaderno"
    assert pedido.cantidad == 3
    assert isinstance(pedido.precio_unitario, Decimal)
    assert pedido.precio_unitario == Decimal("5000.50")


@pytest.mark.parametrize(
    "cantidad",
    [0, -1, 100001, 1.5],
    ids=["cero", "negativa", "supera_limite", "fraccionaria"],
)
def test_rechaza_cantidades_invalidas(cantidad):
    datos = {**datos_validos(), "cantidad": cantidad}

    with pytest.raises(ValidationError) as error:
        PedidoCrear(**datos)

    campos = [detalle["loc"] for detalle in error.value.errors()]
    assert ("cantidad",) in campos


@pytest.mark.parametrize(
    "precio",
    ["0", "-1", "1.234", "10000000000.00"],
    ids=["cero", "negativo", "tres_decimales", "supera_limite"],
)
def test_rechaza_precios_invalidos(precio):
    datos = {**datos_validos(), "precio_unitario": precio}

    with pytest.raises(ValidationError) as error:
        PedidoCrear(**datos)

    campos = [detalle["loc"] for detalle in error.value.errors()]
    assert ("precio_unitario",) in campos