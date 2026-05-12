from datetime import datetime
from enum import Enum
from pydantic import EmailStr
from sqlmodel import Field, SQLModel

class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"
    superuser = "superuser"

class Usuario(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre_usuario: str = Field(default="")
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str = Field(min_length=4, max_length=15)
    rol: RoleEnum = Field(default=RoleEnum.user)
    fecha_creacion: datetime = Field(default=datetime.now())
    
class CrearUsuario(SQLModel):
    nombre_usuario: str = Field(default="")
    email: EmailStr 
    hashed_password: str = Field(min_length=4, max_length=15)
    
class ActualizarUsuario(SQLModel):
    nombre_usuario: str 
    
class InfoUsuario(SQLModel):
    id: int
    nombre_usuario: str 
    email: EmailStr 
    rol: RoleEnum
    fecha_creacion: datetime
    model_config = {"from_attributes": True}
    
class ActualizarRol(SQLModel):
    rol: RoleEnum
    
    