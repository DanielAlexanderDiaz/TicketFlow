from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Auditoria(SQLModel, table=True):
    __tablename__ = "auditoria"
    id: Optional[int] = Field(default=None, primary_key=True)
    entidad: str
    id_entidad: int 
    id_usuario: int = Field(foreign_key="usuario.id", index=True)
    id_usuario_compartido: Optional[int] = Field(default=None) 
    campo_cambiado: str = Field(default="")
    fecha_cambio: datetime = Field(default_factory=datetime.now)
    valor_anterior: str | None = Field(default=None)
    valor_nuevo: str | None = Field(default=None)
    accion: str = Field(default="")