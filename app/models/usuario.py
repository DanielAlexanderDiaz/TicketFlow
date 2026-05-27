from datetime import datetime
from sqlalchemy import JSON
from app.core.seguridad import RoleUser
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Column


class Usuario(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre_usuario: str = Field(default="")
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str = Field(min_length=4, max_length=15)
    rol: RoleUser = Field(default=RoleUser.USER)
    fecha_creacion: datetime = Field(default=datetime.now())
    activo: bool = Field(default=True)
    imagen_url: str = Field(default="")
    permiso_extra: list[str] = Field(default=list, sa_column=Column(JSON))
    

    