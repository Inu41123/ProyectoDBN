# 📋 Checklist Global del Proyecto: CampusCloud (Equipo 1)

**Integrantes:** Héctor, Cristian, Elan  
**Materia:** Base de Datos en la Nube  
**Ponderación:** 60% Infraestructura y CRUD + 40% Reporte / Exposición  
**Gestores Asignados al Equipo 1:** **Microsoft SQL Server 2025** y **MongoDB 8**  
**Almacenamiento S3:** SILO (`pgsty/silo:latest`) con bucket `respaldosbd`  
**Agente de Respaldos:** Contenedor `backup-scheduler` (Linux crond + AWS CLI v2)  
**Gateway:** NGINX (Reverse Proxy :8080)  
**Red interna:** `DoubleCloud-net`  

---

## 🚦 Estado General por Fases

| Fase | Descripción | Estado | Documento de Detalle |
| :--- | :--- | :---: | :--- |
| **Fase 1** | **Infraestructura Base y Orquestación Docker** | ✅ **Completada** | [FASE1_INFRAESTRUCTURA.md](file:///c:/DoubleCloud/docs/FASE1_INFRAESTRUCTURA.md) |
| **Fase 2** | **Aplicación Web y Endpoints CRUD (Python)** | ✅ **Completada** | [FASE2_CRUD_API.md](file:///c:/DoubleCloud/docs/FASE2_CRUD_API.md) |
| **Fase 3** | **Enrutamiento NGINX y Consumo API** | ✅ **Completada** | [FASE3_NGINX_PROXY.md](file:///c:/DoubleCloud/docs/FASE3_NGINX_PROXY.md) |
| **Fase 4** | **Adaptación de Infraestructura y Agente Backup-Scheduler** | ✅ **Completada** | [FASE4_SCHEDULER_INFRA.md](file:///c:/DoubleCloud/docs/FASE4_SCHEDULER_INFRA.md) |
| **Fase 5** | **Pipeline a SILO S3, Automatización Cron y Restauración** | ✅ **Completada** | [FASE5_RESPALDOS_S3.md](file:///c:/DoubleCloud/docs/FASE5_RESPALDOS_S3.md) |
| **Fase 6** | **Guía Maestra de Exposición para el Equipo ("Aprobar sin Reporte")** | ✅ **Completada** | [FASE6_GUIA_EXPOSICION.md](file:///c:/DoubleCloud/docs/FASE6_GUIA_EXPOSICION.md) |

---

## 📌 Desglose Detallado de Tareas

### ✅ Fase 1: Infraestructura Base y Orquestación Docker
- [x] Configuración inicial de red y gestores.
- [x] Creación de carpetas de volúmenes persistentes.
- [x] Verificación de salud y conectividad de los primeros contenedores.

---

### ✅ Fase 2: Aplicación Web y Endpoints CRUD (Python)
- [x] Modelado de datos e inicialización automática (SQL Server `Usuarios` y MongoDB `documentos`).
- [x] Seeding de datos del Equipo 1 (Héctor, Cristian, Elan) al arrancar.
- [x] Endpoints REST en FastAPI con validaciones Pydantic.
- [x] Interfaz Web responsiva (Bootstrap 5 en `:8080`) con subida real de ficheros y visor integrado (PDFs/Imágenes).
- [x] Pruebas completas de los 4 métodos HTTP (CRUD) en ambos motores verificadas.

---

### ✅ Fase 3: Enrutamiento NGINX y Consumo API
- [x] Configuración de Proxy Inverso en [nginx.conf](file:///c:/DoubleCloud/nginx/nginx.conf).
- [x] Configuración de `client_max_body_size 100M` para soporte de subida de archivos pesados.
- [x] Mapeo de rutas para Frontend (`/`), API REST (`/api/`), uploads (`/uploads/`) y assets (`/static/`).
- [x] Integración de documentación interactiva Swagger UI (`/docs`).
- [x] Verificación de todas las rutas a través del puerto `:8080` (HTTP 200 OK).

---

### ✅ Fase 4: Adaptación de Infraestructura y Agente Backup-Scheduler
- [x] Eliminación limpia de Duplicati según la nueva directriz docente.
- [x] Aislamiento exclusivo de los motores asignados al Equipo 1: SQL Server 2025 y MongoDB 8.
- [x] Construcción del Dockerfile de `backup-scheduler` con repositorios oficiales de RHEL 9.
- [x] Configuración del volumen compartido `sqlserver_backup` entre SQL Server y el scheduler.
- [x] Implementación del archivo `.env` desacoplado para seguridad.
- [x] Verificación de clientes CLI (`mongodump`, `sqlcmd`, `aws cli v2`).

---

### ✅ Fase 5: Pipeline a SILO S3, Automatización Cron y Restauración
- [x] Creación del bucket `respaldosbd` en SILO S3.
- [x] Scripts individuales `backup-mongodb.sh` y `backup-sqlserver.sh`.
- [x] Orquestador `backup-semanal.sh` con control de concurrencia y verificación de integridad (`CHECKSUM` y `RESTORE VERIFYONLY`).
- [x] Demostración de subida automática a `s3://respaldosbd/` (salida 0 errores).
- [x] Limpieza de objetos huérfanos y verificación de solo `mongodb/` y `sqlserver/` en S3.
- [x] Procedimiento documentado y validado de Disaster Recovery (Restauración).
