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
    
class FiltrosTicket(BaseModel):
    # Busqueda - Coincidencia parcial
    buscar_titulo: Optional[str] = None
    buscar_descripcion: Optional[str] = None
    # Filtros
    id_ticket: Optional[int] = None
    prioridad: Optional[PrioridadTicket] = None
    estado: Optional[EstadoTicket] = None
    asignado: Optional[int] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    # Ordenamiento
    orden: Literal["id", "titulo","prioridad", "estado", "fecha_creacion"] = "id"
    direccion: Literal["asc", "desc"] = "asc"
    
    
class PaginacionTicket(BaseModel):
    total: int
    total_paginas: int
    pagina_actual: int
    tiene_anterior: bool
    tiene_siguiente: bool
    buscar: Optional[str] = None
    items: List[InformacionTicket]