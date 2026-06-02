from datetime import datetime
from sqlalchemy import JSON
from app.core.seguridad import RolUsuario
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Column


class Usuario(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre_usuario: str = Field(default="")
    email: EmailStr = Field(index=True, unique=True)
    password: str = Field(min_length=4, max_length=15)
    rol: RolUsuario = Field(default=RolUsuario.USER)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    activo: bool = Field(default=True)
    imagen_url: str = Field(default="")
    permiso: list[str] = Field(default=list, sa_column=Column(JSON))
    

    