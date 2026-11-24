# ☁️ Fase 5: Pipeline de Respaldos S3, Automatización y Restauración

**Proyecto:** CampusCloud - Infraestructura de Base de Datos en la Nube  
**Equipo 1:** Héctor, Cristian, Elan  
**Almacenamiento S3:** SILO (`pgsty/silo:latest`)  
**Bucket de Respaldos:** `respaldosbd`  
**Motores Asignados:** **MongoDB 8** y **Microsoft SQL Server 2025**  
**Fecha de Validación:** 23 de Noviembre de 2026  

---

## 1. Arquitectura del Flujo de Respaldos

```
  +-------------------------------------------------------------+
  |              DoubleCloud-backup-scheduler                   |
  |                                                             |
  |   Cron (Dom 02:00 CST) / Ejecución Manual                   |
  |                │                                            |
  |        backup-semanal.sh                                    |
  |         ├── backup-mongodb.sh                               |
  |         └── backup-sqlserver.sh                             |
  +──────────────┬───────────────────────────────┬──────────────+
                 │                               │
                 ▼ mongodump                     ▼ sqlcmd BACKUP
  +──────────────────────────────+   +──────────────────────────────+
  |     DoubleCloud-mongodb      |   |    DoubleCloud-sqlserver     |
  |      (Puerto 27017)          |   |        (Puerto 1433)         |
  +──────────────┬───────────────+   +───────────┬──────────────────+
                 │ /backups/*.archive.gz         │ /sqlserver-backups/*.bak
                 │                               │ (Volumen sqlserver_backup)
                 └───────────────┬───────────────┘
                                 │
                                 ▼ AWS CLI v2
                 +───────────────────────────────+
                 |       DoubleCloud-silo        |
                 |     (S3 API Puerto 9000)      |
                 |      Bucket: respaldosbd      |
                 |    ├── mongodb/*.archive.gz   |
                 |    └── sqlserver/*.bak        |
                 +───────────────────────────────+
```

---

## 2. Scripts de Respaldo por Motor

### 2.1 Respaldo MongoDB (`/scripts/backup-mongodb.sh`)
- **Herramienta:** `mongodump` con compresión integrada gzip en formato archivo binario (`--archive`).
- **Autenticación:** Utiliza credenciales de `admin` vía variables de entorno.
- **Ruta de Almacenamiento S3:** `s3://respaldosbd/mongodb/mongodb_<timestamp>.archive.gz`
- **Limpieza Local:** El archivo temporal en `/backups` se borra inmediatamente tras la subida exitosa a SILO.

### 2.2 Respaldo SQL Server 2025 (`/scripts/backup-sqlserver.sh`)
- **Herramienta:** `sqlcmd` (ODBC Driver 18 con `-C` TrustServerCertificate).
- **Mecanismo:** Envía instrucción Transact-SQL `BACKUP DATABASE CampusCloudDB TO DISK = '/var/opt/mssql/backup/<timestamp>.bak' WITH CHECKSUM, COMPRESSION, STATS = 10`.
- **Verificación de Integridad:** Ejecuta `RESTORE VERIFYONLY FROM DISK` antes de proceder al upload.
- **Ruta de Almacenamiento S3:** `s3://respaldosbd/sqlserver/CampusCloudDB_<timestamp>.bak`
- **Volumen Compartido:** Accede directamente a `/sqlserver-backups/` para subir el archivo con `aws s3 cp` y luego remueve el archivo local.

### 2.3 Orquestador Central (`/scripts/backup-semanal.sh`)
- Implementa control de concurrencia mediante mutex de bloqueo de directorio (`/backups/backup-semanal.lock`).
- Atrapa señales de salida para liberar el mutex (`trap 'rmdir "$LOCK"' EXIT`).
- Ejecuta secuencialmente ambos respaldos y cuenta cualquier código de error:
  ```sh
  ejecutar MongoDB /scripts/backup-mongodb.sh
  ejecutar SQLServer /scripts/backup-sqlserver.sh
  ```
- Retorna código 0 únicamente si ambos respaldos se cargaron exitosamente en S3.

---

## 3. Pruebas de Ejecución y Evidencia

### 3.1 Ejecución Manual del Respaldo Semanal
Comando ejecutado desde el host:
```powershell
docker exec DoubleCloud-backup-scheduler sh /scripts/backup-semanal.sh
```

**Salida Obtenida:**
```text
INICIO: 2026-11-23 17:58:56 CST
writing `campuscloud.documentos` to "archive `/backups/mongodb_20261123_175856.archive.gz`"
done dumping `campuscloud.documentos` (3 documents)
upload: backups/mongodb_20261123_175856.archive.gz to s3://respaldosbd/mongodb/mongodb_20261123_175856.archive.gz
OK MongoDB: mongodb/mongodb_20261123_175856.archive.gz (2002 bytes)
CORRECTO: MongoDB

BACKUP DATABASE successfully processed 530 pages in 0.067 seconds (61.742 MB/sec).
The backup set on file 1 is valid.
upload: sqlserver-backups/CampusCloudDB_20261123_175857.bak to s3://respaldosbd/sqlserver/CampusCloudDB_20261123_175857.bak
OK SQL Server: sqlserver/CampusCloudDB_20261123_175857.bak (4444160 bytes)
CORRECTO: SQLServer
FIN: 2026-11-23 17:58:58 CST; errores=0
```

### 3.2 Verificación de Objetos en SILO S3
Comando:
```powershell
docker exec DoubleCloud-backup-scheduler aws --endpoint-url http://minio:9000 s3 ls s3://respaldosbd/ --recursive --human-readable
```

**Resultado:**
- `mongodb/mongodb_20261123_175856.archive.gz` (~2 KiB)
- `sqlserver/CampusCloudDB_20261123_175857.bak` (~4.2 MiB)

---

## 4. Procedimiento de Restauración (Disaster Recovery)

### 4.1 Restauración de MongoDB
1. Descarga del artefacto desde S3:
   ```sh
   aws --endpoint-url http://minio:9000 s3 cp s3://respaldosbd/mongodb/<archivo>.archive.gz /backups/restore.archive.gz
   ```
2. Restauración hacia una base de datos o en la base principal con `--drop`:
   ```sh
   mongorestore --host mongodb --port 27017 -u admin -p Mongo123 --authenticationDatabase admin --archive=/backups/restore.archive.gz --gzip --nsInclude="campuscloud.*"
   ```

### 4.2 Restauración de SQL Server 2025
1. Descarga del archivo `.bak` desde S3 hacia `/sqlserver-backups/`:
   ```sh
   aws --endpoint-url http://minio:9000 s3 cp s3://respaldosbd/sqlserver/<archivo>.bak /sqlserver-backups/restore.bak
   ```
2. Restauración con `sqlcmd`:
   ```sh
   /opt/mssql-tools18/bin/sqlcmd -S sqlserver -U sa -P 'SqlServer2025!Campus' -C -Q "
   RESTORE DATABASE CampusCloudDB FROM DISK = '/var/opt/mssql/backup/restore.bak' WITH REPLACE;
   "
   ```
