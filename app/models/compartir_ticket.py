from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class TicketCompartir(SQLModel, table=True):
    __tablename__ = "ticket_compartir"
    id: Optional[int] = Field(default=None, primary_key=True) #int
    id_ticket: int = Field(foreign_key="ticket.id", index=True)
    id_usuario_origen: int = Field(foreign_key="usuario.id", index=True)
    id_usuario_destino: int = Field(gt=0)
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    
