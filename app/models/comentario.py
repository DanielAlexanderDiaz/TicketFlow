from datetime import datetime
from sqlmodel import Field, SQLModel

class Comentario(SQLModel, table=True):
    __tablename__ = "comentario"
    id: int = Field(default=None, primary_key=True)
    id_ticket: int = Field(foreign_key="ticket.id", index=True)
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    comentario: str
    fecha_creacion: datetime = Field(default=datetime.now())
    
