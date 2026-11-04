from conexion import cliente, db

coleccion = db["movies"]


def mostrar_distribucion(operacion):
    print(f"\n--- Distribucion despues de {operacion} ---")

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


def insertar_pelicula():
    print("\n--- Insertar pelicula ---")

    ultima = coleccion.find_one(
        {},
        {"id_movie": 1},
        sort=[("id_movie", -1)]
    )

    id_movie = ultima["id_movie"] + 1 if ultima else 1

    titulo = input("Titulo: ")
    anio = int(input("Año: "))
    genero = input("Generos (separados por coma): ")
    director = input("Director: ")
    argumento = input("Argumento: ")

    pelicula = {
        "id_movie": id_movie,
        "title": titulo,
        "year": año,
        "genres": [g.strip() for g in genero.split(",")],
        "directors": [director],
        "plot": argumento,
        "type": "movie"
    }

    resultado = coleccion.insert_one(pelicula)

    print("Pelicula insertada correctamente.")
    print("ID:", resultado.inserted_id)
    print("ID de pelicula:", id_movie)

    mostrar_distribucion("CREATE")


def consultar_peliculas():
    print("\n--- Consultar peliculas ---")

    limite = int(input("Cantidad de peliculas a mostrar: "))

    peliculas = coleccion.find(
        {},
        {"_id": 0}
    ).sort("id_movie", 1).limit(limite)

    for pelicula in peliculas:
        print("\nID:", pelicula.get("id_movie"))
        print("Titulo:", pelicula.get("title"))
        print("Año:", pelicula.get("year"))
        print("Generos:", pelicula.get("genres"))
        print("Director:", pelicula.get("directors"))
        print("Argumento:", pelicula.get("plot"))

    mostrar_distribucion("READ")


def actualizar_pelicula():
    print("\n--- Actualizar pelicula ---")

    id_movie = int(input("ID de la pelicula: "))

    pelicula = coleccion.find_one({"id_movie": id_movie})

    if pelicula:
        print("Pelicula encontrada:", pelicula.get("title"))

        titulo = input("Nuevo titulo (Enter para conservar): ")
        anio = input("Nuevo año (Enter para conservar): ")
        argumento = input("Nuevo argumento (Enter para conservar): ")

        cambios = {}

        if titulo:
            cambios["title"] = titulo

        if anio:
            cambios["year"] = int(año)

        if argumento:
            cambios["plot"] = argumento

        if cambios:
            resultado = coleccion.update_one(
                {"id_movie": id_movie},
                {"$set": cambios}
            )

            print("Documentos modificados:", resultado.modified_count)
        else:
            print("No se realizaron cambios.")

    else:
        print("No se encontro la pelicula.")

    mostrar_distribucion("UPDATE")


def eliminar_pelicula():
    print("\n--- Eliminar pelicula ---")

    id_movie = int(input("ID de la pelicula: "))

    pelicula = coleccion.find_one({"id_movie": id_movie})

    if pelicula:
        print("Pelicula:", pelicula.get("title"))

        confirmar = input("¿Desea eliminarla? (s/n): ")

        if confirmar.lower() == "s":
            resultado = coleccion.delete_one(
                {"id_movie": id_movie}
            )

            print("Documentos eliminados:", resultado.deleted_count)
        else:
            print("Operacion cancelada.")
    else:
        print("No se encontro la pelicula.")

    mostrar_distribucion("DELETE")


def main():
    while True:
        print("\n===================================")
        print("       CRUD DE PELICULAS")
        print("===================================")
        print("1. Insertar pelicula")
        print("2. Consultar peliculas")
        print("3. Actualizar pelicula")
        print("4. Eliminar pelicula")
        print("5. Salir")
        print("===================================")

        opcion = input("Seleccione una opcion: ")

        try:
            if opcion == "1":
                insertar_pelicula()

            elif opcion == "2":
                consultar_peliculas()

            elif opcion == "3":
                actualizar_pelicula()

            elif opcion == "4":
                eliminar_pelicula()

            elif opcion == "5":
                print("Saliendo del programa...")
                break

            else:
                print("Opcion no valida.")

        except ValueError:
            print("Error: ingrese un valor numerico valido.")

        except Exception as error:
            print("Error durante la operacion:", error)


if __name__ == "__main__":
    try:
        cliente.admin.command("ping")
        print("Conexion con MongoDB exitosa.")
        main()

    except Exception as error:
        print("Error de conexion:", error)

    finally:
        cliente.close()