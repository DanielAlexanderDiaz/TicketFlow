from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from app.api.dependencias import DBSession, UsuarioActual, requiere_superuser
from app.models import Usuario
from app.schemas.usuario import ActualizarPermisos, ActualizarRol, ActualizarUsuario, InformacionUsuario, UsuarioActivo
from app.services.usuario_services import UsuarioService

router = APIRouter(prefix="/usuario", tags=["usuario"])

# Actualizar nombre de usuario
@router.patch("/nombre/{id_usuario}", response_model=InformacionUsuario)
def actualizar_usuario(payload: ActualizarUsuario, db: DBSession, usuario: UsuarioActual):
    return UsuarioService(db).actualizar_usuario(usuario.id, payload)

# Actualizar foto de usuario
@router.patch("/foto/{id_usuario}", response_model=InformacionUsuario)
def actualizar_foto(db: DBSession, usuario: UsuarioActual, img: Optional[UploadFile] = File(None)):
    return UsuarioService(db).actualizar_imagen(usuario.id, img)

# Eliminar usuario
@router.delete("/eliminar/{id_usuario}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(db: DBSession, id_usuario: int, usuario: UsuarioActual, _ : Usuario = Depends(requiere_superuser)):
    if id_usuario == usuario.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No puedes eliminar tu propio usuario')
    UsuarioService(db).eliminar_usuario(id_usuario)
    return None

# Actualizar rol
@router.patch("/rol/{id_usuario}", response_model=InformacionUsuario)
def actualizar_rol(db: DBSession, payload: ActualizarRol, id_usuario: int, usuario: UsuarioActual, _ : Usuario = Depends(requiere_superuser)):
    return UsuarioService(db).actualizar_rol(id_usuario, payload)

# Actualizar permisos
@router.patch("/permisos/{id_usuario}", response_model=InformacionUsuario)
def actualizar_permisos(db: DBSession, payload: ActualizarPermisos, id_usuario: int, usuario: UsuarioActual, _ : Usuario = Depends(requiere_superuser)):
    return UsuarioService(db).actualizar_permisos(id_usuario, payload)

# Activar o desactivar usuario
@router.patch("/activo/{id_usuario}", response_model=InformacionUsuario)
def usuario_activo(db: DBSession, payload: UsuarioActivo, id_usuario: int, usuario: UsuarioActual, _ : Usuario = Depends(requiere_superuser)):
    return UsuarioService(db).usuario_activo(id_usuario, payload)