from datetime import date
from typing import Literal, Optional
from fastapi import APIRouter, Query
from app.api.dependencias import DBSession, UsuarioActual
from app.schemas.auditoria import FiltroAuditoria, PaginacionAuditoria
from app.services.auditoria_services import AuditoriaService

router = APIRouter(prefix="/auditoria", tags=["auditoria"])

@router.get('/auditoria', response_model=PaginacionAuditoria)
def lista_auditoria(
    db: DBSession, _id_usuario: UsuarioActual,
    entidad: Optional[str] = Query(default=None, description="Búsqueda parcial por entidad"),
    id_entidad: Optional[int] = Query(default=None, description="Filtrar por id entidad"),
    id_usuario: Optional[int] = Query(default=None, description="Filtrar por id usuario"),
    campo_cambiado: Optional[str] = Query(default=None, description="Búsqueda parcial por título"),
    accion: Optional[str] = Query(default=None, description="Búsqueda parcial por título"),
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    orden: Literal["id", "id_entidad", "id_usuario"] = Query(default="id"),
    direccion: Literal["asc", "desc"] = Query(default="asc"),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=10, ge=1, le=50),
):
    filtros = FiltroAuditoria(
        entidad=entidad,
        id_entidad=id_entidad,
        id_usuario=id_usuario,
        campo_cambiado=campo_cambiado,
        accion=accion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        orden=orden,
        direccion=direccion,
    )
    servicio = AuditoriaService(db).listado_auditoria(_id_usuario.id, filtros, pagina, por_pagina)
    return servicio