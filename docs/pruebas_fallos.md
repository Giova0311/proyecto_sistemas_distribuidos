# Guía de demostración

Los resultados descritos son esperados. Registra los observados al
ejecutar el proyecto; este documento no certifica pruebas ejecutadas.

## 1. Funcionamiento normal

Crear un pedido desde la interfaz.
Actualizarlo siguiendo los cuatro estados.
Comprobar total, búsqueda y persistencia al recargar.

En PowerShell:

```powershell
1..8 | ForEach-Object {
  (Invoke-WebRequest http://localhost:8080/api/health/ready).Headers["X-Node-ID"]
}
```

Resultado esperado: aparecen backend-1 y backend-2.
No exigir una alternancia exacta: otras solicitudes también consumen
turnos del balanceador.

## 2. Caída de un backend

```powershell
docker compose stop backend-1
```

Crear y listar pedidos desde la interfaz.
Resultado esperado: el otro nodo atiende las nuevas solicitudes.

```powershell
docker compose start backend-1
```

Esperar unos segundos y repetir las consultas de salud.
Resultado esperado: ambos nodos vuelven a aparecer.

Repetir intercambiando backend-1 y backend-2.

Versión automatizada:

```powershell
python scripts/probar_fallos.py
```

El script restaura el nodo detenido con finally.

## 3. Revisar la réplica

Abrir el cliente de MySQL en la réplica:

```powershell
docker compose exec mysql-replica mysql -uroot -p
```

Introducir MYSQL_ROOT_PASSWORD de .env.

```sql
SHOW REPLICA STATUS\G
SELECT * FROM pedidos.pedidos;
```

Comprobar:
- Replica_IO_Running: Yes.
- Replica_SQL_Running: Yes.
- Last_IO_Error y Last_SQL_Error sin errores.
- Los cambios de pedidos aparecen en la réplica.

Seconds_Behind_Source es un indicador de retraso, no una prueba
suficiente por sí solo de igualdad completa.

## 4. Interrupción y recuperación de la réplica

```powershell
docker compose stop mysql-replica
```

Crear y modificar pedidos.
Resultado esperado: el principal sigue atendiendo.

```powershell
docker compose start mysql-replica
```

Consultar SHOW REPLICA STATUS y comparar pedidos.
Resultado esperado: se aplican los cambios pendientes, siempre que el
binlog necesario siga disponible.

## 5. Caída y recuperación del principal

```powershell
docker compose stop mysql-primary
```

Intentar listar o crear pedidos.
Resultado esperado: error controlado de disponibilidad; no se afirma
que la réplica tome automáticamente el control.

```powershell
docker compose start mysql-primary
```

Esperar su recuperación y actualizar el listado.
Resultado esperado: los pedidos confirmados siguen almacenados y la
API vuelve a funcionar.

## 6. Edición concurrente

Abrir el mismo pedido en dos ventanas.
Guardar una modificación en la primera.
Intentar guardar desde la segunda sin recargar.

Resultado esperado: HTTP 409 y aviso de versión obsoleta.
Recargar y volver a abrir la edición para usar la versión actual.

## Evidencias

Guardar capturas o registros de:
1. Servicios activos.
2. Interfaz y pedido creado.
3. Identificación de ambos nodos.
4. backend-1 detenido y pedido atendido por backend-2.
5. Nodo recuperado.
6. Estado de replicación.
7. Resultado real de pytest.
8. Error controlado y recuperación del principal.

Añadir fecha, acción, resultado esperado y resultado observado.
