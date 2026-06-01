import datetime
import uuid
import jwt
from pwdlib import PasswordHash
from app.core.config import configuracion
from enum import StrEnum

pwd_context = PasswordHash.recommended()
 
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
 
def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)
 
def crear_token(data: dict, tiempo_expiracion: int | None = None) -> str:
    payload = data.copy()
    ahora = datetime.datetime.now(datetime.timezone.utc)
    expiracion = ahora + datetime.timedelta(
        minutes=tiempo_expiracion or configuracion.JWT_TIEMPO_EXPIRACION
    )
    payload.update({
        "exp": expiracion,
        "iat": ahora,
        "jti": str(uuid.uuid4()),
    })
    return jwt.encode(payload, configuracion.JWT_SECRET_KEY, algorithm=configuracion.JWT_ALGORITMO)
 
def decodificar_token(token: str) -> dict:
    return jwt.decode(
        token,
        configuracion.JWT_SECRET_KEY,
        algorithms=[configuracion.JWT_ALGORITMO],
    )

class RolUsuario(StrEnum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    
class Permiso(StrEnum):
    # Usuarios
    PUEDE_ELIMINAR_USUARIO        = "puede_eliminar_usuario"
    PUEDE_ACTUALIZAR_ROL          = "puede_actualizar_rol"
    PUEDE_ACTUALIZAR_PERMISOS     = "puede_actualizar_permisos"
 
    # Tickets
    PUEDE_CREAR_TICKET            = "puede_crear_ticket"
    PUEDE_ACTUALIZAR_TICKET       = "puede_actualizar_ticket"
    PUEDE_ELIMINAR_TICKET         = "puede_eliminar_ticket"
    PUEDE_COMPARTIR_TICKET        = "puede_compartir_ticket"
    PUEDE_DESCOMPARTIR_TICKET     = "puede_descompartir_ticket"
    PUEDE_ASIGNAR_TICKET          = "puede_asignar_ticket"
    PUEDE_CAMBIAR_ESTADO_TICKET   = "puede_cambiar_estado_ticket"
 
    # Comentarios
    PUEDE_CREAR_COMENTARIO        = "puede_crear_comentario"
    PUEDE_ACTUALIZAR_COMENTARIO   = "puede_actualizar_comentario"
    PUEDE_ELIMINAR_COMENTARIO     = "puede_eliminar_comentario"
 
PERMISOS_POR_ROL: dict[RolUsuario, set[Permiso]] = {
    RolUsuario.USER: {
        Permiso.PUEDE_CREAR_TICKET,
        Permiso.PUEDE_ACTUALIZAR_TICKET,
        Permiso.PUEDE_COMPARTIR_TICKET,
        Permiso.PUEDE_DESCOMPARTIR_TICKET,
        Permiso.PUEDE_CAMBIAR_ESTADO_TICKET,
        Permiso.PUEDE_CREAR_COMENTARIO,
        Permiso.PUEDE_ACTUALIZAR_COMENTARIO,
        Permiso.PUEDE_ELIMINAR_COMENTARIO,
    },
    RolUsuario.ADMIN: set(),  # Sin permisos por defecto (RF regla general de autorización)
    RolUsuario.SUPERADMIN: {p for p in Permiso},
}