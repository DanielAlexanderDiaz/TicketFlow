from fastapi import APIRouter

from app.api.dependencias import DBSession, UsuarioActual
from app.models.comentario import ActualizarComentario, InfoComentario
from app.services.comentario_services import ComentarioService


router = APIRouter(prefix="/comentario", tags=["comentario"])

@router.get("/", response_model=InfoComentario)
def info_comentario(id_comentario: int, db: DBSession, usuario: UsuarioActual):
    return ComentarioService(db).comentario_by_ticket(id_comentario)