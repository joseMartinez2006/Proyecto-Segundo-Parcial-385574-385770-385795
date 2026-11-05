# Guía de instalación y ejecución del proyecto

## 1. Requisitos previos

Para ejecutar el proyecto se necesita:

- Git.
- Docker.
- Docker Compose.
- Python 3.
- MongoDB Shell (`mongosh`), disponible dentro de los contenedores de MongoDB.

## 2. Obtener el proyecto

Clonar el repositorio:

```bash
git clone https://github.com/joseMartinez2006/Proyecto-Segundo-Parcial-385574-385770-385795.git
```

Ingresar al directorio:

```bash
cd Proyecto-Segundo-Parcial-385574-385770-385795
```

Verificar que se encuentren los archivos principales:

```bash
ls
```

La estructura principal debe contener:

```text
docker-compose.yml
scripts/
app/
datos/
requirements.txt
```

## 3. Verificar la configuración de Docker

Comprobar que Docker y Docker Compose estén disponibles:

```bash
docker --version
docker compose version
```

Validar el archivo de configuración:

```bash
docker compose config --quiet
```

Si no aparece ningún error, la configuración es válida.

## 4. Iniciar los servidores MongoDB

Primero se levantan el servidor de configuración y los tres nodos que funcionarán como shards:

```bash
docker compose up -d configsvr shard1 shard2 shard3
```

Verificar que los contenedores estén funcionando:

```bash
docker compose ps
```

### ¿Qué hace este comando?

- `configsvr`: almacena los metadatos de configuración del clúster.
- `shard1`: primer nodo de almacenamiento.
- `shard2`: segundo nodo de almacenamiento.
- `shard3`: tercer nodo de almacenamiento.
- `-d`: ejecuta los contenedores en segundo plano.

## 5. Inicializar los Replica Sets

Cada nodo debe inicializar su Replica Set mediante su respectivo archivo JavaScript.

**Servidor de configuración:**

```bash
docker compose exec configsvr mongosh --port 27019 --file /scripts/01-configsvr.js
```

**Shard 1:**

```bash
docker compose exec shard1 mongosh --port 27018 --file /scripts/02-shard1.js
```

**Shard 2:**

```bash
docker compose exec shard2 mongosh --port 27018 --file /scripts/02-shard2.js
```

**Shard 3:**

```bash
docker compose exec shard3 mongosh --port 27018 --file /scripts/02-shard3.js
```

Cada script inicializa su respectivo Replica Set.

Verificar el estado de cada uno:

```bash
docker compose exec configsvr mongosh --port 27019 --quiet --eval 'rs.status().myState'

docker compose exec shard1 mongosh --port 27018 --quiet --eval 'rs.status().myState'

docker compose exec shard2 mongosh --port 27018 --quiet --eval 'rs.status().myState'

docker compose exec shard3 mongosh --port 27018 --quiet --eval 'rs.status().myState'
```

El resultado esperado en cada caso es `1`, que indica que el nodo es PRIMARY.

## 6. Iniciar el router mongos

Una vez inicializados los Replica Sets, iniciar el router:

```bash
docker compose up -d mongos
```

Verificar los contenedores:

```bash
docker compose ps
```

El router `mongos` permite acceder al clúster distribuido y dirigir las operaciones hacia los shards correspondientes.

El puerto publicado para la conexión desde Python es `27020`.

## 7. Configurar el clúster distribuido

Ejecutar:

```bash
docker compose exec mongos mongosh --file /scripts/03-configurar-cluster.js
```

Este archivo configura el nivel de confirmación de escritura, agrega los tres shards al clúster y habilita el sharding en la base de datos `sample_mflix`.

Verificar que los tres shards estén registrados:

```bash
docker compose exec mongos mongosh --quiet --eval 'db.adminCommand({listShards: 1})'
```

## 8. Configurar el sharding de la colección movies

Ejecutar:

```bash
docker compose exec mongos mongosh --file /scripts/06-configurar-movies.js
```

Este script configura la colección `movies` de la base de datos `sample_mflix` y establece la siguiente shard key:

```javascript
{ id_movie: "hashed" }
```

La clave de tipo Hash permite distribuir los documentos utilizando valores hash del campo `id_movie`.

## 9. Instalar las dependencias de Python

Instalar las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

Verificar la conexión:

```bash
python app/conexion.py
```

La salida esperada es similar a:

```text
Conexion con MongoDB exitosa.
Base de datos: sample_mflix
```

## 10. Importar las películas

Los datos originales se encuentran en:

```text
datos/sample_mflix.movies.json
```

Ejecutar:

```bash
python app/importar_peliculas.py
```

Este programa lee el archivo JSON, asigna un identificador secuencial mediante el campo `id_movie` e inserta los documentos en lotes de 500.

En la ejecución comprobada se importaron **21,349 películas**.

> **Importante:** ejecutar la importación únicamente cuando la colección esté vacía. El programa cancela la operación si detecta documentos existentes para evitar duplicar la información.

## 11. Ejecutar las operaciones CRUD

Iniciar el programa:

```bash
python app/crud_peliculas.py
```

El programa permite realizar las siguientes operaciones:

| Operación | Descripción |
|---|---|
| Create | Insertar una película. |
| Read | Consultar películas almacenadas. |
| Update | Modificar información de una película. |
| Delete | Eliminar una película. |

Después de cada operación, el programa muestra la distribución de documentos entre los tres shards mediante `$shardedDataDistribution`.

## 12. Comprobar la distribución de documentos

Para consultar directamente la distribución de la colección, ejecutar:

```bash
docker compose exec mongos mongosh --quiet --eval 'db.getSiblingDB("admin").aggregate([{$shardedDataDistribution:{}},{$match:{ns:"sample_mflix.movies"}}]).forEach(printjson)'
```

El resultado muestra la cantidad de documentos almacenados en cada shard y la información sobre los documentos huérfanos.

## 13. Comprobar la distribución adicional

Para realizar una prueba de inserción de documentos adicionales, ejecutar:

```bash
python app/carga_distribucion.py
```

Este programa inserta 300 documentos adicionales y muestra la distribución inicial y final.

En la ejecución comprobada se obtuvieron los siguientes resultados:

| Shard | Documentos |
|---|---:|
| shard1rs | 7,248 |
| shard2rs | 7,028 |
| shard3rs | 7,373 |
| **Total** | **21,649** |

## 14. Verificar el balanceador

Ejecutar:

```bash
docker compose exec mongos mongosh --quiet --eval 'print("Balanceador habilitado:", sh.getBalancerState()); print("Balanceador ejecutandose:", sh.isBalancerRunning()); sh.status()'
```

Esta consulta permite comprobar el estado del balanceador, los shards registrados, la shard key, la cantidad de chunks y la distribución de documentos.

El resultado esperado para el balanceador habilitado es:

```text
Balanceador habilitado: true
```

## 15. Detener los contenedores

Al terminar de trabajar, ejecutar:

```bash
docker compose down
```

Este comando detiene y elimina los contenedores y la red creada por Docker Compose, pero conserva los volúmenes de datos.

Para eliminar también los volúmenes y los datos almacenados en ellos:

```bash
docker compose down -v
```

> **Advertencia:** no utilizar `docker compose down -v` si se desea conservar la base de datos.

---

## Resumen del funcionamiento del proyecto

El proyecto utiliza una arquitectura de MongoDB Sharding compuesta por un servidor de configuración, tres shards y un router `mongos`.

El funcionamiento general es el siguiente:

1. Se inician los servidores MongoDB mediante Docker Compose.
2. Se inicializan los Replica Sets del servidor de configuración y de los tres shards.
3. Se inicia el router `mongos`.
4. Se registran los shards y se habilita el sharding en `sample_mflix`.
5. Se configura la colección `movies` con una shard key de tipo Hash sobre `id_movie`.
6. Se importan las películas desde el archivo JSON.
7. Se ejecutan las operaciones CRUD mediante Python y PyMongo.
8. Se consulta la distribución de documentos entre los shards.
9. Se comprueba el estado del balanceador.
