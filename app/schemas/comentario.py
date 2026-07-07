from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict


class CrearComentario(BaseModel):
    comentario: str
    
class ActualizarComentario(BaseModel):
    comentario: str
    
class EliminarComentario(BaseModel):
    id_comentario: int
    
class InformacionComentario(BaseModel):
    id: int
    id_ticket: int
    id_usuario: int
    comentario: str
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    model_config = ConfigDict(from_attributes = True)
    
class FiltroComentario(BaseModel):
    id_ticket: Optional[int] = None
    id_usuario: Optional[int] = None
    comentario: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    orden: Literal["id", "id_ticket","id_usuario", "fecha_creacion", "fecha_actualizacion"] = "id"
    direccion: Literal["asc", "desc"] = "asc"
    
class PaginacionComentario(BaseModel):
    total: int
    total_paginas: int
    pagina_actual: int
    tiene_anterior: bool
    tiene_siguiente: bool
    buscar: Optional[str] = None
    items: List[InformacionComentario]