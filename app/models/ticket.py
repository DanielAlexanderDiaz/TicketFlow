from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class EstadoTicket(str, Enum):
    pendiente = "Pendiente"
    en_progreso = "En progreso"
    finalizado = "Finalizado"
    
class PrioridadTicket(str, Enum):
    baja = "Baja"
    media = "Media"
    alta = "Alta"

class Ticket(SQLModel, table=True):
    __tablename__ = "ticket"
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str 
    descripcion: str 
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    estado: EstadoTicket = Field(default=EstadoTicket.pendiente)
    prioridad: PrioridadTicket = Field(default=PrioridadTicket.baja)
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    
class CrearTicket(SQLModel):
    titulo: str
    descripcion: str
    
class ActualizarTicket(SQLModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[EstadoTicket] = None
    prioridad: Optional[PrioridadTicket] = None
    
class InfoTicket(SQLModel):
    id: int
    id_usuario: int
    titulo: str
    descripcion: str
    estado: EstadoTicket
    prioridad: PrioridadTicket
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = {"from_attributes": True}
    
    