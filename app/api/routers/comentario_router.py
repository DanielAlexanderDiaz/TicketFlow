from datetime import datetime
from typing import Literal, Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencias import DBSession, UsuarioActual, comentario_crear, comentario_actualizar, comentario_eliminar
from app.schemas.comentario import CrearComentario, ActualizarComentario, EliminarComentario, FiltroComentario, InformacionComentario, PaginacionComentario
from app.services.comentario_services import ComentarioService


router = APIRouter(prefix="/comentario", tags=["comentario"])

@router.post("/", response_model=InformacionComentario, status_code=status.HTTP_201_CREATED, dependencies=[Depends(comentario_crear)])
def crear_comentario(db: DBSession, id_ticket: int, id_usuario: UsuarioActual, payload: CrearComentario) -> InformacionComentario:
    servicio = ComentarioService(db).crear_comentario(id_ticket, id_usuario.id, payload)
    return servicio

@router.patch("/actualizar/{id_comentario}", response_model=InformacionComentario, dependencies=[Depends(comentario_actualizar)])
def actualizar_comentario(db: DBSession, id_ticket: int, id_comentario: int, id_usuario: UsuarioActual, payload: ActualizarComentario) -> InformacionComentario:
    servicio = ComentarioService(db).actualizar_comentario(id_ticket, id_comentario, id_usuario.id, payload)
    return servicio

@router.delete("/eliminar", dependencies=[Depends(comentario_eliminar)])
def eliminar_comentario(db: DBSession, id_ticket: int, id_usuario: UsuarioActual, payload: EliminarComentario) -> None:
    ComentarioService(db).eliminar_comentario(id_ticket, id_usuario.id, payload)
    return

@router.get('/comentarios', response_model=PaginacionComentario)
def lista_comentarios(
    db: DBSession, id_usuario: UsuarioActual,
    id_ticket: Optional[int] = Query(default=None, description="Filtrar por N° de ticket"),
    _id_usuario: Optional[int] = Query(default=None, description="Filtrar por id_usuario"),
    comentario: Optional[str] = Query(default=None, description="Búsqueda parcial por comentario"),
    fecha_creacion: Optional[datetime] = Query(default=None),
    fecha_actualizacion: Optional[datetime] = Query(default=None),
    orden: Literal["id", "id_ticket","comentario", "fecha_creacion", "fecha_actualizacion"] = Query(default="id"),
    direccion: Literal["asc", "desc"] = "asc",
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=10, ge=1, le=50),
):
    filtros = FiltroComentario(
        id_ticket=id_ticket,
        id_usuario=_id_usuario,
        comentario=comentario,
        fecha_creacion=fecha_creacion,
        fecha_actualizacion=fecha_actualizacion,
        orden=orden,
        direccion=direccion,
    )
    servicio = ComentarioService(db).listado_comentario(id_usuario.id, filtros, pagina, por_pagina)
    return servicio