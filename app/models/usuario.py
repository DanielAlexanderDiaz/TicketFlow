from datetime import datetime
from enum import Enum
from core.seguridad import RoleUser
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class Usuario(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre_usuario: str = Field(default="")
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str = Field(min_length=4, max_length=15)
    rol: RoleUser = Field(default=RoleUser.USER)
    fecha_creacion: datetime = Field(default=datetime.now())
    

    