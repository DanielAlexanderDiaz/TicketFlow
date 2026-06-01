from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.core.seguridad import RolUsuario

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72, description="Contraseña en texto plano")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class ActualizarUsuario(BaseModel):
    nombre_usuario: Optional[str]
    imagen_url: Optional[str]
    
class EliminarUsuario(BaseModel):
    id: int

class ActualizarRol(BaseModel):
    rol: RolUsuario
    
class ActualizarPermisos(BaseModel):
    permiso: list[str]
    
class UsuarioActivo(BaseModel):
    activo: bool

class InformacionUsuario(BaseModel):
    id: int
    nombre_usuario: str
    email: EmailStr
    rol: RolUsuario
    fecha_creacion: datetime
    imagen_url: str = ""
    activo: bool
    permiso: list[str] = Field(default=list)
    model_config = ConfigDict(from_attributes = True)
    
