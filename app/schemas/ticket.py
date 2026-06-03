from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from fastapi import UploadFile
from app.models.ticket import EstadoTicket, PrioridadTicket


class CrearTicket(BaseModel):
    titulo: str
    descripcion: str
    
class ActualizarTicket(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[EstadoTicket] = None
    prioridad: Optional[PrioridadTicket] = None
    imagen_url: Optional[UploadFile] = None
    
class EliminarTicket(BaseModel):
    id_ticket: int
    
class CambioEstadoTicket(BaseModel):
    id_ticket: int
    estado: EstadoTicket

class AsignarTicket(BaseModel):
    id_ticket: int
    id_usuario: int
    
class TicketActivo(BaseModel):
    activo: bool
    
class InformacionTicket(BaseModel):
    id: int
    id_usuario: int
    titulo: str
    descripcion: str
    estado: EstadoTicket
    prioridad: PrioridadTicket
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    asignado: Optional[int]
    activo: bool
    imagen_url: str = ""
    model_config = ConfigDict(from_attributes = True)
    
class PaginacionTicket(BaseModel):
    items: list[InformacionTicket]
    total: int
    page: int
    size: int
    pages: int
    