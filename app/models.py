from pydantic import BaseModel, Field
from typing import Optional

# =========================================================================
# MODELOS PARA SQL SERVER (Usuarios de la empresa / institución)
# =========================================================================
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    rol: str = Field(..., min_length=2, max_length=50) # Administrador, Docente, Estudiante
    departamento: Optional[str] = Field("Tecnología", max_length=100)

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    rol: Optional[str] = None
    departamento: Optional[str] = None

class UsuarioOut(UsuarioBase):
    id: int
    fecha_registro: Optional[str] = None


# =========================================================================
# MODELOS PARA MONGODB (Ficheros, documentos y metadatos)
# =========================================================================
class DocumentoBase(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=150)
    tipo_archivo: str = Field(...) # PDF, Excel, Word, Imagen, Código
    categoria: str = Field(...) # Académico, Administrativo, Técnico, Finanzas
    autor_email: str = Field(..., min_length=5, max_length=100)
    descripcion: Optional[str] = Field("", max_length=500)
    tamanio_kb: Optional[float] = Field(1024.0, ge=0)
    file_url: Optional[str] = None
    filename: Optional[str] = None

class DocumentoCreate(DocumentoBase):
    pass

class DocumentoUpdate(BaseModel):
    titulo: Optional[str] = None
    tipo_archivo: Optional[str] = None
    categoria: Optional[str] = None
    autor_email: Optional[str] = None
    descripcion: Optional[str] = None
    tamanio_kb: Optional[float] = None
    file_url: Optional[str] = None
    filename: Optional[str] = None

class DocumentoOut(DocumentoBase):
    id: str
    fecha_subida: Optional[str] = None
