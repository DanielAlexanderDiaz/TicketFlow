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

@router.patch("/{email}", response_model=InfoUsuario)
def actualizar_usuario(email: EmailStr, payload: ActualizarUsuario, db: DBSession, usuario: UsuarioActual):
    return UsuarioService(db).actualizar_usuario(email, payload)