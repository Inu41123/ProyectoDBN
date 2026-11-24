import os
import time
import pymssql
from pymongo import MongoClient
from datetime import datetime

# =========================================================================
# CONFIGURACIÓN DE VARIABLES DE ENTORNO
# =========================================================================
SQL_HOST = os.getenv("SQL_SERVER_HOST", "sqlserver")
SQL_PORT = int(os.getenv("SQL_SERVER_PORT", 1433))
SQL_USER = os.getenv("SQL_SERVER_USER", "sa")
SQL_PASSWORD = os.getenv("SQL_SERVER_PASSWORD", "SqlServer2025!Campus")
SQL_DB_NAME = "CampusCloudDB"

MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_USER", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "Mongo123")
MONGO_DB_NAME = os.getenv("MONGO_DB", "campuscloud")

# =========================================================================
# CONEXIÓN SQL SERVER
# =========================================================================
def get_sql_connection(db=SQL_DB_NAME):
    return pymssql.connect(
        server=SQL_HOST,
        port=SQL_PORT,
        user=SQL_USER,
        password=SQL_PASSWORD,
        database=db,
        as_dict=True,
        autocommit=True
    )

# =========================================================================
# CONEXIÓN MONGODB
# =========================================================================
def get_mongo_collection():
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
    client = MongoClient(uri)
    db = client[MONGO_DB_NAME]
    return db["documentos"]

# =========================================================================
# INICIALIZACIÓN Y SEEDING DE LAS BASES DE DATOS
# =========================================================================
def init_databases():
    # 1. Inicializar SQL Server con reintentos
    max_retries = 10
    connected = False
    for attempt in range(max_retries):
        try:
            # Conectar a master primero
            conn_master = pymssql.connect(
                server=SQL_HOST,
                port=SQL_PORT,
                user=SQL_USER,
                password=SQL_PASSWORD,
                database="master",
                autocommit=True
            )
            cursor_m = conn_master.cursor()
            
            # Crear base de datos si no existe
            cursor_m.execute(f"""
                IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{SQL_DB_NAME}')
                BEGIN
                    CREATE DATABASE {SQL_DB_NAME};
                END
            """)
            conn_master.close()

            # Conectar a CampusCloudDB para crear tabla
            conn_app = get_sql_connection(SQL_DB_NAME)
            cursor_app = conn_app.cursor()
            cursor_app.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Usuarios')
                BEGIN
                    CREATE TABLE Usuarios (
                        id INT IDENTITY(1,1) PRIMARY KEY,
                        nombre NVARCHAR(100) NOT NULL,
                        email NVARCHAR(100) NOT NULL UNIQUE,
                        rol NVARCHAR(50) NOT NULL,
                        departamento NVARCHAR(100) DEFAULT 'Tecnología',
                        fecha_registro DATETIME DEFAULT GETDATE()
                    );

                    -- Datos iniciales del Equipo 1
                    INSERT INTO Usuarios (nombre, email, rol, departamento) VALUES
                    ('Héctor García', 'hector@campuscloud.edu.mx', 'Administrador', 'Dirección de TI'),
                    ('Cristian Mendoza', 'cristian@campuscloud.edu.mx', 'Docente', 'Ciencias Computacionales'),
                    ('Elan Rodríguez', 'elan@campuscloud.edu.mx', 'Estudiante', 'Ingeniería en Software');
                END
            """)
            conn_app.close()
            print("✅ SQL Server: Base de datos y tabla 'Usuarios' verificadas.")
            connected = True
            break
        except Exception as e:
            print(f"⏳ Esperando a SQL Server ({attempt+1}/{max_retries}): {e}")
            time.sleep(3)

    if not connected:
        print("⚠️ No se pudo inicializar SQL Server tras varios intentos.")

    # 2. Inicializar MongoDB
    try:
        col = get_mongo_collection()
        if col.count_documents({}) == 0:
            docs_seed = [
                {
                    "titulo": "Arquitectura_CampusCloud_v1.pdf",
                    "tipo_archivo": "PDF",
                    "categoria": "Académico",
                    "autor_email": "hector@campuscloud.edu.mx",
                    "descripcion": "Diagrama de arquitectura con NGINX, Python, SQL Server, Mongo y Duplicati.",
                    "tamanio_kb": 1540.0,
                    "fecha_subida": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "titulo": "Matriz_Respaldos_S3.xlsx",
                    "tipo_archivo": "Excel",
                    "categoria": "Técnico",
                    "autor_email": "cristian@campuscloud.edu.mx",
                    "descripcion": "Calendario y programación de respaldos a MinIO/SILO.",
                    "tamanio_kb": 420.5,
                    "fecha_subida": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "titulo": "Manual_Instalacion_Docker.docx",
                    "tipo_archivo": "Word",
                    "categoria": "Administrativo",
                    "autor_email": "elan@campuscloud.edu.mx",
                    "descripcion": "Instrucciones de orquestación de servicios en Windows WSL2.",
                    "tamanio_kb": 2100.0,
                    "fecha_subida": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
            col.insert_many(docs_seed)
            print("✅ MongoDB: Colección 'documentos' inicializada con datos semilla.")
        else:
            print("✅ MongoDB: Colección 'documentos' ya cuenta con registros.")
    except Exception as e:
        print(f"⚠️ Error al inicializar MongoDB: {e}")
