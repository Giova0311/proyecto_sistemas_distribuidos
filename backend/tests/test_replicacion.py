import os
import time
from uuid import uuid4

import httpx
import pymysql


def esperar(replica, pedido_id, condicion):
    limite = time.monotonic() + 20

    while time.monotonic() < limite:
        with replica.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM pedidos WHERE id=%s",
                (pedido_id,),
            )
            fila = cursor.fetchone()
        if condicion(fila):
            return
        time.sleep(0.5)

    raise AssertionError("El cambio no llegó a la réplica en 20 segundos.")


def test_replicar_creacion_actualizacion_eliminacion():
    base = os.getenv("API_URL", "http://nginx/api")
    pedido = None

    with pymysql.connect(
        host="mysql-replica",
        user="lector",
        password=os.environ["REPLICA_READER_PASSWORD"],
        database="pedidos",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    ) as replica, httpx.Client(base_url=base + "/", timeout=25) as client:

        datos = {
            "cliente": "Prueba réplica",
            "producto": "Artículo replicado",
            "cantidad": 1,
            "precio_unitario": "123.45",
        }

        try:
            response = client.post(
                "pedidos",
                json=datos,
                headers={"Idempotency-Key": str(uuid4())},
            )
            assert response.status_code == 201, response.text
            pedido = response.json()

            esperar(
                replica,
                pedido["id"],
                lambda fila: fila is not None and fila["version"] == 1,
            )

            response = client.put(
                f"pedidos/{pedido['id']}",
                json={
                    **datos,
                    "estado": "en_proceso",
                    "version": 1,
                },
            )
            assert response.status_code == 200, response.text
            pedido = response.json()

            esperar(
                replica,
                pedido["id"],
                lambda fila: (
                    fila is not None
                    and fila["estado"] == "en_proceso"
                    and fila["version"] == 2
                ),
            )

            response = client.delete(
                f"pedidos/{pedido['id']}",
                params={"version": 2},
            )
            assert response.status_code == 204

            esperar(replica, pedido["id"], lambda fila: fila is None)
            pedido = None

        finally:
            if pedido:
                response = client.get(f"pedidos/{pedido['id']}")
                if response.status_code == 200:
                    client.delete(
                        f"pedidos/{pedido['id']}",
                        params={"version": response.json()["version"]},
                    )
