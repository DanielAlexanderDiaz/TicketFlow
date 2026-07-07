from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
    

class CompartirTicket(BaseModel):
    id_usuario_destino: int
    
class InformacionCompartir(BaseModel):
    id_ticket: int | None = None
    id_usuario_origen: int | None = None
    id_usuario_destino: int | None = None
    model_config = ConfigDict(from_attributes=True)
    
class FiltroCompartir(BaseModel):
    id_ticket: Optional[int] = None
    id_usuario_origen: Optional[int] = None
    id_usuario_destino: Optional[int] = None
    fecha_creacion: Optional[datetime] = None
    orden: Literal["id", "id_usuario_origen","id_usuario_destino", "fecha_creacion"] = "id"
    direccion: Literal["asc", "desc"] = "asc"
    
class PaginacionCompartir(BaseModel):
    total: int
    total_paginas: int
    pagina_actual: int
    tiene_anterior: bool
    tiene_siguiente: bool
    buscar: Optional[str] = None
    items: list[InformacionCompartir]