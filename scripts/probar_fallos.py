# Ejecutar desde la carpeta raíz del proyecto.
# Detiene temporalmente un backend por vez y lo arranca en finally.
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://localhost:8080/api"


def docker(*args):
    subprocess.run(
        ["docker", "compose", *args],
        cwd=ROOT,
        check=True,
    )


def request(path, method="GET", body=None, key=None):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Idempotency-Key"] = key

    data = None if body is None else json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers=headers,
        method=method,
    )

    with urllib.request.urlopen(req, timeout=25) as response:
        raw = response.read()
        return (
            json.loads(raw) if raw else None,
            response.headers.get("X-Node-ID"),
        )


def nodos_disponibles():
    return {request("/health/ready")[1] for _ in range(12)}


def esperar_recuperacion():
    limite = time.monotonic() + 60
    while time.monotonic() < limite:
        try:
            if nodos_disponibles() == {"backend-1", "backend-2"}:
                return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(2)
    raise RuntimeError("No se recuperaron ambos nodos en 60 segundos.")


def prueba(caido, superviviente):
    pedido = None
    print(f"\nDeteniendo {caido}...")

    try:
        docker("stop", caido)

        nodos = nodos_disponibles()
        assert nodos == {superviviente}, nodos

        pedido, nodo = request(
            "/pedidos",
            method="POST",
            key=str(uuid4()),
            body={
                "cliente": "Demostración de fallo",
                "producto": f"Atendido por {superviviente}",
                "cantidad": 1,
                "precio_unitario": "25000.00",
            },
        )
        assert nodo == superviviente
        recibido, _ = request(f"/pedidos/{pedido['id']}")
        assert recibido["id"] == pedido["id"]

        print(
            f"OK: {superviviente} creó y consultó "
            f"el pedido #{pedido['id']}."
        )

    finally:
        docker("start", caido)
        esperar_recuperacion()

        if pedido:
            actual, _ = request(f"/pedidos/{pedido['id']}")
            request(
                f"/pedidos/{pedido['id']}?version={actual['version']}",
                method="DELETE",
            )

    print(f"OK: {caido} se reincorporó al balanceo.")


if __name__ == "__main__":
    esperar_recuperacion()
    prueba("backend-1", "backend-2")
    prueba("backend-2", "backend-1")
    print("\nPruebas de caída y recuperación completadas.")
