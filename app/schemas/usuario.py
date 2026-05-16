from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.core.seguridad import RoleUser


class CrearUsuario(BaseModel):
    nombre_usuario: str = Field(default="")
    email: EmailStr 
    hashed_password: str = Field(min_length=4, max_length=15)
    
class ActualizarUsuario(BaseModel):
    nombre_usuario: str 
    
class InfoUsuario(BaseModel):
    id: int
    nombre_usuario: str 
    email: EmailStr 
    rol: RoleUser
    fecha_creacion: datetime
    model_config = ConfigDict(from_attributes = True)
    
class ActualizarRol(BaseModel):
    rol: RoleUser
    