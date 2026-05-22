from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.core.seguridad import RoleUser

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72, description="Contraseña en texto plano")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CrearUsuario(BaseModel):
    nombre_usuario: str = Field(default="")
    email: EmailStr 
    hashed_password: str = Field(min_length=6, max_length=72, description="Contraseña en texto plano")
    
class ActualizarUsuario(BaseModel):
    nombre_usuario: str 
    imagen_url: str

class ActualizarRol(BaseModel):
    rol: RoleUser
    
class ActualizarEstado(BaseModel):
    activo: bool
    
class InfoUsuario(BaseModel):
    id: int
    nombre_usuario: str 
    email: EmailStr 
    rol: RoleUser
    fecha_creacion: datetime
    model_config = ConfigDict(from_attributes = True)
    
