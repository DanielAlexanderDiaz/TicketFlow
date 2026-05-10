from fastapi import APIRouter
from pydantic import EmailStr
from app.api.dependencias import DBSession, UsuarioActual
from app.models.usuario import ActualizarUsuario, InfoUsuario
from app.services.usuario_services import UsuarioService


router = APIRouter(prefix="/usuario", tags=["usuario"])

@router.patch("/{email}", response_model=InfoUsuario)
def actualizar_usuario(email: EmailStr, payload: ActualizarUsuario, db: DBSession, usuario: UsuarioActual):
    return UsuarioService(db).actualizar_usuario(email, payload)