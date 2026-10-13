import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def obtener_conexion():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def obtener_conexion_pruebas():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        dbname="incidencias_test",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )