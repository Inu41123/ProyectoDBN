# 🏗️ Fase 1: Documentación de Infraestructura y Orquestación Docker

**Proyecto:** CampusCloud - Infraestructura de Base de Datos en la Nube  
**Equipo 1:** Héctor, Cristian, Elan  
**Red Docker:** `DoubleCloud-net` (Driver: Bridge)  
**Fecha de Implementación:** 17 de Noviembre de 2026  

---

## 1. Resumen de la Arquitectura

Se orquestó una infraestructura completa basada en contenedores Docker para soportar:
1. **Dos motores de bases de datos:** SQL Server 2025 (Relacional) y MongoDB 8 (NoSQL Documental).
2. **Una API Central en Python (FastAPI):** Capa lógica de negocio con recarga en vivo de código (`--reload`) mediante volumen montado.
3. **NGINX:** Gateway y Proxy inverso como punto único de entrada web.
4. **SILO (Fork MinIO):** Almacenamiento de objetos compatible con Amazon S3.
5. **Duplicati:** Sistema de respaldos cifrados que versiona y envía los backups al almacenamiento S3.

```
 [Usuario / Navegador]
          │
          ▼ (:8080)
   ┌──────────────┐
   │    NGINX     │
   └──────┬───────┘
          │ (proxy_pass interno a :8000)
          ▼
   ┌──────────────┐
   │  API Python  │ ◄────── Red: DoubleCloud-net ──────► ┌────────────────────┐
   │  (FastAPI)   │                                      │     SILO (S3)      │
   └───┬──────┬───┘                                      │  :9000 (API S3)    │
       │      │                                          │  :9001 (Web Admin) │
       ▼      ▼                                          └─────────▲──────────┘
  ┌────────┐ ┌─────────┐                                           │ (sube backups)
  │  SQL   │ │ MongoDB │                                 ┌─────────┴──────────┐
  │ Server │ │    8    │                                 │     Duplicati      │
  │ :1434  │ │ :27018  │                                 │     (Web :8200)    │
  └───┬────┘ └───┬─────┘                                 └─────────▲──────────┘
      │          │                                                 │
      └────┬─────┘                                                 │ (lee .bak y .gz)
           ▼                                                       │
  [/backups/exportados] ───────────────────────────────────────────┘
```

---

## 2. Directorio de Servicios, Puertos y Credenciales

| Servicio | Contenedor | Imagen | Puerto Host : Puerto Contenedor | Usuario | Contraseña / Key | Propósito |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **NGINX** | `DoubleCloud-nginx` | `nginx:alpine` | `8080:80` | N/A | N/A | Proxy inverso hacia la API central |
| **API Backend** | `DoubleCloud-api` | `doublecloud-api` (local) | `8000:8000` | N/A | N/A | Lógica de negocio y endpoints CRUD |
| **SQL Server** | `DoubleCloud-sqlserver` | `mcr.microsoft.com/mssql/server:2025-latest` | `1434:1433` | `sa` | `SqlServer2025!Campus` | Base de datos relacional (Usuarios/Roles) |
| **MongoDB** | `DoubleCloud-mongodb` | `mongo:8` | `27018:27017` | `admin` | `Mongo123` | Base de datos documental (Ficheros/Docs) |
| **SILO (S3)** | `DoubleCloud-silo` | `pgsty/silo:latest` | `9000:9000`<br>`9001:9001` | `minioadmin` | `CampusCloud2025!` | Puerto 9000: API S3<br>Puerto 9001: Consola Web |
| **Duplicati** | `DoubleCloud-duplicati` | `linuxserver/duplicati:latest` | `8200:8200` | admin (inicial) | Config en Web UI<br>`SETTINGS_ENCRYPTION_KEY`: `CampusCloud2025SecretKey!` | Gestor de respaldos cifrados |

---

## 3. Mapeo de Volúmenes y Carpetas Clave

```
C:\DoubleCloud\
├── app\                    --> Montado en /app (Código fuente de la API Python)
├── nginx\
│   └── nginx.conf          --> Montado en /etc/nginx/nginx.conf (Reglas del proxy inverso)
├── backups\
│   ├── exportados\         --> Montado en /backups/exportados y en /var/opt/mssql/backup (Lectura por Duplicati /source)
│   └── restaurados\        --> Montado en /backups/restaurados (Destino para Duplicati /restore)
├── docs\                   --> Documentación y evidencias
└── docker-compose.yml       --> Manifiesto principal de la infraestructura
```

---

## 4. Validaciones de Salud y Conectividad Ejecutadas

Todos los servicios fueron levantados y verificados:

1. **NGINX -> API Proxy Test:**
   ```powershell
   curl.exe http://localhost:8080/
   # Respuesta: {"message":"Bienvenido a CampusCloud API (Equipo 1)","status":"Online","gestores":["SQL Server 2025","MongoDB 8"]}
   ```
2. **Consola Web de SILO (S3):**
   ```powershell
   curl.exe -I http://localhost:9001/
   # Respuesta: HTTP/1.1 200 OK (MinIO Console activa)
   ```
3. **Consola Web de Duplicati:**
   ```powershell
   curl.exe -I http://localhost:8200/
   # Respuesta: HTTP/1.1 200 OK (Kestrel Server activo)
   ```
4. **Estado de Contenedores (`docker ps`):**
   Todos los 6 contenedores reportan estado `Up` continuo y sin errores de ciclo de vida.
