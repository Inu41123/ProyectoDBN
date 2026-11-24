import os
from fastapi import FastAPI, HTTPException, Request, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from database import init_databases, get_sql_connection, get_mongo_collection
from models import (
    UsuarioCreate, UsuarioUpdate, UsuarioOut,
    DocumentoCreate, DocumentoUpdate, DocumentoOut
)

# Asegurar existencia del directorio de uploads
os.makedirs("uploads", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando CampusCloud API y verificando bases de datos...")
    init_databases()
    yield
    print("🛑 Deteniendo CampusCloud API...")

app = FastAPI(
    title="CampusCloud API (Equipo 1)",
    description="API Central Multi-Gestor con SQL Server 2025 y MongoDB 8",
    version="1.0.0",
    lifespan=lifespan
)

# Montaje de archivos estáticos, uploads y plantillas
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

# =========================================================================
# VISTA PRINCIPAL (FRONTEND HTML)
# =========================================================================
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gestores": ["SQL Server 2025", "MongoDB 8"],
        "equipo": ["Héctor", "Cristian", "Elan"]
    }

# =========================================================================
# ENDPOINTS CRUD: SQL SERVER (USUARIOS Y ROLES)
# =========================================================================
@app.get("/api/sql/usuarios", response_model=List[UsuarioOut])
def listar_usuarios(rol: Optional[str] = Query(None, description="Filtrar por rol")):
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()
        if rol:
            cursor.execute("SELECT id, nombre, email, rol, departamento, CONVERT(VARCHAR, fecha_registro, 120) as fecha_registro FROM Usuarios WHERE rol = %s ORDER BY id DESC", (rol,))
        else:
            cursor.execute("SELECT id, nombre, email, rol, departamento, CONVERT(VARCHAR, fecha_registro, 120) as fecha_registro FROM Usuarios ORDER BY id DESC")
        
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en SQL Server: {str(e)}")

@app.get("/api/sql/usuarios/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(usuario_id: int):
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, email, rol, departamento, CONVERT(VARCHAR, fecha_registro, 120) as fecha_registro FROM Usuarios WHERE id = %s", (usuario_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en SQL Server")
        return row
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en SQL Server: {str(e)}")

@app.post("/api/sql/usuarios", response_model=UsuarioOut, status_code=201)
def crear_usuario(usuario: UsuarioCreate):
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM Usuarios WHERE email = %s", (usuario.email,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="El correo ya se encuentra registrado.")

        cursor.execute("""
            INSERT INTO Usuarios (nombre, email, rol, departamento)
            OUTPUT INSERTED.id, INSERTED.nombre, INSERTED.email, INSERTED.rol, INSERTED.departamento, CONVERT(VARCHAR, INSERTED.fecha_registro, 120) as fecha_registro
            VALUES (%s, %s, %s, %s)
        """, (usuario.nombre, usuario.email, usuario.rol, usuario.departamento))
        
        created = cursor.fetchone()
        conn.close()
        return created
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar en SQL Server: {str(e)}")

@app.put("/api/sql/usuarios/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate):
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM Usuarios WHERE id = %s", (usuario_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        updates = []
        params = []
        if datos.nombre is not None:
            updates.append("nombre = %s")
            params.append(datos.nombre)
        if datos.email is not None:
            updates.append("email = %s")
            params.append(datos.email)
        if datos.rol is not None:
            updates.append("rol = %s")
            params.append(datos.rol)
        if datos.departamento is not None:
            updates.append("departamento = %s")
            params.append(datos.departamento)

        if not updates:
            conn.close()
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

        query = f"""
            UPDATE Usuarios
            SET {', '.join(updates)}
            OUTPUT INSERTED.id, INSERTED.nombre, INSERTED.email, INSERTED.rol, INSERTED.departamento, CONVERT(VARCHAR, INSERTED.fecha_registro, 120) as fecha_registro
            WHERE id = %s
        """
        params.append(usuario_id)
        cursor.execute(query, tuple(params))
        updated = cursor.fetchone()
        conn.close()
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar en SQL Server: {str(e)}")

@app.delete("/api/sql/usuarios/{usuario_id}")
def eliminar_usuario(usuario_id: int):
    try:
        conn = get_sql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Usuarios WHERE id = %s", (usuario_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        cursor.execute("DELETE FROM Usuarios WHERE id = %s", (usuario_id,))
        conn.close()
        return {"message": f"Usuario con ID {usuario_id} eliminado exitosamente de SQL Server"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar en SQL Server: {str(e)}")

# =========================================================================
# ENDPOINTS CRUD Y SUBIDA: MONGODB (DOCUMENTOS Y FICHEROS REALES)
# =========================================================================
def doc_to_dict(doc) -> dict:
    return {
        "id": str(doc["_id"]),
        "titulo": doc.get("titulo", ""),
        "tipo_archivo": doc.get("tipo_archivo", ""),
        "categoria": doc.get("categoria", ""),
        "autor_email": doc.get("autor_email", ""),
        "descripcion": doc.get("descripcion", ""),
        "tamanio_kb": doc.get("tamanio_kb", 0.0),
        "file_url": doc.get("file_url", ""),
        "filename": doc.get("filename", ""),
        "fecha_subida": doc.get("fecha_subida", "")
    }

@app.get("/api/mongo/documentos", response_model=List[DocumentoOut])
def listar_documentos(categoria: Optional[str] = Query(None)):
    try:
        col = get_mongo_collection()
        filtro = {"categoria": categoria} if categoria else {}
        cursor = col.find(filtro).sort("_id", -1)
        return [doc_to_dict(d) for d in cursor]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en MongoDB: {str(e)}")

@app.get("/api/mongo/documentos/{doc_id}", response_model=DocumentoOut)
def obtener_documento(doc_id: str):
    try:
        if not ObjectId.is_valid(doc_id):
            raise HTTPException(status_code=400, detail="ID de documento MongoDB inválido")
        col = get_mongo_collection()
        doc = col.find_one({"_id": ObjectId(doc_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado en MongoDB")
        return doc_to_dict(doc)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en MongoDB: {str(e)}")

@app.post("/api/mongo/upload")
async def subir_archivos_mongo(
    files: List[UploadFile] = File(...),
    categoria: str = Form("Académico"),
    autor_email: str = Form("hector@campuscloud.edu.mx"),
    descripcion: str = Form("")
):
    try:
        col = get_mongo_collection()
        insertados = []
        for file in files:
            safe_name = os.path.basename(file.filename)
            timestamp = int(datetime.now().timestamp())
            saved_filename = f"{timestamp}_{safe_name}"
            file_path = os.path.join("uploads", saved_filename)

            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            size_kb = round(len(content) / 1024.0, 2)

            ext = safe_name.split(".")[-1].lower() if "." in safe_name else ""
            if ext in ["pdf"]:
                tipo = "PDF"
            elif ext in ["xlsx", "xls", "csv"]:
                tipo = "Excel"
            elif ext in ["docx", "doc"]:
                tipo = "Word"
            elif ext in ["png", "jpg", "jpeg", "gif", "webp", "svg"]:
                tipo = "Imagen"
            elif ext in ["py", "js", "html", "css", "json", "sql", "sh", "txt"]:
                tipo = "Código/Texto"
            else:
                tipo = "Documento"

            doc_data = {
                "titulo": safe_name,
                "filename": saved_filename,
                "file_url": f"/uploads/{saved_filename}",
                "tipo_archivo": tipo,
                "categoria": categoria,
                "autor_email": autor_email,
                "descripcion": descripcion or f"Archivo real {safe_name} cargado al sistema.",
                "tamanio_kb": size_kb,
                "fecha_subida": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            res = col.insert_one(doc_data)
            doc_data["_id"] = res.inserted_id
            insertados.append(doc_to_dict(doc_data))

        return {
            "message": f"{len(insertados)} archivo(s) procesado(s) y guardado(s) exitosamente en MongoDB.",
            "documentos": insertados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo a MongoDB: {str(e)}")

@app.post("/api/mongo/documentos", response_model=DocumentoOut, status_code=201)
def crear_documento(doc: DocumentoCreate):
    try:
        col = get_mongo_collection()
        doc_data = doc.model_dump()
        doc_data["fecha_subida"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res = col.insert_one(doc_data)
        doc_data["_id"] = res.inserted_id
        return doc_to_dict(doc_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar en MongoDB: {str(e)}")

@app.put("/api/mongo/documentos/{doc_id}", response_model=DocumentoOut)
def actualizar_documento(doc_id: str, datos: DocumentoUpdate):
    try:
        if not ObjectId.is_valid(doc_id):
            raise HTTPException(status_code=400, detail="ID de documento MongoDB inválido")
        
        updates = {k: v for k, v in datos.model_dump().items() if v is not None}
        if not updates:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

        col = get_mongo_collection()
        res = col.find_one_and_update(
            {"_id": ObjectId(doc_id)},
            {"$set": updates},
            return_document=True
        )
        if not res:
            raise HTTPException(status_code=404, detail="Documento no encontrado en MongoDB")
        return doc_to_dict(res)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar en MongoDB: {str(e)}")

@app.delete("/api/mongo/documentos/{doc_id}")
def eliminar_documento(doc_id: str):
    try:
        if not ObjectId.is_valid(doc_id):
            raise HTTPException(status_code=400, detail="ID de documento MongoDB inválido")
        col = get_mongo_collection()
        doc = col.find_one({"_id": ObjectId(doc_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Documento no encontrado en MongoDB")
        
        # Eliminar archivo físico si existe
        if doc.get("filename"):
            local_path = os.path.join("uploads", doc["filename"])
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                except Exception:
                    pass

        col.delete_one({"_id": ObjectId(doc_id)})
        return {"message": f"Documento {doc_id} y archivo físico eliminados exitosamente de MongoDB"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar en MongoDB: {str(e)}")
