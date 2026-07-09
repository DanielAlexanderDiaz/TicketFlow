from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session
from app.core.db import get_session
from app.core.seguridad import PERMISOS_POR_ROL, Permiso, RolUsuario, decodificar_token
from app.models.usuario import Usuario
from app.repositories.token_blacklist_repository import TokenBlackListRepository
from app.repositories.usuario_repository import UsuarioRepositorio

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_db() -> Session:
    return Depends(get_session())

DBSession = Annotated[Session, Depends(get_db)]

def get_usuario_actual(token: Annotated[str, Depends(oauth2_scheme)], db: DBSession) -> Usuario:
    excepcion_credencial = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = decodificar_token(token)
        id_usuario = int(payload.get("sub"))
        jti = payload.get("jti")
        
        if id_usuario is None:
            raise ValueError("Token inválido: falta sub")
        
        if jti is None:
            raise ValueError("Token inválido: falta jti")
    except (jwt.PyJWTError, ValueError, TypeError, Exception) as e:
        raise excepcion_credencial
    
    black_list_repo = TokenBlackListRepository(db)
    if black_list_repo.esta_en_blacklist(jti):
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
        if usuario_actual.permiso:
            permiso_valido = PERMISOS_POR_ROL.get(usuario_actual.rol, set()) | {Permiso(p) for p in usuario_actual.permiso}
        
        if not all(perm in permiso_valido for perm in self.permisos_necesarios):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No se tienen permisos suficientes")
        return usuario_actual
    
    
# RBAC - Verificar el rol
requiere_admin = VerificarRol([RolUsuario.ADMIN, RolUsuario.SUPERADMIN])
requiere_superadmin = VerificarRol([RolUsuario.SUPERADMIN])

# RBAC - Verificar los permisos
ticket_crear = VerificarPermisos([Permiso.TICKET_PUEDE_CREAR])
ticket_actualizar = VerificarPermisos([Permiso.TICKET_PUEDE_ACTUALIZAR])
ticket_eliminar = VerificarPermisos([Permiso.TICKET_PUEDE_ELIMINAR])
ticket_compartir = VerificarPermisos([Permiso.TICKET_PUEDE_COMPARTIR])
ticket_descompartir = VerificarPermisos([Permiso.TICKET_PUEDE_DESCOMPARTIR])
ticket_asignar = VerificarPermisos([Permiso.TICKET_PUEDE_ASIGNAR])
ticket_desasignar = VerificarPermisos([Permiso.TICKET_PUEDE_DESASIGNAR])
ticket_cambiar_estado = VerificarPermisos([Permiso.TICKET_PUEDE_CAMBIAR_ESTADO])

comentario_crear = VerificarPermisos([Permiso.COMENTARIO_PUEDE_CREAR])
comentario_actualizar = VerificarPermisos([Permiso.COMENTARIO_PUEDE_ACTUALIZAR])
comentario_eliminar = VerificarPermisos([Permiso.COMENTARIO_PUEDE_ELIMINAR])

puede_gestionar_usuarios = VerificarPermisos([Permiso.USUARIO_PUEDE_ELIMINAR, 
                                              Permiso.USUARIO_PUEDE_ACTUALIZAR_ROL, 
                                              Permiso.USUARIO_PUEDE_ACTUALIZAR_PERMISOS])

