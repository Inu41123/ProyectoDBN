# ⏱️ Fase 4: Documentación del Agente de Respaldos (Backup-Scheduler) e Infraestructura Cloud

**Proyecto:** CampusCloud - Infraestructura de Base de Datos en la Nube  
**Equipo 1:** Héctor, Cristian, Elan  
**Entorno:** Docker Desktop (Windows / WSL2)  
**Red interna:** `DoubleCloud-net` (Driver: Bridge)  
**Motores Asignados al Equipo 1:** **Microsoft SQL Server 2025** y **MongoDB 8**  
**Fecha de Implementación:** 23 de Noviembre de 2026  

---

## 1. Resumen de los Cambios de Infraestructura

Siguiendo el **Manual Integral de Laboratorio** del docente y las especificaciones para el **Equipo 1**:
1. **Eliminación de Duplicati:** Se retiró el contenedor de Duplicati para adoptar una arquitectura nativa Cloud de respaldos desacoplados mediante scripts y CLI.
2. **Motores de Base de Datos Asignados al Equipo 1:**
   - **Microsoft SQL Server 2025 Developer** (`:1434:1433`) - Motor relacional para usuarios, roles y autenticación.
   - **MongoDB 8 Community** (`:27018:27017`) - Motor NoSQL documental para almacenamiento y metadatos de archivos.
3. **Contenedor `backup-scheduler`:** Un agente en Linux (Oracle Linux 9 / RHEL9 base) que centraliza las herramientas cliente oficiales (`mongodump`, `sqlcmd`), el demonio `crond` de tareas programadas y el cliente oficial **AWS CLI v2**.
4. **Volumen Compartido para SQL Server:** Configuración del volumen persistente `sqlserver_backup` montado en `/var/opt/mssql/backup` (en el servidor de SQL Server) y en `/sqlserver-backups` (en el scheduler), permitiendo la lectura directa del archivo `.bak` para su carga a S3.
5. **Configuración Desacoplada con `.env`:** Separación de credenciales, usuarios y parámetros para cumplimiento de buenas prácticas de seguridad.

---

## 2. Directorio de Servicios en Ejecución (Infraestructura Final)

| Servicio | Nombre Contenedor | Imagen | Puerto Host : Contenedor | Propósito |
| :--- | :--- | :--- | :---: | :--- |
| **NGINX** | `DoubleCloud-nginx` | `nginx:alpine` | `8080:80` | Gateway y Proxy Inverso único hacia el backend |
| **API Backend** | `DoubleCloud-api` | `doublecloud-api` | `8000:8000` | Lógica de negocio, CRUD y Swagger en `/docs` |
| **SQL Server** | `DoubleCloud-sqlserver` | `mssql/server:2025-latest` | `1434:1433` | Motor relacional transaccional (Equipo 1) |
| **MongoDB** | `DoubleCloud-mongodb` | `mongo:8` | `27018:27017` | Motor NoSQL documental (Equipo 1) |
| **SILO (S3)** | `DoubleCloud-silo` | `pgsty/silo:latest` | `9000:9000`<br>`9001:9001` | Almacenamiento de objetos S3 (API :9000 / Web :9001) |
| **Scheduler** | `DoubleCloud-backup-scheduler`| `doublecloud-backup-scheduler`| *Red interna* | Cron dominical y ejecución de scripts de backup |

---

## 3. Construcción del `backup-scheduler` (Dockerfile)

Se resolvió la advertencia didáctica del docente referente a la obsolescencia de paquetes RPM directos implementando los repositorios oficiales de MongoDB 8.0 y Microsoft SQL Server Tools para RHEL 9:

```dockerfile
FROM mysql:8.4
USER root
RUN microdnf install -y cronie python3 python3-pip curl ca-certificates tar gzip unzip findutils shadow-utils && microdnf clean all

# MongoDB Database Tools (repo oficial MongoDB 8.0 para RHEL 9 con gpgcheck=0)
RUN printf "[mongodb-org-8.0]\nname=MongoDB Repository\nbaseurl=https://repo.mongodb.org/yum/redhat/9/mongodb-org/8.0/x86_64/\ngpgcheck=0\nenabled=1\n" > /etc/yum.repos.d/mongodb-org-8.0.repo \
 && microdnf install -y mongodb-database-tools && microdnf clean all

# Microsoft SQLCMD 18; repo oficial RHEL9
RUN curl -fsSL https://packages.microsoft.com/config/rhel/9/prod.repo -o /etc/yum.repos.d/mssql-release.repo \
 && ACCEPT_EULA=Y microdnf install -y mssql-tools18 unixODBC && microdnf clean all

# AWS CLI v2 oficial
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
 && unzip -q awscliv2.zip && ./aws/install && rm -rf awscliv2.zip aws

# Creación de directorios de trabajo y ajuste de permisos
RUN mkdir -p /backups /scripts /etc/cron.d /var/log /sqlserver-backups && chmod 777 /backups /sqlserver-backups

COPY scripts/ejecutar-cron.sh /usr/local/bin/ejecutar-cron.sh
RUN chmod +x /usr/local/bin/ejecutar-cron.sh

ENTRYPOINT ["/usr/local/bin/ejecutar-cron.sh"]
```

---

## 4. Tarea Programada (Cron Dominical)

El archivo de configuración cron se ubica en `/etc/cron.d/respaldos`:

```cron
0 2 * * 0 root /scripts/backup-semanal.sh >> /var/log/cron-respaldos.log 2>&1
```

- **Frecuencia:** Cada domingo a las 02:00 hrs CST.
- **Zona Horaria:** Configurada en el contenedor mediante `TZ=America/Mexico_City`.
- **Ejecución Asíncrona:** Demonio `crond -n` en primer plano sin bloquear el contenedor.

---

## 5. Verificación de Operatividad

```powershell
docker compose ps
```
Todos los contenedores se encuentran en estado `Up`, comunicados en la red `doublecloud_DoubleCloud-net`.
