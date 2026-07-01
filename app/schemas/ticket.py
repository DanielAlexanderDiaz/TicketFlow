from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict
from fastapi import UploadFile
from app.models.ticket import EstadoTicket, PrioridadTicket


class CrearTicket(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    
class ActualizarTicket(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: Optional[PrioridadTicket] = None
    
class EliminarTicket(BaseModel):
    id_ticket: int
    
class CambioEstadoTicket(BaseModel):
    estado: EstadoTicket

class AsignarTicket(BaseModel):
    id_usuario_asignado: int
    
class TicketActivo(BaseModel):
    activo: bool
    
class InformacionTicket(BaseModel):
    id: int
    id_usuario_creador: int
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
    total: int
    total_paginas: int
    tiene_anterior: bool
    tiene_siguiente: bool
    orden: Literal["id", "titulo"]
    direccion: Literal["asc", "desc"]
    buscar: Optional[str] = None
    items: List[InformacionTicket]