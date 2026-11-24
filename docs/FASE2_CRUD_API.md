# ⚡ Fase 2: Documentación de la Aplicación Web y API CRUD

**Proyecto:** CampusCloud - Infraestructura de Base de Datos en la Nube  
**Equipo 1:** Héctor, Cristian, Elan  
**Tecnología Backend:** Python 3.11 con FastAPI y Uvicorn  
**Tecnología Frontend:** HTML5, Bootstrap 5 (Dark Theme), Vanilla JavaScript  
**Fecha de Implementación:** 18 de Noviembre de 2026  

---

## 1. Resumen de la Implementación

En esta fase se construyó y validó la aplicación central (`DoubleCloud-api`) que conecta con los dos motores de base de datos asignados al Equipo 1:
1. **SQL Server 2025 (Relacional):** Modelo de **Usuarios y Roles** (Administradores, Docentes, Estudiantes).
2. **MongoDB 8 (NoSQL Documental):** **Cargador de Ficheros y Documentos Reales** con subida múltiple, cálculo automático de tamaño, persistencia en disco/volumen y visor integrado en el navegador (`target="_blank"`).
3. **Panel Web Interactivo:** Servido en `http://localhost:8080/` con interfaz gráfica para ejecutar todas las operaciones CRUD sin necesidad de herramientas externas.
4. **Inicialización y Seeding Automático:** Al arrancar la API, se crea la base de datos `CampusCloudDB` y la colección `documentos`, insertando registros de prueba automáticamente si están vacías.

---

## 2. Modelos de Datos

### A. SQL Server (`Usuarios`)
```sql
CREATE TABLE Usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) NOT NULL UNIQUE,
    rol NVARCHAR(50) NOT NULL,         -- 'Administrador', 'Docente', 'Estudiante'
    departamento NVARCHAR(100) DEFAULT 'Tecnología',
    fecha_registro DATETIME DEFAULT GETDATE()
);
```

### B. MongoDB (`documentos`)
```json
{
  "_id": ObjectId("..."),
  "titulo": "Manual_Sistemas.pdf",
  "filename": "1794983474_Manual_Sistemas.pdf",
  "file_url": "/uploads/1794983474_Manual_Sistemas.pdf",
  "tipo_archivo": "PDF",             // PDF, Excel, Word, Imagen, Código/Texto
  "categoria": "Académico",           // Académico, Administrativo, Técnico, Finanzas
  "autor_email": "hector@campuscloud.edu.mx",
  "descripcion": "Manual de usuario para la entrega de la práctica.",
  "tamanio_kb": 1540.25,
  "fecha_subida": "2026-11-18 06:31:14"
}
```

---

## 3. Catálogo de Endpoints REST

### 🔵 SQL Server (Usuarios)

| Método | Endpoint | Descripción | Body / Query | Código Éxito |
| :---: | :--- | :--- | :--- | :---: |
| **GET** | `/api/sql/usuarios` | Listar usuarios | Query opcional: `?rol=Docente` | `200 OK` |
| **GET** | `/api/sql/usuarios/{id}` | Obtener usuario por ID | Ninguno | `200 OK` |
| **POST** | `/api/sql/usuarios` | Crear nuevo usuario | JSON `{nombre, email, rol, departamento}` | `201 Created` |
| **PUT** | `/api/sql/usuarios/{id}` | Actualizar datos de usuario | JSON con campos a modificar | `200 OK` |
| **DELETE** | `/api/sql/usuarios/{id}` | Eliminar usuario | Ninguno | `200 OK` |

### 🟢 MongoDB (Documentos y Ficheros Reales)

| Método | Endpoint | Descripción | Parámetros / Form | Código Éxito |
| :---: | :--- | :--- | :--- | :---: |
| **GET** | `/api/mongo/documentos` | Listar documentos | Query opcional: `?categoria=Técnico` | `200 OK` |
| **GET** | `/api/mongo/documentos/{id}` | Obtener documento por ID | Ninguno | `200 OK` |
| **POST** | `/api/mongo/upload` | **Subir archivo(s) real(es)** | `multipart/form-data`: `files` (múltiples), `categoria`, `autor_email`, `descripcion` | `200 OK` |
| **PUT** | `/api/mongo/documentos/{id}` | Actualizar metadatos | JSON con campos a modificar | `200 OK` |
| **DELETE** | `/api/mongo/documentos/{id}` | Eliminar documento y archivo físico | Ninguno | `200 OK` |
| **GET** | `/uploads/{filename}` | **Servir archivo para previsualización** | Ruta directa al archivo físico | `200 OK` |

---

## 4. Evidencias de Pruebas CRUD y Subida de Archivos

### Prueba 1: Subida de Archivo Real a MongoDB (`POST /api/mongo/upload`)
* **Petición:** Subida de archivo físico con cálculo automático de tamaño y tipo.
* **Respuesta del Servidor:**
  ```json
  {
    "message": "1 archivo(s) procesado(s) y guardado(s) exitosamente en MongoDB.",
    "documentos": [
      {
        "id": "6afd4632c028899fdb41cc32",
        "titulo": "test_evaluacion.txt",
        "tipo_archivo": "Código/Texto",
        "categoria": "Tecnico",
        "autor_email": "hector@campuscloud.edu.mx",
        "descripcion": "Archivo de prueba para validacion del visor",
        "tamanio_kb": 0.1,
        "file_url": "/uploads/1794983474_test_evaluacion.txt",
        "filename": "1794983474_test_evaluacion.txt",
        "fecha_subida": "2026-11-18 06:31:14"
      }
    ]
  }
  ```

### Prueba 2: Visualización del Archivo a través de NGINX (`GET /uploads/...`)
* **Petición:** `http://localhost:8080/uploads/1794983474_test_evaluacion.txt`
* **Resultado:** Servido con código `200 OK` con contenido íntegro. En caso de PDFs o imágenes, el navegador abre el visor integrado automáticamente.

### Prueba 3: Operaciones CRUD en SQL Server
* Inserción (`POST /api/sql/usuarios`), Consulta (`GET /api/sql/usuarios`), Actualización (`PUT /api/sql/usuarios/4`) y Eliminación (`DELETE /api/sql/usuarios/4`) validadas y documentadas con éxito.

---

## 5. Acceso a la Interfaz Gráfica

* **URL del Panel:** **`http://localhost:8080/`** (a través del Proxy Inverso de NGINX)
* **Pestaña SQL Server:** Gestión de usuarios por roles.
* **Pestaña MongoDB:** 
  - Modal de arrastrar y soltar para subir múltiples archivos reales.
  - Botón **"Ver"** (ojito 👁️) para abrir el documento en una pestaña nueva del navegador.
  - Botón **"Editar"** (lápiz ✏️) para actualizar en vivo el título, categoría, autor o descripción en MongoDB.
  - Botón **"Eliminar"** (papelera 🗑️) para borrar de MongoDB y limpiar el archivo físico del disco.
