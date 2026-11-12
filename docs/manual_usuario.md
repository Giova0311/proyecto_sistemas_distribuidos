# Manual de usuario

## 1. Descripción

La aplicación permite registrar, consultar, buscar, editar y eliminar
pedidos. Cada pedido contiene un producto, su cantidad y precio unitario.

Es una demostración académica local. No requiere iniciar sesión.

## 2. Requisitos

- Git, si se descarga el proyecto mediante el repositorio.
- Docker Desktop iniciado y configurado para contenedores Linux.
- Docker Compose v2.
- Navegador web.
- Puerto 8080 disponible.
- Internet durante la descarga y construcción inicial.

No es necesario instalar MySQL ni Node.js en Windows para ejecutar
la aplicación con Docker.

## 3. Instalación en un equipo nuevo

Abrir CMD en la ubicación donde se guardará el proyecto:

```bat
git clone https://github.com/Giova0311/proyecto_sistemas_distribuidos.git sistema-pedidos
cd sistema-pedidos
```

Crear la configuración local:

```bat
copy .env.example .env
```

Editar .env y reemplazar las cuatro contraseñas de ejemplo por
contraseñas diferentes.

Usar letras, números, guion o guion bajo:

- REPLICATION_PASSWORD: entre 16 y 32 caracteres.
- Las otras contraseñas: entre 16 y 128 caracteres.

No publicar .env ni incluirlo en capturas.

Si el equipo ya tiene el proyecto funcionando, conservar su .env.
Cambiar ese archivo no cambia automáticamente las contraseñas
almacenadas en los volúmenes existentes de MySQL.

## 4. Iniciar el sistema

Desde la raíz del proyecto:

```bat
docker compose up -d --build
docker compose ps -a
docker compose logs bootstrap
```

En el primer inicio, la construcción puede tardar varios minutos.

Comprobar:

- MySQL principal y réplica saludables.
- Los dos backends saludables.
- Frontend y NGINX en ejecución.
- bootstrap finalizado con código 0.

bootstrap es un proceso temporal. Que termine correctamente es normal.

Abrir:

http://localhost:8080

## 5. Crear un pedido

En el formulario "Nuevo pedido":

1. Escribir el nombre del cliente.
2. Escribir el nombre del producto.
3. Introducir una cantidad entera mayor que cero.
4. Introducir un precio unitario positivo, con hasta dos decimales.
5. Revisar el total calculado.
6. Pulsar "Crear pedido".

Ejemplo:

| Campo           | Valor                   |
| --------------- | ----------------------- |
| Cliente         | Cliente de demostración |
| Producto        | Cuaderno                |
| Cantidad        | 3                       |
| Precio unitario | 5000                    |
| Total esperado  | 15000                   |

El sistema muestra un mensaje con el número del pedido registrado.
El pedido comienza en estado pendiente.

Si no aparece en el listado, revisar los filtros de búsqueda y estado.

## 6. Consultar y buscar

El listado muestra cliente, producto, cantidad, total, estado y acciones.

Para buscar:

1. Escribir parte del cliente o producto.
2. Pulsar "Buscar".

Para filtrar por estado, seleccionar una opción del desplegable.

Para quitar los filtros:

1. Vaciar el campo de búsqueda.
2. Seleccionar "Todos los estados".
3. Pulsar "Buscar".

El listado muestra hasta diez pedidos por página.
Utilizar "Anterior" y "Siguiente" para recorrer los resultados.

"Actualizar" vuelve a consultar los pedidos conservando los filtros.

## 7. Editar un pedido

1. Pulsar "Editar" en el pedido.
2. Modificar sus datos en el formulario.
3. Pulsar "Guardar cambios".

Para salir sin guardar, pulsar "Cancelar edición".

Si otra persona o ventana modificó el mismo pedido, el sistema puede
rechazar el cambio por versión obsoleta. Cancelar la edición, actualizar
el listado y abrir nuevamente el pedido antes de modificarlo.

## 8. Cambiar el estado

El recorrido permitido es:

Pendiente → En proceso → Enviado → Entregado.

El selector de edición permite conservar el estado actual o avanzar
al siguiente. No permite retroceder ni saltar estados.

Para avanzar:

1. Pulsar "Editar".
2. Seleccionar el siguiente estado.
3. Pulsar "Guardar cambios".

## 9. Eliminar un pedido

1. Pulsar "Eliminar".
2. Revisar el número de pedido en la confirmación.
3. Aceptar para eliminarlo o cancelar para conservarlo.

No existe una papelera ni un botón para deshacer la eliminación.

## 10. Problemas frecuentes

| Situación                     | Acción                                                                     |
| ----------------------------- | -------------------------------------------------------------------------- |
| La página no abre             | Comprobar Docker Desktop y ejecutar docker compose ps -a                   |
| No aparecen pedidos           | Revisar los filtros y pulsar Actualizar                                    |
| Datos rechazados              | Revisar los campos obligatorios, cantidad y precio                         |
| Conflicto de versión          | Cancelar la edición, actualizar y volver a editar                          |
| Error de conexión al guardar  | Recuperar la conexión y consultar el listado antes de repetir la operación |
| Un backend deja de funcionar  | El otro puede seguir atendiendo; una solicitud en curso puede fallar       |
| MySQL principal está detenido | Recuperar el servicio; la réplica no lo reemplaza automáticamente          |

Para consultar registros:

```bat
docker compose logs --tail=100 bootstrap backend-1 backend-2 nginx
```

## 11. Detener y volver a iniciar

Detener:

```bat
docker compose stop
```

Volver a iniciar los contenedores existentes:

```bat
docker compose start
```

Estos comandos conservan los datos.

No utilizar docker compose down -v si se quieren conservar los pedidos:
esa opción elimina los volúmenes de datos.

## 12. Capturas del sistema

## 12. Capturas del sistema

### Pantalla principal

La pantalla reúne el formulario de registro, los filtros y el listado
de pedidos.

![Pantalla principal](capturas/cap_1.png.png)

### Creación de un pedido

Pedido de demostración con tres cuadernos a $5.000 por unidad,
para un total de $15.000.

![Pedido creado](capturas/cap_2.png.png)

### Edición del estado

Formulario de edición con el siguiente estado seleccionado,
antes de guardar los cambios.

![Edición del estado](capturas/cap_3.png.png)
