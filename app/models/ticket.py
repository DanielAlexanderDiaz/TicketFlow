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
    estado: EstadoTicket = Field(default=EstadoTicket.pendiente)
    prioridad: PrioridadTicket = Field(default=PrioridadTicket.baja)
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    
class TicketAuditoria(SQLModel, table=True):
    __tablename__ = "ticket_auditoria"
    id: Optional[int] = Field(default=None, primary_key=True)
    id_ticket: int = Field(foreign_key="ticket.id", index=True)
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    id_usuario_compartido: Optional[int] = Field(default=None)
    campo_cambiado: str = Field(default="")
    fecha_cambio: datetime = Field(default_factory=datetime.now)
    valor_anterior: str | None = Field(default=None)
    valor_nuevo: str | None = Field(default=None)
    accion: str = Field(default="actualizado")
    
