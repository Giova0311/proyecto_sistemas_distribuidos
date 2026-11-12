# Sistema distribuido de gestión de pedidos

Proyecto académico con React, FastAPI, MySQL y NGINX.

## Requisitos

- Docker Desktop iniciado, con contenedores Linux y Docker Compose v2.
- Python 3.10 o superior para el script de pruebas de fallos.
- Conexión a Internet durante la primera construcción.
- Puerto local 8080 disponible.

No es necesario instalar MySQL, Node.js ni las dependencias de Python
directamente en Windows para ejecutar el sistema mediante Docker.

## Inicio en PowerShell

Desde la carpeta sistema-pedidos:

```powershell
docker compose up --build -d
docker compose ps -a
docker compose logs bootstrap
```

El generador crea un .env con contraseñas aleatorias.
Si falta, copia .env.example a .env y cambia las cuatro contraseñas.

La primera construcción tarda varios minutos.
El servicio bootstrap debe finalizar con código 0.
Los dos backends deben aparecer saludables.

- Aplicación: http://localhost:8080
- Swagger: http://localhost:8080/api/docs
- Disponibilidad: http://localhost:8080/api/health/ready

## Uso

1. Crear un pedido con cliente, producto, cantidad y precio unitario.
2. Buscarlo por cliente o producto.
3. Editarlo y avanzar su estado.
4. Eliminarlo con confirmación.

Estados:
pendiente -> en_proceso -> enviado -> entregado.

Se permite editar sin cambiar de estado, pero no retroceder ni saltar
estados. El sistema permite editar los datos y eliminar pedidos en
cualquier estado; es una decisión de alcance académico.

Cada pedido representa un producto con cantidad, no un carrito de
múltiples productos.

## Pruebas

Con todos los servicios funcionando:

```powershell
docker compose exec backend-1 pytest -q tests
python scripts/probar_fallos.py
```

Las pruebas crean y eliminan sus propios pedidos.
No deben ejecutarse a la vez que una demostración manual de fallos.

Las pruebas automatizadas cubren:

- Crear, consultar, actualizar y eliminar.
- Validación de entradas.
- Reintento con la misma clave sin crear un duplicado.
- Rechazo de una clave reutilizada con datos diferentes.
- Rechazo de una versión obsoleta.
- Restricciones de transición de estados.
- Distribución entre ambos nodos.
- Replicación de inserciones, actualizaciones y eliminaciones.
- Caída y reincorporación de cada backend, mediante script separado.

## Detener y volver a iniciar

```powershell
docker compose stop
docker compose start
```

Para eliminar contenedores conservando los datos:

```powershell
docker compose down
docker compose up -d
```

No añadas -v a down si quieres conservar los pedidos:
esa opción elimina los volúmenes de datos.

## Desarrollo del frontend

Opcional, si tienes Node.js instalado:

```powershell
cd frontend
npm install
npm run dev
```

Vite redirige /api a localhost:8080. Mantén Docker ejecutándose.
Conserva package-lock.json una vez generado para fijar las dependencias
transitivas. Las imágenes Docker usan etiquetas de versión, no digest.

## Diagnóstico

```powershell
docker compose ps -a
docker compose logs --tail=100 bootstrap backend-1 backend-2
docker compose logs --tail=100 mysql-primary mysql-replica nginx
```

Si bootstrap falla, resuelve la causa indicada antes de continuar.
Después puedes ejecutar de nuevo docker compose up -d.

Las contraseñas iniciales de root se guardan al crear los volúmenes.
Editar .env no modifica automáticamente esas contraseñas ya almacenadas.

## Alcance

La caída de un backend permite seguir operando con el otro.
La caída de la réplica permite operar contra el principal, pero
interrumpe temporalmente la replicación.
La caída del principal impide gestionar pedidos hasta que se recupere.

No hay promoción automática de la réplica.
NGINX y el principal siguen siendo puntos únicos de fallo.
Todos los contenedores se ejecutan inicialmente en un mismo equipo;
una caída del equipo completo no está cubierta.

Es una demostración local sin autenticación ni TLS.
El puerto se publica únicamente en 127.0.0.1.
No publicar directamente en Internet sin añadir control de acceso,
HTTPS, manejo de secretos y una estrategia de respaldo y recuperación.

Consulta docs/arquitectura.md y docs/pruebas_fallos.md.

## Documentación de entrega

- [Manual técnico](docs/manual_tecnico.md)
- [Manual de usuario y capturas](docs/manual_usuario.md)
- [Informe de pruebas](docs/informe_pruebas.md)
- [Registro de parches](CHANGELOG.md)
