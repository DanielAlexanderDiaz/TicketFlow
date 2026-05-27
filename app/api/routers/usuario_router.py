from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.api.dependencias import DBSession, UsuarioActual, requiere_admin
from app.schemas.usuario import ActualizarEstado, ActualizarPermisos, ActualizarRol, ActualizarUsuario, InfoUsuario
from app.services.usuario_services import UsuarioService

router = APIRouter(prefix="/usuario", tags=["usuario"])

@router.get("/listar", response_model=list[InfoUsuario], dependencies=[Depends(requiere_admin)])
def listar_todos_usuarios(db: DBSession):
    return UsuarioService(db).listar_usuarios()

@router.get("/informacion_usuario", response_model=InfoUsuario)
def informacion_usuario(db: DBSession, usuario: UsuarioActual):
    return UsuarioService(db).informacion_usuario(usuario.id)

@router.get("/informacion_usuario_id", response_model=InfoUsuario, dependencies=[Depends(requiere_admin)])
def info_usuario_id(id_usuario: int, db: DBSession):
    return UsuarioService(db).informacio_usuario_id(id_usuario)

@router.patch("/{id_usuario}", response_model=InfoUsuario)
def actualizar_usuario(payload: ActualizarUsuario, db: DBSession, usuario: UsuarioActual):
    return UsuarioService(db).actualizar_usuario_id(usuario.id, payload)

@router.patch("/update/{id_usuario}", response_model=InfoUsuario)
def actualizar_usuarios(db: DBSession, id_usuario: int, img: Optional[UploadFile] = File(None), nombre_usuario: Optional[str] = Form(None)):
    
    payload = ActualizarUsuario(
        nombre_usuario = nombre_usuario ,
        imagen_url = img
    )
    
    return UsuarioService(db).actualizar_usuario_id(id_usuario, payload)

@router.patch("/{id_usuario}/rol", response_model=InfoUsuario, dependencies=[Depends(requiere_admin)])
def actualizar_rol_usuario(id_usuario: int, payload: ActualizarRol, db: DBSession):
    return UsuarioService(db).actualizar_rol(id_usuario, payload)

@router.patch("/{id_usuario}/estado", response_model=InfoUsuario, dependencies=[Depends(requiere_admin)])
def actualizar_estado_usuario(id_usuario: int, payload: ActualizarEstado, db: DBSession):
    return UsuarioService(db).actualizar_estado(id_usuario, payload) 

@router.patch("/{id_usuario}/permisos", response_model=InfoUsuario, dependencies=[Depends(requiere_admin)])
def actualizar_permisos(id_usuario: int, payload: ActualizarPermisos, db: DBSession):
    return UsuarioService(db).asignar_permisos(id_usuario, payload)