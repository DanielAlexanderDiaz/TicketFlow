from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class EstadoTicket(str, Enum):
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "en_progreso"
    FINALIZADO = "finalizado"
    
class PrioridadTicket(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"

class Ticket(SQLModel, table=True):
    __tablename__ = "ticket"
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    descripcion: str
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_actualizacion: datetime = Field(default_factory=datetime.now)
    estado: EstadoTicket = Field(default=EstadoTicket.PENDIENTE)
    prioridad: PrioridadTicket = Field(default=PrioridadTicket.BAJA)
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    activo: bool = Field(default=True)
    imagen_url: str = Field(default="")

