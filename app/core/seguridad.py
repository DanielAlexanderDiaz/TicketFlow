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
    
def decodificar_token_sin_verificar_exp(token: str) -> dict:
    return jwt.decode(
        token,
        configuracion.JWT_SECRET_KEY,
        algorithms=[configuracion.JWT_ALGORITMO],
        options={"verify_exp": False}
    )

class RolUsuario(StrEnum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    
class Permiso(StrEnum):
    # Usuarios
    USUARIO_PUEDE_ELIMINAR = "puede_eliminar_usuario"
    USUARIO_PUEDE_ACTUALIZAR_ROL = "puede_actualizar_rol"
    USUARIO_PUEDE_ACTUALIZAR_PERMISOS = "puede_actualizar_permisos"
 
    # Tickets
    TICKET_PUEDE_CREAR = "puede_crear_ticket"
    TICKET_PUEDE_ACTUALIZAR = "puede_actualizar_ticket"
    TICKET_PUEDE_ELIMINAR = "puede_eliminar_ticket"
    TICKET_PUEDE_COMPARTIR = "puede_compartir_ticket"
    TICKET_PUEDE_DESCOMPARTIR = "puede_descompartir_ticket"
    TICKET_PUEDE_ASIGNAR = "puede_asignar_ticket"
    TICKET_PUEDE_CAMBIAR_ESTADO = "puede_cambiar_estado_ticket"
 
    # Comentarios
    COMENTARIO_PUEDE_CREAR = "puede_crear_comentario"
    COMENTARIO_PUEDE_ACTUALIZAR = "puede_actualizar_comentario"
    COMENTARIO_PUEDE_ELIMINAR = "puede_eliminar_comentario"
 
PERMISOS_POR_ROL: dict[RolUsuario, set[Permiso]] = {
    RolUsuario.USER: {
        Permiso.TICKET_PUEDE_CREAR,
        Permiso.TICKET_PUEDE_ACTUALIZAR,
        Permiso.TICKET_PUEDE_COMPARTIR,
        Permiso.TICKET_PUEDE_DESCOMPARTIR,
        Permiso.TICKET_PUEDE_CAMBIAR_ESTADO,
        Permiso.COMENTARIO_PUEDE_CREAR,
        Permiso.COMENTARIO_PUEDE_ACTUALIZAR,
        Permiso.COMENTARIO_PUEDE_ELIMINAR,
    },
    RolUsuario.ADMIN: set(),  # Sin permisos por defecto (RF regla general de autorización)
    RolUsuario.SUPERADMIN: {p for p in Permiso},
}