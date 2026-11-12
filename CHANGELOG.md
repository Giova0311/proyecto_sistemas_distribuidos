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
Las capturas reales siguen pendientes.

### Aplicación

Actualización documental.
No requiere reconstruir imágenes ni reiniciar Docker.
