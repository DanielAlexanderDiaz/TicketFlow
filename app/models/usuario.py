from pydantic import EmailStr
from sqlmodel import Field, SQLModel

class Usuario(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nombre_usuario: str = Field(default="")
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str = Field(min_length=4, max_length=15)
 
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
    model_config = {"from_attributes": True}