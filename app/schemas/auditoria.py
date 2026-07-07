from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict


class InformacionAuditoria(BaseModel):
    entidad: str
    id_entidad: int
    id_usuario: int
    id_usuario_compartido: int | None = None
    campo_cambiado: str
    fecha_cambio: datetime
    valor_anterior: str | None = None
    valor_nuevo: str | None = None
    accion: str
    model_config = ConfigDict(from_attributes = True)
    
class FiltroAuditoria(BaseModel):
    entidad: Optional[str] = None
    id_entidad: Optional[int] = None
    id_usuario: Optional[int] = None
    campo_cambiado: Optional[str] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    accion: Optional[str] = None
    orden: Literal["id", "id_entidad", "id_usuario", "fecha_cambio"] = "id"
    direccion: Literal["asc", "desc"] = "asc"
    
class PaginacionAuditoria(BaseModel):
    total: int
    total_paginas: int
    pagina_actual: int
    tiene_anterior: bool
    tiene_siguiente: bool
    buscar: Optional[str] = None
    items: List[InformacionAuditoria]