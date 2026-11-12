# Informe de pruebas

## 1. Objetivo

Verificar la validación de datos, las operaciones de pedidos,
el balanceo entre backends, la replicación de MySQL y la continuidad
del servicio al detener una instancia de backend.

Los resultados corresponden a las ejecuciones realizadas en el equipo
local del proyecto y a las salidas de terminal registradas durante
la validación.

## 2. Entorno

- Equipo anfitrión: Windows con Docker Desktop.
- Contenedores Linux.
- Python del contenedor de pruebas: 3.12.16.
- pytest: 8.3.5.
- Dos instancias FastAPI: backend-1 y backend-2.
- NGINX como entrada y balanceador.
- MySQL 8.4 principal y réplica.
- Aplicación: http://localhost:8080.
- Rama de trabajo: actualizacion/documentacion-entrega.

Las pruebas unitarias y de integración se ejecutaron desde contenedores
temporales. La simulación de fallos se ejecutó desde Windows.

## 3. Pruebas unitarias

Archivo: backend/tests/test_unitarios.py.

Estas pruebas validan directamente el esquema de creación de pedidos,
sin realizar solicitudes HTTP ni conexiones a MySQL.

| Caso                       | Resultado esperado                                              | Resultado observado |
| -------------------------- | --------------------------------------------------------------- | ------------------- |
| Datos válidos              | Aceptación, eliminación de espacios exteriores y precio Decimal | Aprobado            |
| Cantidad cero              | Rechazo                                                         | Aprobado            |
| Cantidad negativa          | Rechazo                                                         | Aprobado            |
| Cantidad superior a 100000 | Rechazo                                                         | Aprobado            |
| Cantidad fraccionaria      | Rechazo                                                         | Aprobado            |
| Precio cero                | Rechazo                                                         | Aprobado            |
| Precio negativo            | Rechazo                                                         | Aprobado            |
| Precio con tres decimales  | Rechazo                                                         | Aprobado            |
| Precio superior al límite  | Rechazo                                                         | Aprobado            |

Comando ejecutado:

```bat
docker compose run --rm --no-deps backend-1 python -m pytest -v tests/test_unitarios.py
```

Resultado:

```text
9 passed, 2 warnings in 0.63s
```

Los dos avisos correspondieron a permisos insuficientes para escribir
la caché de pytest en /app. No impidieron ejecutar las pruebas.

En ejecuciones posteriores se desactivó esa caché mediante
-p no:cacheprovider.

## 4. Pruebas de integración

Archivos:

- backend/tests/test_pedidos.py.
- backend/tests/test_replicacion.py.

Comando ejecutado:

```bat
docker compose run --rm --no-deps backend-1 python -m pytest -v -p no:cacheprovider tests/test_pedidos.py tests/test_replicacion.py
```

| Prueba                       | Comprobaciones                                                                   | Resultado |
| ---------------------------- | -------------------------------------------------------------------------------- | --------- |
| CRUD, idempotencia y versión | Crear, consultar, actualizar, eliminar, total calculado, reintentos y conflictos | Aprobada  |
| Validación: cantidad cero    | Respuesta HTTP 422                                                               | Aprobada  |
| Validación: precio negativo  | Respuesta HTTP 422                                                               | Aprobada  |
| Validación: cliente vacío    | Respuesta HTTP 422                                                               | Aprobada  |
| Validación: tres decimales   | Respuesta HTTP 422                                                               | Aprobada  |
| Clave obligatoria            | Rechazo de creación sin Idempotency-Key                                          | Aprobada  |
| Balanceo                     | Respuestas identificadas como backend-1 y backend-2                              | Aprobada  |
| Replicación                  | Creación, actualización y eliminación reflejadas en la réplica                   | Aprobada  |

La prueba de CRUD también comprobó:

- Total de 30001.00 para dos unidades a 15000.50.
- Reutilización de una clave con los mismos datos sin duplicar el pedido.
- Rechazo de la misma clave con datos diferentes.
- Rechazo de una versión obsoleta.
- Rechazo de un salto de estado.
- Rechazo de un reintento antiguo después de eliminar el pedido.

Resultado:

```text
8 passed in 4.96s
```

La prueba de replicación verificó los cambios dentro del plazo de
20 segundos definido por el test. No se midió el retraso exacto.

## 5. Pruebas de fallo y recuperación

Script: scripts/probar_fallos.py.

Comando ejecutado:

```bat
python scripts/probar_fallos.py
```

### Escenario 1: detener backend-1

Acción: detener backend-1 mediante Docker Compose.

Resultado esperado: backend-2 continúa atendiendo solicitudes.

Resultado observado:

- backend-2 creó el pedido #4.
- El pedido pudo consultarse.
- backend-1 volvió a iniciarse y se reincorporó al balanceo.

Estado: aprobado.

### Escenario 2: detener backend-2

Acción: detener backend-2 mediante Docker Compose.

Resultado esperado: backend-1 continúa atendiendo solicitudes.

Resultado observado:

- backend-1 creó el pedido #5.
- El pedido pudo consultarse.
- backend-2 volvió a iniciarse y se reincorporó al balanceo.

Estado: aprobado.

### Extracto de la salida

```text
OK: backend-2 creó y consultó el pedido #4.
OK: backend-1 se reincorporó al balanceo.
OK: backend-1 creó y consultó el pedido #5.
OK: backend-2 se reincorporó al balanceo.
Pruebas de caída y recuperación completadas.
```

El script incluye la eliminación de sus pedidos de prueba.

## 6. Estado posterior

Se ejecutó:

```bat
docker compose ps -a
```

| Servicio      | Estado observado        |
| ------------- | ----------------------- |
| backend-1     | En ejecución, saludable |
| backend-2     | En ejecución, saludable |
| mysql-primary | En ejecución, saludable |
| mysql-replica | En ejecución, saludable |
| frontend      | En ejecución            |
| nginx         | En ejecución            |
| bootstrap     | Finalizado con código 0 |

## 7. Resumen

| Grupo                                  | Aprobados | Fallidos |
| -------------------------------------- | --------: | -------: |
| Casos unitarios                        |         9 |        0 |
| Casos de integración                   |         8 |        0 |
| Escenarios de detención y recuperación |         2 |        0 |

Se aprobaron 17 casos mediante pytest y dos escenarios adicionales
mediante el script de fallos.

## 8. Conclusiones y límites

Las ejecuciones comprobaron la validación de entradas, las operaciones
de pedidos, las comprobaciones de idempotencia y versión, el balanceo
y la replicación de los cambios probados.

El sistema mantuvo la capacidad de crear y consultar pedidos con
un backend detenido. Ambos nodos pudieron reincorporarse.

La simulación utilizó docker compose stop, una detención controlada.
No demuestra el comportamiento ante todas las interrupciones abruptas,
particiones de red o fallos durante una transacción.

No se ejecutaron en esta sesión pruebas de caída del principal,
caída de la réplica, carga masiva o caída del equipo anfitrión.

No se midió el tiempo exacto de recuperación ni se certifica
disponibilidad continua durante cada instante de la prueba.

La replicación es asíncrona y no existe promoción automática de la
réplica. La caída de MySQL principal sigue impidiendo gestionar pedidos
hasta su recuperación.
