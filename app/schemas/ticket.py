from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.ticket import EstadoTicket, PrioridadTicket


class CrearTicket(BaseModel):
    titulo: str
    descripcion: str
    
class ActualizarTicket(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[EstadoTicket] = None
    prioridad: Optional[PrioridadTicket] = None
    
class ActualizarTickekActivo(BaseModel):
    activo: bool
    
class InfoTicket(BaseModel):
    id: int
    id_usuario: int
    titulo: str
    descripcion: str
    estado: EstadoTicket
    prioridad: PrioridadTicket
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = ConfigDict(from_attributes = True)
    
class HistorialTicket(BaseModel):
    id: int
    id_ticket: int
    id_usuario: int
    id_usuario_compartido: int | None = None 
    campo_cambiado: str
    fecha_cambio: datetime
    valor_anterior: str | None = None
    valor_nuevo: str | None = None
    accion: str
    model_config = ConfigDict(from_attributes = True)