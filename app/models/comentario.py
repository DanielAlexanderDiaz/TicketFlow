import datetime
from sqlmodel import Field, SQLModel

class ComentarioTicket(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    id_ticket: int = Field(foreign_key="ticket.id", index=True)
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    comentario: str
    fecha_creacion = datetime.datetime.now()
    
class CrearComentarioTicket(SQLModel):
    id_ticket: int
    id_usuario: int
    comentario: str
    fecha_creacion = datetime.datetime.now()
    
class InfoComentarioTicket(SQLModel):
    id: int
    id_ticket: int
    id_usuario: int
    comentario: str
    fecha_creacion = datetime.datetime.now()
    model_config = {"from_attributes": True}
    
    