const database = db.getSiblingDB("sample_mflix");

print("== Crear coleccion movies ==");

database.createCollection("movies");

print("== Configurar Shard Key Hashed ==");

printjson(
    sh.shardCollection(
        "sample_mflix.movies",
        { id_movie: "hashed" }
    )
);

print("== Verificar configuracion ==");

printjson(
    database.movies.getShardVersion()
);

sh.status();