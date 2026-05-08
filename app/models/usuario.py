import datetime
from pydantic import EmailStr
from sqlmodel import Field, SQLModel

class Usuario(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre_usuario: str = Field(default="")
    email: EmailStr = Field(unique=True)
    hashed_password: str = Field(min_length=4, max_length=15)
    fecha_creacion = datetime.datetime.now()
 
class CrearUsuario(SQLModel):
    email: EmailStr = Field(unique=True)
    hashed_password: str = Field(min_length=4, max_length=15)
    
class InfoUsuario(SQLModel):
    id: int
    nombre_usuario: str 
    email: EmailStr 
    fecha_creacion = datetime.datetime.now()
    model_config = {"from_attributes": True}