import datetime
from sqlmodel import Field, SQLModel

class Ticket(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    titulo: str = Field(default="")
    descripcion: str = Field(default="")
    estado: str = Field(default="Abierto")
    prioridad: str = Field(default="Baja")
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    
class CrearTicket(SQLModel):
    id_usuario: int
    titulo: str
    descripcion: str
    estado: str
    prioridad: str
    
class ActualizarTicket(SQLModel):
    titulo: str
    descripcion: str
    estado: str
    prioridad: str
    
class InfoTicket(SQLModel):
    id: int
    titulo: str
    descripcion: str
    estado: str
    prioridad: str
    model_config = {"from_attributes": True}