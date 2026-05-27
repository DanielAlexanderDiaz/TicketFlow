from datetime import datetime
from email.mime import image
from fastapi import HTTPException, Query, UploadFile, status
from sqlmodel import Session
from app.models.auditoria import Auditoria
from app.repositories.auditoria_repository import AuditoriaRepositorio
from app.schemas.usuario import ActualizarEstado, ActualizarPermisos, ActualizarRol, ActualizarUsuario, InfoUsuario
from app.repositories.usuario_repository import UsuarioRepositorio
from app.utils.uploads_file import save_uploaded_img

class UsuarioService:
    def __init__(self, db: Session):
        self.db = db
        self.usuario_repo = UsuarioRepositorio(db)
        self.auditoria_repo = AuditoriaRepositorio(db)
        
    def listar_usuarios(self) -> list[InfoUsuario]:
        lista = self.usuario_repo.listar_usuarios()
        if not lista:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No se encontraron usuarios')
        return [InfoUsuario.model_validate(l) for l in lista]
        
    def informacion_usuario(self, id_usuario: int):
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        return InfoUsuario.model_validate(usuario)
    
    def informacio_usuario_id(self, id_usuario: int):
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        return InfoUsuario.model_validate(usuario)
    
    def actualizar_usuario_id(self, id_usuario: int, payload: ActualizarUsuario) -> InfoUsuario:
        # valida
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        if payload.imagen_url:
            img_data = save_uploaded_img(payload.imagen_url)
            usuario.imagen_url = img_data["url"]
        
        
        datos = payload.model_dump(exclude_unset=True, exclude_none=True, exclude={"imagen_url"})
        if not datos:
            return InfoUsuario.model_validate(usuario)
        
        # obtener valores anteriores
        for campo, nuevo_valor in datos.items():
            valor_anterior = getattr(usuario, campo, None)
            setattr(usuario, campo, nuevo_valor)
            
            if str(valor_anterior) != str(nuevo_valor):
                self.auditoria_repo.crear_audtoria(Auditoria(
                    entidad = "usuario",
                    id_entidad = id_usuario, 
                    id_usuario = id_usuario,
                    id_usuario_compartido = None,
                    campo_cambiado=campo,
                    fecha_cambio=datetime.now(),
                    valor_anterior=str(valor_anterior),
                    valor_nuevo=str(nuevo_valor),
                    accion="actualizado"
                    ))
            
        usuario_actualizado = self.usuario_repo.actualizar_usuario(usuario)
        
        return InfoUsuario.model_validate(usuario_actualizado)
    
    def actualizar_rol(self, id_usuario: int, payload: ActualizarRol) -> InfoUsuario:
        # valida
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)    
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
       
        datos = payload.model_dump(exclude_unset=True)
        if not datos:
            return InfoUsuario.model_validate(usuario)
        
        # obtener valores anteriores
        for campo, nuevo_valor in datos.items():
            valor_anterior = getattr(usuario, campo, None)
            setattr(usuario, campo, nuevo_valor)
            
        if str(valor_anterior) != str(nuevo_valor):
            self.auditoria_repo.crear_audtoria(Auditoria(
                entidad = "usuario",
                id_entidad = id_usuario, 
                id_usuario = id_usuario,
                id_usuario_compartido = None,
                campo_cambiado=campo,
                fecha_cambio=datetime.now(),
                valor_anterior=str(valor_anterior),
                valor_nuevo=str(nuevo_valor),
                accion="actualizado"
                ))

        usuario_actualizado = self.usuario_repo.actualizar_usuario(usuario)
        
        return InfoUsuario.model_validate(usuario_actualizado)
    
    def actualizar_estado(self, id_usuario: int, payload: ActualizarEstado) -> InfoUsuario:
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        valor_anterior = usuario.activo
        nuevo_valor = payload.activo
        usuario.activo = payload.activo
        
        if str(valor_anterior) != str(nuevo_valor):
            self.auditoria_repo.crear_audtoria(Auditoria(
                entidad = "usuario",
                id_entidad = id_usuario, 
                id_usuario = id_usuario,
                id_usuario_compartido = None,
                campo_cambiado="activo",
                fecha_cambio=datetime.now(),
                valor_anterior=str(valor_anterior),
                valor_nuevo=str(nuevo_valor),
                accion="actualizado"
                ))
        
        self.usuario_repo.actualizar_usuario(usuario)
        
        return InfoUsuario.model_validate(usuario)
    
    def asignar_permisos(self, id_usuario: int, payload: ActualizarPermisos) -> InfoUsuario:
        usuario = self.usuario_repo.get_usuario_by_id(id_usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Usuario no encontrado')
        
        usuario.permisos = payload.permisos
        self.usuario_repo.actualizar_usuario(usuario)
        
        return InfoUsuario.model_validate(usuario)