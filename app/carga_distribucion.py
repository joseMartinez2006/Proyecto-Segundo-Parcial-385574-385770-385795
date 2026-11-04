from conexion import cliente, db

coleccion = db["movies"]


def mostrar_distribucion():
    resultado = cliente.admin.aggregate([
        {"$shardedDataDistribution": {}},
        {"$match": {"ns": "sample_mflix.movies"}}
    ])

    for documento in resultado:
        for shard in documento["shards"]:
            print(
                f"{shard['shardName']}: "
                f"{shard['numOwnedDocuments']} peliculas"
            )


try:
    cliente.admin.command("ping")
    print("Conexion con MongoDB exitosa.")

    print("\n== Distribucion inicial ==")
    mostrar_distribucion()

    existentes = coleccion.count_documents({
        "id_movie": {"$gte": 21350, "$lte": 21649}
    })

    if existentes > 0:
        print("\nYa existen peliculas con los ID de prueba.")
        print("Se cancela la insercion para evitar duplicados.")

    else:
        nuevas = []

        for i in range(300):
            id_movie = i + 21350

            pelicula = {
                "id_movie": id_movie,
                "title": f"Pelicula de distribucion {id_movie}",
                "year": 2020 + (i % 7),
                "genres": ["Prueba"],
                "directors": ["Director de prueba"],
                "type": "movie"
            }

            nuevas.append(pelicula)

        print("\n== Insertando 300 peliculas ==")

        resultado = coleccion.insert_many(nuevas)

        print("Documentos insertados:", len(resultado.inserted_ids))

        print("\n== Distribucion final ==")
        mostrar_distribucion()

        print("\nTotal de peliculas:", coleccion.count_documents({}))

except Exception as error:
    print("Error:", error)

finally:
    cliente.close()