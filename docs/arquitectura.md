# Arquitectura y decisiones

## Componentes

| Componente | Responsabilidad |
|---|---|
| React | Formulario, listado, filtros y gestión de pedidos |
| NGINX | Entrada HTTP y balanceo entre los dos nodos |
| backend-1 | API REST sin sesiones locales |
| backend-2 | Misma API REST, proceso independiente |
| MySQL principal | Todas las lecturas y escrituras de la API |
| MySQL réplica | Copia asíncrona de la base pedidos |
| bootstrap | Usuarios, esquema y configuración inicial de réplica |

## Recorrido de una solicitud

El navegador solicita la interfaz a NGINX, que la obtiene del contenedor
frontend. Las solicitudes /api llegan al grupo de backends. Cada backend
consulta o modifica MySQL principal. MySQL registra las transacciones
en el binlog y la réplica las aplica.

Los backends no necesitan llamarse entre sí: son instancias equivalentes
del mismo servicio REST y comparten la persistencia. No se afirma que
sean microservicios con responsabilidades diferentes.

## Consistencia

La API lee y escribe en el principal, evitando lecturas atrasadas
de la réplica después de una escritura.

La replicación es asíncrona: la confirmación de un pedido no significa
que la réplica ya lo haya aplicado. No se promete pérdida cero ante
destrucción del principal.

Los cambios se confirman en transacciones InnoDB.
Las actualizaciones bloquean la fila y comprueban version.
Una edición basada en datos anteriores devuelve HTTP 409.

## Reintentos de creación

El cliente envía una UUID en Idempotency-Key.
La tabla solicitudes guarda la clave, la huella de los datos y el ID
del pedido en la misma transacción que crea el pedido.

Dos nodos que reciban la misma clave no pueden confirmar dos registros
de solicitud: la clave primaria resuelve la carrera.

La misma clave con datos diferentes devuelve 409.
Si el pedido fue eliminado, un reintento de la clave antigua devuelve
409 y no recrea el pedido.

El frontend conserva en localStorage la clave de una creación pendiente.
Una edición o eliminación con respuesta perdida debe comprobarse
recargando el listado.

## Salud y fallos

/health/live indica que el proceso responde.
/health/ready comprueba también una consulta al principal.

Docker informa la salud de los backends.
NGINX utiliza detección pasiva de fallos y reintenta ciertas respuestas
en el otro backend. No consulta activamente /health/ready.

No se habilita proxy_next_upstream non_idempotent.
Una solicitud que falla mientras está en curso puede devolver error;
se debe comprobar su resultado o reintentar la creación con su clave.

## Replicación

MySQL 8.4 usa server-id diferentes, binlog y GTID.
La réplica filtra las tablas pedidos.%.
Los usuarios administrativos locales no se replican.
El usuario lector solo tiene SELECT.
read_only protege contra escrituras ordinarias en la réplica;
usuarios administrativos conservan capacidad de administración.

bootstrap configura el canal solo cuando no existe, crea las tablas
desde un único proceso y espera a que la réplica alcance el GTID del
principal al finalizar la inicialización.

La inicialización está diseñada para los volúmenes de este proyecto.
No sustituye un procedimiento de incorporación de réplicas a una base
existente cuyo historial binlog ya se haya purgado.

## Modelo de datos

pedidos:
- id: identificador.
- cliente y producto: textos validados.
- cantidad: entero positivo.
- precio_unitario: DECIMAL(12,2).
- estado: pendiente, en_proceso, enviado o entregado.
- version: contador para detectar ediciones concurrentes.
- creado_en y actualizado_en: fechas UTC.

total se calcula con Decimal a partir de cantidad y precio_unitario.

solicitudes:
- clave: UUID enviada por el cliente, clave primaria.
- huella: SHA-256 del contenido normalizado.
- pedido_id: pedido generado.

solicitudes conserva una referencia histórica sin clave foránea,
para mantener el registro de idempotencia tras eliminar un pedido.

## Límites de disponibilidad

| Fallo | Resultado esperado |
|---|---|
| backend-1 | backend-2 sigue atendiendo |
| backend-2 | backend-1 sigue atendiendo |
| Réplica | API operativa; copia atrasada |
| Principal | API de pedidos no disponible hasta recuperación |
| Ambos backends | API no disponible |
| NGINX | Entrada web no disponible |
| Equipo anfitrión | Demostración completa no disponible |

Para tolerar automáticamente la pérdida del principal se necesita
otra arquitectura: elección/promoción, quorum o fencing, enrutamiento
del escritor y procedimientos de recuperación. No se implementa
una promoción improvisada que pueda causar dos escritores.
