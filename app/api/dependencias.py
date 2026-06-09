from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session
from app.core.db import get_session
from app.core.seguridad import PERMISOS_POR_ROL, Permiso, RolUsuario, decodificar_token
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepositorio

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_db() -> Session:
    return next(get_session())

DBSession = Annotated[Session, Depends(get_db)]

def get_usuario_actual(token: Annotated[str, Depends(oauth2_scheme)], db: DBSession) -> Usuario:
    excepcion_credencial = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = decodificar_token(token)
        id_usuario = int(payload.get("sub"))
        if id_usuario is None:
            raise ValueError("Token inválido: falta sub")
    except (jwt.PyJWTError, ValueError, TypeError, Exception) as e:
        raise excepcion_credencial
    
    repo = UsuarioRepositorio(db)
    usuario = repo.get_usuario_by_id(id_usuario)
    
    if not usuario:
        raise excepcion_credencial
    return usuario

UsuarioActual = Annotated[Usuario, Depends(get_usuario_actual)]

class VerificarRol:
    def __init__(self, roles_permitidos: list[RolUsuario]):
        self.roles_permitidos = roles_permitidos
        
    def __call__(self, usuario_actual: UsuarioActual):
        if usuario_actual.rol not in self.roles_permitidos:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No se tiene rol permitido")
        return usuario_actual
    
class VerificarPermisos:
    def __init__(self, permisos_necesarios: list[Permiso]):
        self.permisos_necesarios = permisos_necesarios
        
    def __call__(self, usuario_actual: UsuarioActual):
        if usuario_actual.permiso_extra:
            permiso_valido = {Permiso(p) for p in usuario_actual.permiso_extra}
        else:    
            permiso_valido = PERMISOS_POR_ROL.get(usuario_actual.rol, set())
        
        if not all(perm in permiso_valido for perm in self.permisos_necesarios):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No se tienen permisos suficientes")
        return usuario_actual
    
    
requiere_admin = VerificarRol([RolUsuario.ADMIN, RolUsuario.SUPERADMIN])
requiere_superuser = VerificarRol([RolUsuario.SUPERADMIN])
puede_gestionar_ticket = VerificarPermisos([Permiso.TICKET_PUEDE_CREAR, 
                                            Permiso.TICKET_PUEDE_ACTUALIZAR, 
                                            Permiso.TICKET_PUEDE_ELIMINAR, 
                                            Permiso.TICKET_PUEDE_COMPARTIR, 
                                            Permiso.TICKET_PUEDE_DESCOMPARTIR, 
                                            Permiso.TICKET_PUEDE_ASIGNAR, 
                                            Permiso.TICKET_PUEDE_CAMBIAR_ESTADO])