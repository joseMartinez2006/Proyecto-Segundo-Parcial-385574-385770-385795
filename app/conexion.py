from pymongo import MongoClient

URI = "mongodb://localhost:27020/"

cliente = MongoClient(URI)

db = cliente["sample_mflix"]

def probar_conexion():
    try:
        cliente.admin.command("ping")
        print("Conexion con MongoDB exitosa.")
        print("Base de datos:", db.name)
    except Exception as error:
        print("Error de conexion:", error)


if __name__ == "__main__":
    probar_conexion()