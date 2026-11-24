# 🌐 Fase 3: Documentación de Enrutamiento y Proxy Inverso con NGINX

**Proyecto:** CampusCloud - Infraestructura de Base de Datos en la Nube  
**Equipo 1:** Héctor, Cristian, Elan  
**Servicio Gateway:** NGINX 1.31 (Alpine Linux)  
**Puerto Externo (Host):** `:8080` (Mapeado al puerto `:80` interno del contenedor)  
**Fecha de Implementación:** 18 de Noviembre de 2026  

---

## 1. Justificación y Propósito Arquitectónico

En una arquitectura de nube empresarial, los usuarios y clientes externos **nunca deben interactuar directamente con los servicios internos ni con las bases de datos**. 

NGINX actúa como un **API Gateway y Reverse Proxy**:
1. **Punto único de entrada:** Todo el tráfico HTTP de la organización entra exclusivamente por el puerto `:8080`.
2. **Aislamiento de red:** La API central (`DoubleCloud-api:8000`), SQL Server (`1433`) y MongoDB (`27017`) operan protegidos dentro de la red interna `DoubleCloud-net`.
3. **Soporte de Carga Pesada:** Configuración de `client_max_body_size 100M` para permitir la carga fluida de PDFs y ficheros empresariales sin bloqueos.
4. **Preservación de Identidad:** Reenvío de cabeceras (`X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`, `Host`) para que el backend conozca la procedencia de cada solicitud.

---

## 2. Mapa de Rutas Gestionadas por NGINX

| Ruta Externa (Navegador / Cliente) | Destino Interno (Upstream) | Descripción | Código HTTP Verificado |
| :--- | :--- | :--- | :---: |
| **`http://localhost:8080/`** | `http://api:8000/` | Interfaz Web Principal (Panel Multi-Gestor) | `200 OK` |
| **`http://localhost:8080/api/...`** | `http://api:8000/api/...` | Endpoints REST de SQL Server y MongoDB | `200 OK` |
| **`http://localhost:8080/docs`** | `http://api:8000/docs` | Documentación Interactiva Swagger UI | `200 OK` |
| **`http://localhost:8080/openapi.json`** | `http://api:8000/openapi.json` | Esquema OpenAPI estándar de la API | `200 OK` |
| **`http://localhost:8080/uploads/...`** | `http://api:8000/uploads/...` | Visor y descarga de ficheros reales de MongoDB | `200 OK` |
| **`http://localhost:8080/static/...`** | `http://api:8000/static/...` | Recursos estáticos (CSS, JS) | `200 OK` |

---

## 3. Configuración Técnica Implementada (`nginx.conf`)

```nginx
events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;

    # Permitir subida de archivos grandes (PDFs, imágenes, etc.) hasta 100MB
    client_max_body_size 100M;

    # Definición del upstream hacia la API central
    upstream backend_api {
        server api:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # 1. Enrutamiento de la API REST
        location /api/ {
            proxy_pass http://backend_api/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_read_timeout 300s;
        }

        # 2. Enrutamiento de Documentación Interactiva (Swagger UI)
        location /docs {
            proxy_pass http://backend_api/docs;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /openapi.json {
            proxy_pass http://backend_api/openapi.json;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 3. Enrutamiento de Archivos Subidos y Previsualizaciones
        location /uploads/ {
            proxy_pass http://backend_api/uploads/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 4. Enrutamiento de Recursos Estáticos
        location /static/ {
            proxy_pass http://backend_api/static/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 5. Frontend Web / Raíz
        location / {
            proxy_pass http://backend_api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
}
```

---

## 4. Evidencias de Pruebas de Enrutamiento

Se ejecutó un script de verificación automatizado enviando peticiones directas a través de NGINX (`:8080`) a todas las rutas configuradas:

```powershell
$routes = @("/", "/api/health", "/api/sql/usuarios", "/api/mongo/documentos", "/docs", "/openapi.json");
foreach ($r in $routes) {
    $code = curl.exe -s -o nul -w "%{http_code}" "http://localhost:8080$r";
    Write-Output "Route $r -> HTTP $code"
}
```

### Salida del Servidor:
```text
Route /                   -> HTTP 200
Route /api/health         -> HTTP 200
Route /api/sql/usuarios   -> HTTP 200
Route /api/mongo/documentos -> HTTP 200
Route /docs               -> HTTP 200
Route /openapi.json       -> HTTP 200
```

Todas las rutas respondieron con éxito rotundo (`HTTP 200`), confirmando la correcta comunicación entre NGINX y el contenedor del backend dentro de la red interna de Docker.
