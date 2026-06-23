from fastapi import APIRouter, Depends, status
from app.api.dependencias import DBSession, UsuarioActual, comentario_crear, comentario_actualizar, comentario_eliminar
from app.schemas.comentario import CrearComentario, ActualizarComentario, EliminarComentario, InformacionComentario
from app.services.comentario_services import ComentarioService


router = APIRouter(prefix="/comentario", tags=["comentario"])

@router.post("/", response_model=InformacionComentario, status_code=status.HTTP_201_CREATED, dependencies=[Depends(comentario_crear)])
def crear_comentario(db: DBSession, id_ticket: int, id_usuario: UsuarioActual, payload: CrearComentario) -> InformacionComentario:
    servicio = ComentarioService(db).crear_comentario(id_ticket, id_usuario.id, payload)
    return servicio

@router.patch("/{id_comentario}", response_model=InformacionComentario, dependencies=[Depends(comentario_actualizar)])
def actualizar_comentario(db: DBSession, id_ticket: int, id_comentario: int, id_usuario: UsuarioActual, payload: ActualizarComentario) -> InformacionComentario:
    servicio = ComentarioService(db).actualizar_comentario(id_ticket, id_comentario, id_usuario.id, payload)
    return servicio

@router.delete("/{id_comentario}", dependencies=[Depends(comentario_eliminar)])
def eliminar_comentario(db: DBSession, id_ticket: int, id_usuario: UsuarioActual, payload: EliminarComentario) -> None:
    ComentarioService(db).eliminar_comentario(id_ticket, id_usuario.id, payload)
    return