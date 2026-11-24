# 🎓 Fase 6: Guía Maestra de Exposición del Equipo 1 ("Aprobar sin Reporte")

**Proyecto:** CampusCloud / DoubleCloud - Infraestructura de Base de Datos en la Nube  
**Equipo 1:** Héctor, Cristian, Elan  
**Objetivo de la Fase:** Coordinación técnica total del equipo para dominar la presentación en vivo, responder preguntas trampa del docente, ejecutar comandos en terminal con seguridad absoluta y demostrar trabajo en equipo sin riesgos de caída de la infraestructura.  

---

## 🎭 1. Distribución Estratégica de Roles

Para que el profesor vea dominio técnico homogéneo y que cada quien construyó su parte:

```
+───────────────────────────────────────────────────────────────────────────────+
|                               EQUIPO 1 - ROLES                                |
+───────────────────────────────────┬───────────────────────────────────────────+
| HÉCTOR                            | CRISTIAN                                  | ELAN                                      |
| LÍDER DE INFRAESTRUCTURA & PROXY  | ARQUITECTURA DE DATOS & API               | INGENIERO DE RESPALDOS & CLOUD STORAGE    |
+───────────────────────────────────┼───────────────────────────────────────────┼───────────────────────────────────────────+
| • Orquestación Docker Compose     | • API Central FastAPI                     | • Agente `backup-scheduler`               |
| • Proxy Inverso NGINX (:8080)     | • SQL Server 2025 (Usuarios y Roles)      | • Tareas Crond & Automatización           |
| • Redes, Volúmenes y Seguridad    | • MongoDB 8 (Documentos y Archivos)       | • Pipeline a SILO S3 (Bucket respaldosbd) |
| • Demo del Dashboard Web          | • Documentación Swagger UI (/docs)        | • Procedimiento de Restauración           |
+───────────────────────────────────┴───────────────────────────────────────────┴───────────────────────────────────────────+
```

---

## 🎬 2. Guión de la Demostración en Vivo (Paso a Paso en 7 Minutos)

Sigan este orden exacto durante la presentación. Es fluido, visual y contundente:

### Paso 1: Héctor abre la presentación (Infraestructura viva)
1. Abre la terminal de PowerShell en `c:\DoubleCloud`.
2. Ejecuta el comando de verificación:
   ```powershell
   docker compose ps
   ```
3. **Qué decir:**
   > *"Profesor, aquí tenemos la infraestructura completa orquestada con Docker Compose en una red interna aislada. Tenemos 6 servicios activos: nuestro proxy NGINX como único punto de entrada público en el puerto 8080, nuestra API central en Python, los dos motores asignados a nuestro equipo (SQL Server 2025 y MongoDB 8), el almacenamiento de objetos SILO compatible con S3 y nuestro agente Linux de respaldos automatizados."*

---

### Paso 2: Cristian muestra la API y la persistencia de datos
1. Abre el navegador en `http://localhost:8080/`.
2. Muestra el **Dashboard Web**:
   - En la sección **SQL Server**: Muestra la tabla de usuarios registrados (con los nombres de Héctor, Cristian y Elan ya sembrados). Agrega un nuevo usuario de prueba frente al profesor.
   - En la sección **MongoDB**: Sube un documento (un PDF o una imagen pequeña). Muestra que se guarda con su hash, tipo MIME y fecha, y dale clic a **"Ver Documento"** para que se abra en el navegador.
3. Abre una pestaña en `http://localhost:8080/docs` (Swagger UI).
4. **Qué decir:**
   > *"Nuestra API central fue construida con FastAPI bajo estándares OpenAPI. Manejamos un enfoque políglota de persistencia: datos transaccionales de usuarios y accesos residen en SQL Server 2025 relacional con integridad referencial, mientras que los metadatos y el almacenamiento de archivos documentales se gestionan en MongoDB 8 NoSQL. El proxy NGINX redirige el tráfico y nos permite soportar archivos de hasta 100 MB."*

---

### Paso 3: Elan demuestra los respaldos en SILO S3
1. Abre el navegador en la consola de SILO: `http://localhost:9001`.
   - **Usuario:** `minioadmin`
   - **Contraseña:** `CampusCloud2025!`
2. Entra a **Buckets** -> `respaldosbd`. Muestra las carpetas `mongodb/` y `sqlserver/`.
3. Vuelve a la terminal y ejecuta el respaldo en vivo frente al docente:
   ```powershell
   docker exec DoubleCloud-backup-scheduler sh /scripts/backup-semanal.sh
   ```
4. Muestra la salida con `FIN: ... errores=0`.
5. Regresa a SILO y refresca la página: el nuevo archivo `.archive.gz` y el archivo `.bak` aparecen con la hora exacta recién creada.
6. **Qué decir:**
   > *"Para el sistema de respaldos eliminamos intermediarios pesados y construimos un agente dedicado en Linux con el demonio crond programado cada domingo a las 2:00 AM CST. Este contenedor ejecuta scripts desacoplados usando las herramientas oficiales mongodump y sqlcmd, verifica la integridad del respaldo con CHECKSUM y RESTORE VERIFYONLY, y finalmente transfiere los artefactos cifrados directamente a SILO mediante el cliente oficial AWS CLI v2."*

---

## 🛡️ 3. "Cheat Sheet": Comandos 100% Seguros para Terminal

Si el profesor les dice: *"A ver tú, pásale y ejecútame comandos en la terminal para ver si de verdad lo hiciste"*, **SOLO USEN ESTOS COMANDOS**. Son 100% informativos, nunca tiran ningún servicio y demuestran conocimiento profesional.

| Objetivo | Comando a escribir | Qué esperar / Explicación |
| :--- | :--- | :--- |
| **Ver estado de los servicios** | `docker compose ps` | Muestra los 6 contenedores en estado `Up` con sus puertos. |
| **Ver logs del Proxy NGINX** | `docker logs --tail 25 DoubleCloud-nginx` | Muestra las últimas peticiones HTTP procesadas con código 200. |
| **Ver logs de la API** | `docker logs --tail 25 DoubleCloud-api` | Muestra el log de FastAPI y las conexiones a SQL Server y MongoDB. |
| **Ver logs de SQL Server** | `docker logs --tail 20 DoubleCloud-sqlserver` | Muestra que SQL Server 2025 Developer está escuchando conexiones. |
| **Ver logs de MongoDB** | `docker logs --tail 20 DoubleCloud-mongodb` | Muestra el engine WiredTiger activo y escuchando en el puerto 27017. |
| **Listar respaldos en S3** | `docker exec DoubleCloud-backup-scheduler aws --endpoint-url http://minio:9000 s3 ls s3://respaldosbd/ --recursive --human-readable` | Lista todos los archivos de respaldo en SILO con tamaños legibles (KB / MB). |
| **Ver tarea Cron configurada**| `docker exec DoubleCloud-backup-scheduler cat /etc/cron.d/respaldos` | Muestra la línea del cron: `0 2 * * 0 root /scripts/backup-semanal.sh`. |
| **Ejecutar respaldo manual** | `docker exec DoubleCloud-backup-scheduler sh /scripts/backup-semanal.sh` | Ejecuta el backup completo de Mongo y SQL Server y muestra `errores=0`. |
| **Probar salud de la API** | `curl.exe -s http://localhost:8080/api/health` | Devuelve JSON con los nombres del equipo y estado `"healthy"`. |
| **Entrar a la shell de Mongo** | `docker exec -it DoubleCloud-mongodb mongosh -u admin -p Mongo123 --authenticationDatabase admin --eval "db.adminCommand('ping')"` | Devuelve `{ ok: 1 }` demostrando conexión autenticada a MongoDB. |

---

## ⚠️ 4. Comandos PROHIBIDOS (¡Peligro de Tirar la Infraestructura!)

> [!CAUTION]
> **NUNCA ESCRIBIR ESTOS COMANDOS EN LA EXPOSICIÓN:**
> 1. `docker compose down -v` ❌ -> **¡ELIMINA TODOS LOS VOLÚMENES Y BASES DE DATOS!**
> 2. `docker system prune -a --volumes` ❌ -> **¡BORRA TODO DOCKER DE LA MÁQUINA!**
> 3. `rm -rf /backups/*` o tocar carpetas de volúmenes directamente en Windows.
> 4. Si el profesor pide reiniciar un contenedor, **NUNCA USAR** `docker kill` o `docker rm`.
>    - **Comando correcto y seguro para reiniciar:**  
>      `docker compose restart <nombre_servicio>` (ejemplo: `docker compose restart api`).

---

## 🎯 5. Respuestas a Preguntas Trampa del Docente

Aquí están las preguntas exactas que los profesores de bases de datos y cloud suelen hacer para "agarrar en curva" a los alumnos:

### Pregunta 1: *"¿Por qué crearon un contenedor separado `backup-scheduler` en lugar de programar los respaldos dentro de cada base de datos o en Windows?"*
- **Quién responde:** Elan o Cristian.
- **Respuesta ideal:**
  > *"Por el principio de Separación de Responsabilidades (Separation of Concerns) y portabilidad Cloud. Un contenedor de base de datos debe ser lo más ligero e inmutable posible; instalarle herramientas de AWS CLI, python o demonios de cron aumentaría la superficie de ataque y el peso de la imagen. Al usar un contenedor agente `backup-scheduler`, centralizamos las políticas de backup sin alterar los motores y garantizamos que el sistema funcione igual en Windows, Linux o Kubernetes."*

---

### Pregunta 2: *"¿Por qué implementaron NGINX si la API de Python ya puede recibir peticiones en el puerto 8000?"*
- **Quién responde:** Héctor.
- **Respuesta ideal:**
  > *"Por seguridad y arquitectura perimetral. En producción nunca se expone el servidor de aplicaciones directamente a Internet. NGINX actúa como Reverse Proxy y Gateway: centraliza el punto de entrada en el puerto 8080, gestiona encabezados de seguridad, maneja límites de transferencia como `client_max_body_size 100M` para evitar ataques de denegación por saturación y permite en el futuro agregar terminación SSL/TLS o balanceo de carga sin tocar el código de la API."*

---

### Pregunta 3: *"Si SQL Server corre en un contenedor y el scheduler en otro, ¿cómo hace el scheduler para acceder al archivo `.bak` y subirlo a S3?"*
- **Quién responde:** Cristian o Héctor.
- **Respuesta ideal:**
  > *"A través de un volumen compartido de Docker llamado `sqlserver_backup`. SQL Server por arquitectura genera el archivo `.bak` en su propio sistema de archivos local (`/var/opt/mssql/backup`). Al montar ese mismo volumen dentro del scheduler en `/sqlserver-backups`, el scheduler puede leer el archivo generado, subirlo a S3 con el AWS CLI y luego limpiar el archivo local para no saturar el almacenamiento."*

---

### Pregunta 4: *"¿Cómo verifican que el respaldo que subieron a S3 no esté corrupto?"*
- **Quién responde:** Elan.
- **Respuesta ideal:**
  > *"En el caso de SQL Server, el script no sube el archivo a ciegas: ejecutamos `BACKUP DATABASE ... WITH CHECKSUM` y antes de la subida corremos `RESTORE VERIFYONLY FROM DISK`. Si el checksum o la cabecera del archivo están alterados, el comando falla y se aborta la subida. Para MongoDB, usamos `--archive` con compresión gzip en bloque binario directo desde el stream del socket del motor."*

---

### Pregunta 5: *"¿Qué pasa si se apaga la computadora del servidor de nube a la mitad de la semana? ¿Se borran los datos o el cron?"*
- **Quién responde:** Cualquier integrante.
- **Respuesta ideal:**
  > *"No se pierde absolutamente nada. Los datos de SQL Server, MongoDB y SILO residen en volúmenes Docker gestionados en disco (`sqlserver_data`, `mongodb_data`, `silo_data`). Además, todos los contenedores tienen la directiva `restart: unless-stopped`. Cuando la máquina o el servicio de Docker encienden, los contenedores arrancan en segundo plano, el demonio `crond` se inicializa automáticamente y continúa esperando el día y hora configurados."*

---

## 🏆 6. Plan de Contingencia (¿Qué hacer si algo falla en vivo?)

Si por alguna razón la red se traba o una ventana no carga:

1. **Si una página no carga en el navegador:**
   - Verifica que NGINX esté corriendo: `docker compose ps`.
   - Si se quedó colgada la API, reiníciala elegantemente:
     ```powershell
     docker compose restart api nginx
     ```
2. **Si el comando de backup dice que hay un bloqueo pendiente (`ERROR: respaldo en curso`):**
   - Es el mutex de seguridad. Se desbloquea al instante con:
     ```powershell
     docker exec DoubleCloud-backup-scheduler rmdir /backups/backup-semanal.lock
     ```
3. **Actitud:** Tranquilidad absoluta. Explicar al profesor: *"Estamos ejecutando un reinicio de servicio mediante orquestación para liberar recursos"* demuestra aún más madurez técnica que si todo saliera a la primera.
