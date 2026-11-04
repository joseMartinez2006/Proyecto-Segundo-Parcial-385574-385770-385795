from bson import json_util
from pymongo import MongoClient

URI = "mongodb://localhost:27020/"
ARCHIVO = "datos/sample_mflix.movies.json"
TAMANO_LOTE = 500

cliente = MongoClient(URI)
db = cliente["sample_mflix"]
coleccion = db["movies"]

try:
    cliente.admin.command("ping")
    print("Conexion con MongoDB exitosa.")

    if coleccion.count_documents({}) > 0:
        print("La coleccion no esta vacia. Se cancela la importacion.")
    else:
        with open(ARCHIVO, "r", encoding="utf-8") as archivo:
            peliculas = json_util.loads(archivo.read())

        print("Peliculas leidas:", len(peliculas))

        for indice, pelicula in enumerate(peliculas, start=1):
            pelicula["id_movie"] = indice

        for inicio in range(0, len(peliculas), TAMANO_LOTE):
            lote = peliculas[inicio:inicio + TAMANO_LOTE]
            coleccion.insert_many(lote, ordered=False)

            insertadas = min(inicio + TAMANO_LOTE, len(peliculas))
            print(f"Insertadas: {insertadas}/{len(peliculas)}")

        print("Importacion finalizada.")
        print("Total de documentos:", coleccion.count_documents({}))

except Exception as error:
    print("Error durante la importacion:", error)

finally:
    cliente.close()