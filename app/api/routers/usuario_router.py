from typing import Literal, Optional
from click import pass_obj
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from app.api.dependencias import DBSession, UsuarioActual, requiere_superadmin
from app.models import Usuario
from app.schemas.usuario import ActualizarPermisos, ActualizarRol, ActualizarUsuario, FiltrosUsuario, InformacionUsuario, PaginacionUsuario, UsuarioActivo
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
def eliminar_usuario(db: DBSession, id_usuario: int, usuario: UsuarioActual, _ : Usuario = Depends(requiere_superadmin)):
    if id_usuario == usuario.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No puedes eliminar tu propio usuario')
    UsuarioService(db).eliminar_usuario(id_usuario)
    return None

# Actualizar rol
@router.patch("/rol/{id_usuario}", response_model=InformacionUsuario)
def actualizar_rol(db: DBSession, payload: ActualizarRol, id_usuario: int, usuario: UsuarioActual, _ : Usuario = Depends(requiere_superadmin)):
    return UsuarioService(db).actualizar_rol(id_usuario, payload)

# Actualizar permisos
@router.patch("/permisos/{id_usuario}", response_model=InformacionUsuario)
def actualizar_permisos(db: DBSession, payload: ActualizarPermisos, id_usuario: int, usuario: UsuarioActual, _ : Usuario = Depends(requiere_superadmin)):
    return UsuarioService(db).actualizar_permisos(id_usuario, payload)

# Activar o desactivar usuario
@router.patch("/activo/{id_usuario}", response_model=InformacionUsuario)
def usuario_activo(db: DBSession, payload: UsuarioActivo, id_usuario: int, usuario: UsuarioActual, _ : Usuario = Depends(requiere_superadmin)):
    return UsuarioService(db).usuario_activo(id_usuario, payload)

@router.get('/usuarios', response_model=PaginacionUsuario)
def lista_usuarios(
    db: DBSession, id_usuario: UsuarioActual,
    buscar_email: Optional[str] = Query(default=None, description="Búsqueda parcial por email"),
    buscar_nombre: Optional[str] = Query(default=None, description="Búsqueda parcial por nombre"),
    rol: Optional[int] = Query(default=None, description="Filtrar por rol"),
    activo: Optional[bool] = Query(default=None, description="activado?"),
    orden: Literal["id", "email", "nombre_usuario", "activo"] = Query(default="id"),
    direccion: Literal["asc", "desc"] = Query(default="asc"),
    pagina: int = Query(default=1, ge=1),
    por_pagina: int = Query(default=10, ge=1, le=50),
):
    
    filtros = FiltrosUsuario(
        buscar_email=buscar_email,
        buscar_nombre=buscar_nombre,
        rol=rol,
        activo=activo,
        orden=orden,
        direccion=direccion,
    )
    servicio = UsuarioService(db).listado_usuario(id_usuario.id, filtros, pagina, por_pagina)
    return servicio