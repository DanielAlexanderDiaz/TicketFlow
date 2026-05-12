from datetime import datetime
from sqlmodel import Field, SQLModel

class Comentario(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    id_ticket: int = Field(foreign_key="ticket.id", index=True)
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    comentario: str
    fecha_creacion: datetime = Field(default=datetime.now())
    
class CrearComentario(SQLModel):
    comentario: str
    
class ActualizarComentario(SQLModel):
    comentario: str
    
class InfoComentario(SQLModel):
    id: int
    id_ticket: int
    id_usuario: int
    comentario: str
    fecha_creacion: datetime
    model_config = {"from_attributes": True}
    
    