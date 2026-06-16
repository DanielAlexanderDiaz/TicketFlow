from fastapi import APIRouter, status
from app.api.dependencias import DBSession, UsuarioActual
from app.schemas.comentario import ActualizarComentario, CrearComentario, InformacionComentario
from app.services.comentario_services import ComentarioService


router = APIRouter(prefix="/comentario", tags=["comentario"])
