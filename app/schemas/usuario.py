from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.core.seguridad import RolUsuario

class Registro(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72, description="Contraseña en texto plano")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72, description="Contraseña en texto plano")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class ActualizarUsuario(BaseModel):
    nombre_usuario: Optional[str] = None
    
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
    permiso: list[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes = True)
    
class FiltrosUsuario(BaseModel):
    buscar_email: Optional[str] = None
    buscar_nombre: Optional[str] = None
    rol: Optional[RolUsuario] = None
    activo: Optional[bool] = None
    orden: Literal["id", "email", "nombre_usuario", "activo"] = "id"
    direccion: Literal["asc", "desc"] = "asc"
    
class PaginacionUsuario(BaseModel):
    total: int
    total_paginas: int
    pagina_actual: int
    tiene_anterior: bool
    tiene_siguiente: bool
    buscar: Optional[str] = None
    items: list[InformacionUsuario]    

    