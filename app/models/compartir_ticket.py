from typing import Optional
from pydantic import Field
from sqlmodel import SQLModel

class TicketCompartir(SQLModel, table=True):
    __tablename__ = "ticket_compartir"
    id: Optional[int] = Field(default=None, primary_key=True) #int
    id_ticket: int = Field(foreign_key="ticket.id", index=True)
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    
class solicitudCompartir(SQLModel):
    id_usuario_compartido: int = Field(gt=0)     
