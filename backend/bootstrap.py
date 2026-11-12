# Se ejecuta en un contenedor temporal antes de arrancar los backends.
import os
import re
import time

import pymysql
from sqlalchemy import URL, create_engine

from app.db.database import Base
from app.models.pedido import Pedido, Solicitud

ROOT_PASSWORD = os.environ["MYSQL_ROOT_PASSWORD"]
APP_PASSWORD = os.environ["DB_PASSWORD"]
REPL_PASSWORD = os.environ["REPLICATION_PASSWORD"]
READER_PASSWORD = os.environ["REPLICA_READER_PASSWORD"]


if not 16 <= len(REPL_PASSWORD) <= 32:
    raise SystemExit(
        "REPLICATION_PASSWORD debe tener entre 16 y 32 caracteres."
    )

# El generador utiliza contraseñas hexadecimales. Esta validación
# evita interpolar valores arbitrarios en sentencias administrativas.
for value in (
    ROOT_PASSWORD, APP_PASSWORD, REPL_PASSWORD, READER_PASSWORD
):
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", value):
        raise SystemExit(
            "Usa contraseñas de 16-128 caracteres: letras, "
            "números, guion o guion bajo."
        )


def conectar(host):
    for intento in range(60):
        try:
            return pymysql.connect(
                host=host,
                user="root",
                password=ROOT_PASSWORD,
                autocommit=True,
                connect_timeout=3,
                read_timeout=40,
                cursorclass=pymysql.cursors.DictCursor,
            )
        except pymysql.MySQLError:
            time.sleep(2)
    raise RuntimeError(f"No fue posible conectar con {host}")


with conectar("mysql-primary") as principal:
    with principal.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS pedidos")
        cursor.execute(
            "CREATE USER IF NOT EXISTS 'replicador'@'%' "
            f"IDENTIFIED BY '{REPL_PASSWORD}'"
        )
        cursor.execute(
            "ALTER USER 'replicador'@'%' "
            f"IDENTIFIED BY '{REPL_PASSWORD}'"
        )
        cursor.execute(
            "GRANT REPLICATION SLAVE ON *.* TO 'replicador'@'%'"
        )
        cursor.execute(
            "CREATE USER IF NOT EXISTS 'pedidos_app'@'%' "
            f"IDENTIFIED BY '{APP_PASSWORD}'"
        )
        cursor.execute(
            "ALTER USER 'pedidos_app'@'%' "
            f"IDENTIFIED BY '{APP_PASSWORD}'"
        )
        cursor.execute(
            "REVOKE ALL PRIVILEGES, GRANT OPTION "
            "FROM 'pedidos_app'@'%'"
        )
        cursor.execute(
            "GRANT SELECT, INSERT, UPDATE, DELETE "
            "ON pedidos.* TO 'pedidos_app'@'%'"
        )

with conectar("mysql-replica") as replica:
    with replica.cursor() as cursor:
        # Los objetos administrativos locales no generan GTID propios.
        cursor.execute("SET SESSION sql_log_bin=0")
        cursor.execute("CREATE DATABASE IF NOT EXISTS pedidos")
        cursor.execute(
            "CREATE USER IF NOT EXISTS 'lector'@'%' "
            f"IDENTIFIED BY '{READER_PASSWORD}'"
        )
        cursor.execute(
            "ALTER USER 'lector'@'%' "
            f"IDENTIFIED BY '{READER_PASSWORD}'"
        )
        cursor.execute("GRANT SELECT ON pedidos.* TO 'lector'@'%'")
        cursor.execute("SET SESSION sql_log_bin=1")

        cursor.execute("SHOW REPLICA STATUS")
        estado = cursor.fetchone()

        if not estado:
            cursor.execute(
                "CHANGE REPLICATION FILTER "
                "REPLICATE_WILD_DO_TABLE = ('pedidos.%')"
            )
            cursor.execute(
                "CHANGE REPLICATION SOURCE TO "
                "SOURCE_HOST='mysql-primary', "
                "SOURCE_USER='replicador', "
                f"SOURCE_PASSWORD='{REPL_PASSWORD}', "
                "SOURCE_AUTO_POSITION=1, "
                "GET_SOURCE_PUBLIC_KEY=1, "
                "SOURCE_CONNECT_RETRY=2"
            )

        if not estado or (
            estado["Replica_IO_Running"] != "Yes"
            or estado["Replica_SQL_Running"] != "Yes"
        ):
            cursor.execute("START REPLICA")

# Solo este proceso crea las tablas, evitando carreras entre backends.
admin_engine = create_engine(
    URL.create(
        "mysql+pymysql",
        username="root",
        password=ROOT_PASSWORD,
        host="mysql-primary",
        database="pedidos",
    )
)
Base.metadata.create_all(admin_engine)
admin_engine.dispose()

with conectar("mysql-primary") as principal:
    with principal.cursor() as cursor:
        cursor.execute("SELECT @@GLOBAL.gtid_executed AS gtid")
        gtid = cursor.fetchone()["gtid"]

with conectar("mysql-replica") as replica:
    with replica.cursor() as cursor:
        cursor.execute(
            "SELECT WAIT_FOR_EXECUTED_GTID_SET(%s, 30) AS resultado",
            (gtid,),
        )
        if cursor.fetchone()["resultado"] != 0:
            raise RuntimeError(
                "La réplica no alcanzó al principal en 30 segundos."
            )

        cursor.execute("SHOW REPLICA STATUS")
        estado = cursor.fetchone()

        if (
            estado["Replica_IO_Running"] != "Yes"
            or estado["Replica_SQL_Running"] != "Yes"
        ):
            raise RuntimeError(
                "La replicación no está activa. "
                "Revisa SHOW REPLICA STATUS."
            )

print("Esquema preparado y replicación inicial comprobada.")
