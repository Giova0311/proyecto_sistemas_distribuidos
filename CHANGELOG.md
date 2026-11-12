# Registro de cambios

## Parche 01 — Manual técnico

### Añadido

- Manual técnico en docs/manual_tecnico.md.
- Diagrama de componentes y flujo de datos.
- Explicación de redundancia, replicación e idempotencia.
- Procedimiento de fallo simulado y recuperación.
- Tecnologías empleadas y justificación.
- Limitaciones de disponibilidad.

### Aplicación

Actualización exclusivamente documental.
No requiere reconstruir imágenes ni reiniciar Docker.
No modifica tablas, pedidos ni variables de entorno.

### Validación

Contenido contrastado con la configuración y documentación existente.
No se ejecutaron pruebas del sistema como parte de este parche.

### Pendientes de entrega

- Manual de usuario con capturas reales.
- Pruebas unitarias aisladas.
- Ejecución de pruebas de integración y fallo.
- Informe con resultados observados y conclusiones.

## Parche 02 — Manual de usuario

### Añadido

- Instrucciones de instalación y ejecución.
- Guía para crear, buscar, editar y eliminar pedidos.
- Explicación de estados, paginación y conflictos de edición.
- Soluciones a problemas frecuentes.
- Lista de capturas pendientes.

### Validación

Instrucciones de uso contrastadas con los componentes de la interfaz.
La instalación en un equipo nuevo no se ha probado en este parche.

### Aplicación

Actualización documental.
No requiere reconstruir imágenes ni reiniciar Docker.

## Parche 03 — Evidencias visuales

### Añadido

- Tres capturas reales en docs/capturas/.
- Imágenes y descripciones incorporadas al manual de usuario.

### Validación

Revisión visual de la pantalla inicial, la confirmación de creación
del pedido #1 y el formulario de edición.
El pedido mostrado contiene 3 unidades a $5.000: total $15.000.

La captura de edición no demuestra un cambio de estado guardado.
Estas evidencias no sustituyen las pruebas automatizadas ni de fallos.

### Aplicación

Actualización documental. No requiere reiniciar Docker.

## Parche 04 — Pruebas unitarias de validación

### Añadido

- backend/tests/test_unitarios.py.
- Nueve casos de validación de los datos de creación de pedidos.
- Comprobación de normalización de textos y representación decimal.

### Alcance

Las pruebas instancian directamente el esquema PedidoCrear.
No realizan solicitudes HTTP ni conexiones a MySQL.
Complementan las pruebas de integración existentes.

### Ejecución

Desde la raíz del proyecto:

docker compose build backend-1 backend-2
docker compose run --rm --no-deps backend-1 python -m pytest -v tests/test_unitarios.py

El segundo comando crea un contenedor temporal con la imagen actualizada.
No inicia sus servicios dependientes y elimina el contenedor al terminar.

### Resultado

Ejecución realizada en Docker con Python 3.12.16 y pytest 8.3.5.

- Casos ejecutados: 9.
- Aprobados: 9.
- Fallidos: 0.
- Duración reportada: 0.63 segundos.
- Avisos: 2, relacionados con permisos para escribir la caché de pytest.

Los avisos no impidieron ejecutar las pruebas.
En las siguientes ejecuciones se desactiva la caché mediante
-p no:cacheprovider.

### Aplicación

Se añaden pruebas; no se modifica la lógica de la aplicación,
el esquema de datos ni las variables de entorno.

## Parche 05 — Informe de pruebas ejecutadas

### Añadido

- docs/informe_pruebas.md con procedimientos y resultados observados.
- Registro de 9 casos unitarios aprobados.
- Registro de 8 casos de integración aprobados.
- Registro de 2 escenarios de detención y recuperación de backends.
- Estado final de los servicios y límites de las comprobaciones.

### Aplicación

Actualización documental.
No requiere reconstruir imágenes ni reiniciar Docker.
