from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Ticket(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    titulo: str = Field(default="")
    descripcion: str = Field(default="")
    estado: str = Field(default="Abierto")
    prioridad: str = Field(default="Baja")
    fecha_creacion: datetime = Field(default=datetime.now())
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    
class CrearTicket(SQLModel):
    titulo: str
    descripcion: str
    estado: str = Field(default="Abierto")
    prioridad: str = Field(default="Baja")
    
class ActualizarTicket(SQLModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    
class InfoTicket(SQLModel):
    id: int
    id_usuario: int
    titulo: str
    descripcion: str
    estado: str
    prioridad: str
    fecha_creacion: datetime
    model_config = {"from_attributes": True}