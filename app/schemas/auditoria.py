from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict


class CrearAuditoria(BaseModel):
    entidad: str
    id_entidad: int
    id_usuario: int
    campo_cambiado: str
    fecha_cambio: str
    valor_anterior: str | None = None
    valor_nuevo: str | None = None
    accion: str

class InformacionAuditoria(BaseModel):
    entidad: str
    id_entidad: int
    id_usuario: int
    id_usuario_compartido: int | None = None
    campo_cambiado: str
    fecha_cambio: str
    valor_anterior: str | None = None
    valor_nuevo: str | None = None
    accion: str
    model_config = ConfigDict(from_attributes = True)
    
class FiltroAuditoria(BaseModel):
    entidad: str
    id_entidad: int
    id_usuario: int
    campo_cambiado: str
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    accion: str
    orden: Literal["id", "id_entidad", "id_usuario"] = "id"
    direccion: Literal["asc", "desc"] = "asc"
    
class PaginacionAuditoria(BaseModel):
    total: int
    total_paginas: int
    pagina_actual: int
    tiene_anterior: bool
    tiene_siguiente: bool
    buscar: Optional[str] = None
    items: List[InformacionAuditoria]