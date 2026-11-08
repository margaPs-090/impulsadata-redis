# MySQL con la base de datos de ImpulsaData ya creada y rellena
FROM mysql:8.0

# Los .sql se ejecutan por orden alfabético la primera vez que arranca el contenedor
COPY sql/01_schema.sql /docker-entrypoint-initdb.d/01_schema.sql
COPY sql/02_datos.sql  /docker-entrypoint-initdb.d/02_datos.sql
