from fastapi import APIRouter, status
from app.api.dependencias import DBSession, UsuarioActual
from app.schemas.comentario import ActualizarComentario, CrearComentario, InfoComentario
from app.services.comentario_services import ComentarioService


router = APIRouter(prefix="/comentario", tags=["comentario"])

@router.get("/", response_model=InfoComentario)
def info_comentario(id_comentario: int, db: DBSession, usuario: UsuarioActual):
    return ComentarioService(db).comentario_by_id(id_comentario)

@router.get("/{id_ticket}", response_model=list[InfoComentario])
def info_comentarios(id_ticket: int, db: DBSession, usuario: UsuarioActual):
    return ComentarioService(db).comentario_by_ticket(id_ticket)

@router.get("/usuario/{id_usuario}", response_model=list[InfoComentario])
def info_comentarios(db: DBSession, usuario: UsuarioActual):
    return ComentarioService(db).comentario_by_usuario(usuario.id)

@router.post("/{id_ticket}", response_model=InfoComentario, status_code=status.HTTP_201_CREATED)
def crear_comentario(id_ticket: int, payload: CrearComentario, db: DBSession, usuario: UsuarioActual):
    return ComentarioService(db).crear_comentario(id_ticket, usuario.id, payload)

@router.patch("/{id_comentario}", response_model=InfoComentario)
def actualizar_comentario(id_comentario: int, payload: ActualizarComentario, db: DBSession, usuario: UsuarioActual):
    return ComentarioService(db).actualizar_comentario(id_comentario, usuario.id, payload)