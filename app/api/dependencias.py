from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.core.db import get_session
from app.core.seguridad import PERMISOS_ROLES, Permisos, RoleUser, decoder_token
from app.models.usuario import RoleEnum, Usuario
from app.repositories.usuario_repository import UsuarioRepositorio

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_db() -> Session:
    return next(get_session())

DBSession = Annotated[Session, Depends(get_db)]

def get_usuario_actual(token: Annotated[str, Depends(oauth2_scheme)], db: DBSession) -> Usuario:
    exepcion_credencial = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = decoder_token(token)
        id_usuario = int(payload.get("sub"))
    except:
        raise exepcion_credencial
    
    repo = UsuarioRepositorio(db)
    usuario = repo.get_usuario_by_id(id_usuario)
    
    if not usuario:
        raise exepcion_credencial
    return usuario

UsuarioActual = Annotated[Usuario, Depends(get_usuario_actual)]

class VerificarRol:
    def __init__(self, roles_permitidos: list[RoleUser]):
        self.roles_permitidos = roles_permitidos
        
    def __call__(self, usuario_actual: UsuarioActual):
        if usuario_actual.rol not in self.roles_permitidos:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        return usuario_actual
    
class VerificarPermisos:
    def __init__(self, permisos_necesarios: list[Permisos]):
        self.permisos_necesarios = permisos_necesarios
        
    def __call__(self, usuario_actual: UsuarioActual):
        usuario_permitido = PERMISOS_ROLES.get(usuario_actual.rol, set())
        if not all(perm in usuario_permitido for perm in self.permisos_necesarios):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
        return usuario_actual
    
requiere_admin = VerificarRol([RoleUser.ADMIN, RoleUser.SUPERUSER])
requiere_superuser = VerificarRol([RoleUser.SUPERUSER])
puede_gestionar_ticket = VerificarPermisos([Permisos.TICKET_READ, Permisos.TICKET_WRITE])