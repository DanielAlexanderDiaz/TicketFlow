from fastapi import APIRouter
from pydantic import EmailStr
from app.api.dependencias import DBSession, UsuarioActual
from app.models.usuario import ActualizarUsuario, InfoUsuario
from app.services.usuario_services import UsuarioService


router = APIRouter(prefix="/usuario", tags=["usuario"])

@router.get("/listar", response_model=list[InfoUsuario])
def listar_usuarios(db: DBSession):
    return UsuarioService(db).listar_usuarios()

@router.get("/informacion_usuario", response_model=InfoUsuario)
def info_usuario(db: DBSession, usuario: UsuarioActual):
    return UsuarioService(db).informacion_usuario(usuario.id)

@router.get("/informacion_usuario_id", response_model=InfoUsuario)
def info_usuario_id(id_usuario: int, db: DBSession, usuario: UsuarioActual):
    return UsuarioService(db).informacio_usuario_id(id_usuario)

@router.patch("/{id_usuario}", response_model=InfoUsuario)
def actualizar_usuario(payload: ActualizarUsuario, db: DBSession, usuario: UsuarioActual):
    return UsuarioService(db).actualizar_usuario_id(usuario.id, payload)

@router.patch("/update/{id_usuario}", response_model=InfoUsuario)
def actualizar_usuarios(id_usuario: int, payload: ActualizarUsuario, db: DBSession, usuario: UsuarioActual):
    return UsuarioService(db).actualizar_usuario_id(id_usuario, payload)